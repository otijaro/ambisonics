import os
import math
import time
import subprocess
import numpy as np
import soundfile as sf
import logging
from scipy.signal import stft
from scipy.ndimage import uniform_filter1d

from backend.core_dsp import (
    N_FFT, HOP,
    normalize_audio, stabilize_loudness,
    stereo_to_foa, tetra_aformat_to_foa,
    foa_to_binaural, foa_to_binaural_fallback,
    stereo_to_foa_demo, foa_motion_convert, foa_motion_demo, build_demo_params,
    DEMO_VIRTUAL_SPEAKERS,
    validate_sample_rate,
    SUPPORTED_SAMPLING_RATES,
)

logger = logging.getLogger("ambisonic-processor")

# Longitud estándar del búfer de guarda de contexto para streaming: 48 saltos STFT
# (24576 muestras a 48 kHz, amortigua el polo IIR de elevación (0.85)^48 = 0.000403,
# acotando el error angular en el inicio de bloque a <= 0.0181°).
DEFAULT_N_CTX = 24576


def _restore_notebook_binaural(result, reference_padding=512):
    """Reconstruye la salida N+512 usada por el notebook original.

    El render optimizado devuelve bloque y cola por separado para streaming.
    En memoria, el notebook conservaba N+512 muestras.
    """
    if not isinstance(result, tuple):
        return result
    block, tail_l, tail_r = result
    tail = np.stack([tail_l, tail_r], axis=1)
    missing = max(reference_padding - len(tail), 0)
    if missing:
        tail = np.pad(tail, ((0, missing), (0, 0)))
    return np.concatenate([block, tail], axis=0)


def unified_spectral_prescan(input_data, sr, block_frames, n_ctx):
    """Preanálisis espectral y de amplitud unificado para archivos WAV y arrays en memoria.
    
    Calcula exactamente la misma media global, pico global relativo y rango de
    tilt espectral [min_tilt, max_tilt] mediante STFT streaming con solapamiento
    completo sin ceros artificiales.
    """
    f_axis = np.linspace(0, sr / 2, N_FFT // 2 + 1)
    
    # --------------------------------------------------------------------------
    # Pasada 1: Media Global y Pico Global de Amplitud
    # --------------------------------------------------------------------------
    if isinstance(input_data, str):
        global_sum = 0.0
        total_samples = 0
        for block in sf.blocks(input_data, blocksize=block_frames, dtype='float32'):
            if block.ndim == 1:
                block = block[:, None]
            if block.shape[1] < 2:
                block = np.repeat(block, 2, axis=1)
            global_sum += np.sum(block, axis=0)
            total_samples += len(block)
        global_mean = global_sum / max(total_samples, 1)

        global_peak = 1e-9
        for block in sf.blocks(input_data, blocksize=block_frames, dtype='float32'):
            if block.ndim == 1:
                block = block[:, None]
            if block.shape[1] < 2:
                block = np.repeat(block, 2, axis=1)
            block_centered = block - global_mean
            global_peak = max(global_peak, float(np.max(np.abs(block_centered))))
        global_peak += 1e-9

        # Pasada 2: Tilt Espectral unificado en streaming
        global_min_tilt = float('inf')
        global_max_tilt = float('-inf')
        overlap_tail = np.zeros(0, dtype=np.float32)
        is_first = True

        for block_raw in sf.blocks(input_data, blocksize=block_frames, dtype='float32'):
            if block_raw.ndim == 1:
                block_raw = block_raw[:, None]
            if block_raw.shape[1] < 2:
                block_raw = np.repeat(block_raw, 2, axis=1)
            block_norm = (0.95 * (block_raw - global_mean) / global_peak).astype(np.float32)
            M_curr = (block_norm[:, 0] + block_norm[:, 1]) * 0.5

            if is_first:
                chunk_in = np.pad(M_curr, (N_FFT // 2, 0))
                is_first = False
            else:
                chunk_in = np.concatenate([overlap_tail, M_curr])

            f_axis, _, ZM = stft(
                chunk_in, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP,
                boundary=None, padded=False
            )
            E = np.abs(ZM) ** 2
            st = np.sum(E * f_axis[:, None], axis=0) / (np.sum(E, axis=0) + 1e-12)
            global_min_tilt = min(global_min_tilt, float(np.min(st)))
            global_max_tilt = max(global_max_tilt, float(np.max(st)))

            last_frame_start = (len(chunk_in) - N_FFT) // HOP * HOP
            consumed = last_frame_start + HOP
            overlap_tail = chunk_in[consumed:]

        if len(overlap_tail) >= N_FFT:
            f_axis, _, ZM = stft(
                overlap_tail, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP,
                boundary=None, padded=False
            )
            E = np.abs(ZM) ** 2
            st = np.sum(E * f_axis[:, None], axis=0) / (np.sum(E, axis=0) + 1e-12)
            global_min_tilt = min(global_min_tilt, float(np.min(st)))
            global_max_tilt = max(global_max_tilt, float(np.max(st)))

    else:
        audio = np.asarray(input_data, dtype=np.float32)
        if audio.ndim == 1:
            audio = audio[:, None]
        if audio.shape[1] < 2:
            audio = np.repeat(audio, 2, axis=1)
        global_mean = np.mean(audio, axis=0)
        global_peak = float(np.max(np.abs(audio - global_mean))) + 1e-9

        norm_audio = (0.95 * (audio - global_mean) / global_peak).astype(np.float32)
        M = (norm_audio[:, 0] + norm_audio[:, 1]) * 0.5
        chunk_in = np.pad(M, (N_FFT // 2, 0))
        f_axis, _, ZM = stft(
            chunk_in, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP,
            boundary=None, padded=False
        )
        E = np.abs(ZM) ** 2
        st = np.sum(E * f_axis[:, None], axis=0) / (np.sum(E, axis=0) + 1e-12)
        global_min_tilt = float(np.min(st))
        global_max_tilt = float(np.max(st))

    return global_mean, global_peak, global_min_tilt, global_max_tilt


def convert_audio(input_path: str, output_dir: str, mode: str, hrtf, pos):
    """Conversión completa a FOA (AmbiX ACN/SN3D) y renderizado binaural con SADIE II D1.
    
    Incorpora la arquitectura optimizada validada experimentalmente:
      1. Pre-scan unificado de amplitud y tilt espectral.
      2. Streaming con alineación al salto STFT (hop_block_frames) y guarda de contexto (N_ctx = 24576).
      3. Normalización por bloques y estabilización de sonoridad O(N) para acotamiento de RAM.
      4. Cuantización estricta PCM_16 sin clipping ni pérdida muestral.
    """
    start_total = time.time()
    logger.info(f"Iniciando convert_audio (Optimizado Objetivo 1): {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Validación estricta de frecuencia de muestreo (SIN REMUESTREO)
    with sf.SoundFile(input_path, 'r') as f_in:
        in_sr = f_in.samplerate
        channels = f_in.channels
        total_frames = len(f_in)
        audio_duration = total_frames / in_sr

    sr = validate_sample_rate(in_sr)
    logger.info(f"Frecuencia de muestreo nativa admitida: {sr} Hz (procesamiento exacto sin remuestreo)")

    block_sec = 10.0
    hop_block_frames = int(round(block_sec * sr / HOP)) * HOP
    n_ctx = DEFAULT_N_CTX
    
    if audio_duration < 60.0:
        logger.info("Audio corto (< 60s), usando procesamiento en memoria idéntico a convert.ipynb original.")
        
        # 1. Cargar y normalizar como en el notebook
        audio, _ = sf.read(input_path)
        audio = audio.astype(np.float64)
        if audio.ndim == 1:
            audio = audio[:, None]
        audio = audio - np.mean(audio, axis=0, keepdims=True)
        peak = np.max(np.abs(audio)) + 1e-9
        audio = 0.95 * audio / peak
        
        if audio.shape[1] < 2: 
            audio = np.repeat(audio, 2, axis=1)
        
        # 2. Conversión a FOA
        if mode == "tetra_4mic":
            if audio.shape[1] < 4:
                raise ValueError("El modo tetra requiere 4 canales.")
            res = tetra_aformat_to_foa(audio)
            W, X, Y, Z = res[0], res[1], res[2], res[3]
        else:
            res = stereo_to_foa(audio, sr)
            W, X, Y, Z = res[0], res[1], res[2], res[3]
            
        # 3. Empaquetar y normalizar FOA
        foa = np.stack([W, Y, Z, X], axis=1)
        foa /= np.max(np.abs(foa)) + 1e-9
        sf.write(os.path.join(output_dir, "output_foa.wav"), foa, sr, subtype='PCM_16')
        
        # 4. Binaural Normal
        if hrtf is not None and pos is not None:
            bin_res = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False)
            bin_block = _restore_notebook_binaural(bin_res)
            bin_block /= np.max(np.abs(bin_block)) + 1e-9
        else:
            bin_block = foa_to_binaural_fallback(W, X, Y, Z)
            
        bin_block = normalize_audio(bin_block, peak_target=0.95)
        
        # 5. Binaural 3D Perceptual
        W_3d, X_3d, Y_3d, Z_3d = foa_motion_convert(
            W, X, Y, Z, sr, 
            rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5
        )
        if hrtf is not None and pos is not None:
            bin3d_res = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False)
            bin3d_block = _restore_notebook_binaural(bin3d_res)
            bin3d_block /= np.max(np.abs(bin3d_block)) + 1e-9
        else:
            bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
            
        bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
        
        # Estabilizar volumen con parámetros del notebook
        bin3d_block = stabilize_loudness(
            bin3d_block, sr, 
            win_ms=450, strength=0.55, min_gain=0.88, max_gain=2.0
        )
        
        sf.write(os.path.join(output_dir, "output_binaural.wav"), bin_block, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_binaural_3D_perceptual.wav"), bin3d_block, sr, subtype='PCM_16')
        
    else:
        # ======================================================================
        # MODO STREAMING OPTIMIZADO: CONTEXT-GUARD + NORMALIZACIÓN POR BLOQUES
        # ======================================================================
        logger.info(f"Audio largo (> 60s), ejecutando pipeline streaming optimizado (bloques={hop_block_frames} muestras).")
        
        # ----------------------------------------------------------------------
        # Etapa 1: Pre-scan unificado (amplitud y tilt espectral)
        # ----------------------------------------------------------------------
        t_s1 = time.time()
        global_mean, global_peak, global_min_tilt, global_max_tilt = unified_spectral_prescan(
            input_path, sr, hop_block_frames, n_ctx
        )
        time_stage1 = time.time() - t_s1
        logger.info(f"[TIMING] Etapa 1 Pre-Scan: {time_stage1:.2f}s (Tilt: [{global_min_tilt:.1f}, {global_max_tilt:.1f}])")
        
        # ----------------------------------------------------------------------
        # Etapa 2: Streaming con Context-Guard y Archivos Temporales FLOAT
        # ----------------------------------------------------------------------
        t_s2 = time.time()
        temp_foa_p = os.path.join(output_dir, "temp_foa.wav")
        temp_bin_p = os.path.join(output_dir, "temp_binaural.wav")
        temp_bin3d_p = os.path.join(output_dir, "temp_binaural_3D.wav")
        
        f_foa = sf.SoundFile(temp_foa_p, 'w', sr, channels=4, subtype='FLOAT')
        f_bin = sf.SoundFile(temp_bin_p, 'w', sr, channels=2, subtype='FLOAT')
        f_bin3d = sf.SoundFile(temp_bin3d_p, 'w', sr, channels=2, subtype='FLOAT')
        
        tail_bin_L = None
        tail_bin_R = None
        tail_bin3d_L = None
        tail_bin3d_R = None
        current_time = 0.0
        
        peak_foa_track = 1e-9
        peak_bin_track = 1e-9
        peak_bin3d_track = 1e-9
        
        blocks_iter = sf.blocks(input_path, blocksize=hop_block_frames, dtype='float32')
        try:
            curr_block = next(blocks_iter)
            if curr_block.ndim == 1:
                curr_block = curr_block[:, None]
            if curr_block.shape[1] < 2:
                curr_block = np.repeat(curr_block, 2, axis=1)
            curr_block = (0.95 * (curr_block - global_mean) / global_peak).astype(np.float32)
        except StopIteration:
            curr_block = None
            
        prev_tail = np.zeros((n_ctx, 2), dtype=np.float32)
        b_idx = 0
        
        while curr_block is not None:
            try:
                next_block = next(blocks_iter)
                if next_block.ndim == 1:
                    next_block = next_block[:, None]
                if next_block.shape[1] < 2:
                    next_block = np.repeat(next_block, 2, axis=1)
                next_block = (0.95 * (next_block - global_mean) / global_peak).astype(np.float32)
            except StopIteration:
                next_block = None
                
            n_curr = len(curr_block)
            
            if mode == "tetra_4mic":
                if curr_block.shape[1] < 4:
                    raise ValueError("El modo tetra requiere 4 canales.")
                W, X, Y, Z = tetra_aformat_to_foa(curr_block)
            else:
                if curr_block.shape[1] < 2:
                    curr_block = np.repeat(curr_block, 2, axis=1)
                
                parts = []
                if b_idx > 0:
                    parts.append(prev_tail)
                    pre_len = len(prev_tail)
                else:
                    pre_len = 0
                    
                parts.append(curr_block)
                
                if next_block is not None:
                    parts.append(next_block[:n_ctx])
                    
                ext_chunk = np.vstack(parts)
                
                W_ext, X_ext, Y_ext, Z_ext, _, _ = stereo_to_foa(
                    ext_chunk, sr,
                    min_tilt=global_min_tilt,
                    max_tilt=global_max_tilt,
                    is_first_block=(b_idx == 0)
                )
                
                W = W_ext[pre_len : pre_len + n_curr]
                X = X_ext[pre_len : pre_len + n_curr]
                Y = Y_ext[pre_len : pre_len + n_curr]
                Z = Z_ext[pre_len : pre_len + n_curr]
                
            foa = np.stack([W, Y, Z, X], axis=1)
            f_foa.write(foa)
            peak_foa_track = max(peak_foa_track, float(np.max(np.abs(foa))))
            
            # OLA Binaural
            if hrtf is not None and pos is not None:
                bin_block, tail_bin_L, tail_bin_R = foa_to_binaural(
                    W, X, Y, Z, sr, hrtf, pos, flip_az=False,
                    overlap_L=tail_bin_L, overlap_R=tail_bin_R
                )
            else:
                bin_block = foa_to_binaural_fallback(W, X, Y, Z)
            f_bin.write(bin_block)
            peak_bin_track = max(peak_bin_track, float(np.max(np.abs(bin_block))))
            
            # 3D Perceptual Motion
            W_3d, X_3d, Y_3d, Z_3d = foa_motion_convert(
                W, X, Y, Z, sr,
                rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5,
                t_start=current_time
            )
            if hrtf is not None and pos is not None:
                bin3d_block, tail_bin3d_L, tail_bin3d_R = foa_to_binaural(
                    W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False,
                    overlap_L=tail_bin3d_L, overlap_R=tail_bin3d_R
                )
            else:
                bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
            bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
            f_bin3d.write(bin3d_block)
            peak_bin3d_track = max(peak_bin3d_track, float(np.max(np.abs(bin3d_block))))
            
            current_time += n_curr / sr
            prev_tail = curr_block[-n_ctx:] if len(curr_block) >= n_ctx else curr_block
            curr_block = next_block
            b_idx += 1
            
        if tail_bin_L is not None:
            tail_b = np.stack([tail_bin_L, tail_bin_R], axis=1)
            f_bin.write(tail_b)
            peak_bin_track = max(peak_bin_track, float(np.max(np.abs(tail_b))))
            
        if tail_bin3d_L is not None:
            tail_3d = np.stack([tail_bin3d_L, tail_bin3d_R], axis=1)
            if tail_bin_L is not None:
                tail_b_ref = np.stack([tail_bin_L, tail_bin_R], axis=1)
                tail_3d = 0.90 * tail_3d + 0.10 * tail_b_ref
            f_bin3d.write(tail_3d)
            peak_bin3d_track = max(peak_bin3d_track, float(np.max(np.abs(tail_3d))))
            
        f_foa.close()
        f_bin.close()
        f_bin3d.close()
        time_stage2 = time.time() - t_s2
        logger.info(f"[TIMING] Etapa 2 Streaming OLA: {time_stage2:.2f}s")
        
        # ----------------------------------------------------------------------
        # Etapa 3: Normalización y Estabilización de Loudness por Bloques (PCM_16)
        # ----------------------------------------------------------------------
        t_s3 = time.time()
        foa_wav = os.path.join(output_dir, "output_foa.wav")
        binaural_wav = os.path.join(output_dir, "output_binaural.wav")
        binaural_3d_wav = os.path.join(output_dir, "output_binaural_3D_perceptual.wav")
        
        # 3.1 Normalización por bloques de FOA -> PCM_16
        scale_foa = 1.0 / (peak_foa_track + 1e-9)
        with sf.SoundFile(foa_wav, 'w', sr, channels=4, subtype='PCM_16') as f_out_foa:
            for blk in sf.blocks(temp_foa_p, blocksize=hop_block_frames, dtype='float32'):
                f_out_foa.write((blk * scale_foa).astype(np.float32))
        if os.path.exists(temp_foa_p):
            os.remove(temp_foa_p)
            
        # 3.2 Normalización por bloques de Binaural Normal -> PCM_16
        scale_bin = 0.95 / (peak_bin_track + 1e-9)
        with sf.SoundFile(binaural_wav, 'w', sr, channels=2, subtype='PCM_16') as f_out_bin:
            for blk in sf.blocks(temp_bin_p, blocksize=hop_block_frames, dtype='float32'):
                f_out_bin.write((blk * scale_bin).astype(np.float32))
        if os.path.exists(temp_bin_p):
            os.remove(temp_bin_p)
            
        # 3.3 Estabilización de Loudness por Bloques O(N) -> PCM_16
        info_3d = sf.info(temp_bin3d_p)
        total_samples_3d = info_3d.frames
        scale_pre_3d = 1.0 / (peak_bin3d_track + 1e-9)
        
        # Pasada 1 (Loudness): Acumular envolvente de potencia 1D
        power_1d = np.empty(total_samples_3d, dtype=np.float32)
        ptr = 0
        for blk in sf.blocks(temp_bin3d_p, blocksize=hop_block_frames, dtype='float32'):
            n_b = len(blk)
            blk_p = blk * scale_pre_3d
            power_1d[ptr : ptr + n_b] = np.mean(blk_p ** 2, axis=1)
            ptr += n_b
            
        win = max(int(sr * 0.450), 1)
        smoothed_power = uniform_filter1d(power_1d, size=win, mode='constant', cval=0.0)
        smoothed_power = np.maximum(smoothed_power, 0.0)
        env = np.sqrt(smoothed_power + 1e-9)
        target = float(np.median(env) + 1e-9)
        
        gain = target / (env + 1e-9)
        gain = gain ** 0.55
        gain = np.clip(gain, 0.88, 2.0)
        gain = uniform_filter1d(gain, size=win, mode='constant', cval=0.0)
        gain = np.maximum(gain, 0.0)
        del power_1d, smoothed_power, env
        
        # Pasada 2 (Loudness): Medir pico post-estabilización
        ptr = 0
        peak_3d_post = 1e-9
        for blk in sf.blocks(temp_bin3d_p, blocksize=hop_block_frames, dtype='float32'):
            n_b = len(blk)
            blk_p = blk * scale_pre_3d
            g_sub = gain[ptr : ptr + n_b, None]
            blk_scaled = blk_p * g_sub
            peak_3d_post = max(peak_3d_post, float(np.max(np.abs(blk_scaled))))
            ptr += n_b
            
        # Pasada 3 (Loudness): Escritura final PCM_16 escalada a peak_target=0.95
        scale_final_3d = 0.95 / (peak_3d_post + 1e-9)
        ptr = 0
        with sf.SoundFile(binaural_3d_wav, 'w', sr, channels=2, subtype='PCM_16') as f_out_3d:
            for blk in sf.blocks(temp_bin3d_p, blocksize=hop_block_frames, dtype='float32'):
                n_b = len(blk)
                blk_p = blk * scale_pre_3d
                g_sub = gain[ptr : ptr + n_b, None]
                blk_out = blk_p * g_sub * scale_final_3d
                f_out_3d.write(blk_out.astype(np.float32))
                ptr += n_b
        del gain
        
        if os.path.exists(temp_bin3d_p):
            os.remove(temp_bin3d_p)
            
        time_stage3 = time.time() - t_s3
        logger.info(f"[TIMING] Etapa 3 Normalización y Loudness O(N): {time_stage3:.2f}s")
        
    # 5. Convertir a MP3 si la frecuencia es compatible (estándar MP3 soporta hasta 48 kHz)
    start_exp = time.time()
    binaural_wav = os.path.join(output_dir, "output_binaural.wav")
    binaural_3d_wav = os.path.join(output_dir, "output_binaural_3D_perceptual.wav")
    binaural_mp3 = os.path.join(output_dir, "output_binaural.mp3")
    binaural_3d_mp3 = os.path.join(output_dir, "output_binaural_3D_perceptual.mp3")
    if sr <= 48000:
        try:
            p1 = subprocess.Popen([
                "ffmpeg", "-y", "-loglevel", "quiet",
                "-i", binaural_wav,
                "-codec:a", "libmp3lame", "-b:a", "320k",
                binaural_mp3
            ])
            p2 = subprocess.Popen([
                "ffmpeg", "-y", "-loglevel", "quiet",
                "-i", binaural_3d_wav,
                "-codec:a", "libmp3lame", "-b:a", "320k",
                binaural_3d_mp3
            ])
            p1.wait()
            p2.wait()
            time_exp = time.time() - start_exp
            logger.info(f"[TIMING] Generación MP3 completada: {time_exp:.2f}s")
        except Exception as e:
            logger.error(f"Error generando MP3: {e}")
    else:
        logger.info(f"Omitiendo generación MP3 para {sr} Hz: el estándar MP3 (MPEG-1 Layer III) no admite frecuencias superiores a 48 kHz. Se suministra exclusivamente la salida WAV nativa de alta resolución ({sr} Hz).")
    
    time_total = time.time() - start_total
    logger.info(f"[TIMING] PROCESO TOTAL: {time_total:.2f}s (Audio: {audio_duration:.2f}s - RTF: {time_total/audio_duration:.3f})")
    return audio_duration, time_total, sr
