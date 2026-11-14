import os
import time
import subprocess
import numpy as np
import soundfile as sf
import logging
from backend.core_dsp import (
    normalize_audio, stabilize_loudness,
    stereo_to_foa, tetra_aformat_to_foa,
    foa_to_binaural, foa_to_binaural_fallback,
    stereo_to_foa_demo, foa_motion_convert, foa_motion_demo, build_demo_params,
    DEMO_VIRTUAL_SPEAKERS
)

logger = logging.getLogger("ambisonic-processor")


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


def convert_audio(input_path: str, output_dir: str, mode: str, hrtf, pos):
    start_total = time.time()
    logger.info(f"Iniciando convert_audio (Streaming OLA): {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Primera pasada: Detectar pico global y media global
    start_peak = time.time()
    with sf.SoundFile(input_path, 'r') as f_in:
        sr = f_in.samplerate
        channels = f_in.channels
        total_frames = len(f_in)
        audio_duration = total_frames / sr
        
    block_sec = 10.0
    block_frames = int(block_sec * sr)
    
    global_sum = 0.0
    total_samples = 0
    for block in sf.blocks(input_path, blocksize=block_frames, dtype='float32'):
        if block.ndim == 1: block = block[:, None]
        global_sum += np.sum(block, axis=0)
        total_samples += len(block)
    global_mean = global_sum / total_samples

    global_peak = 1e-9
    for block in sf.blocks(input_path, blocksize=block_frames, dtype='float32'):
        if block.ndim == 1: block = block[:, None]
        block = block - global_mean
        global_peak = max(global_peak, np.max(np.abs(block)))
        
    time_peak = time.time() - start_peak
    logger.info(f"[TIMING] Búsqueda de pico global: {time_peak:.2f}s (Pico: {global_peak:.4f})")
    
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
        
        # 2. Conversión a FOA (ignorando el estado de streaming si lo devuelve)
        if mode == "tetra_4mic":
            if audio.shape[1] < 4:
                raise ValueError("El modo tetra requiere 4 canales.")
            # tetra_aformat_to_foa puede devolver W, X, Y, Z o más dependiendo de cómo quedó en core_dsp
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
            bin_block /= np.max(np.abs(bin_block)) + 1e-9  # Restore notebook's internal normalization
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
            bin3d_block /= np.max(np.abs(bin3d_block)) + 1e-9  # Restore notebook's internal normalization
        else:
            bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
            
        bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
        
        # Estabilizar volumen con parámetros originales del notebook
        bin3d_block = stabilize_loudness(
            bin3d_block, sr, 
            win_ms=450, strength=0.55, min_gain=0.88, max_gain=2
        )
        
        sf.write(os.path.join(output_dir, "output_binaural.wav"), bin_block, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_binaural_3D_perceptual.wav"), bin3d_block, sr, subtype='PCM_16')
        
    else:
        # 2. Preparar archivos de salida
        foa_wav = os.path.join(output_dir, "output_foa.wav")
        binaural_wav = os.path.join(output_dir, "output_binaural.wav")
        binaural_3d_wav = os.path.join(output_dir, "output_binaural_3D_perceptual.wav")
        
        f_foa = sf.SoundFile(foa_wav, 'w', sr, channels=4, subtype='FLOAT')
        f_bin = sf.SoundFile(binaural_wav, 'w', sr, channels=2, subtype='FLOAT')
        f_bin3d = sf.SoundFile(binaural_3d_wav, 'w', sr, channels=2, subtype='FLOAT')
        
        last_az = None
        last_el = None
        
        tail_bin_L = None
        tail_bin_R = None
        tail_bin3d_L = None
        tail_bin3d_R = None
        
        start_proc = time.time()
        
        current_time = 0.0
        
        # 3. Segunda pasada: Procesamiento por bloques (Streaming)
        for block in sf.blocks(input_path, blocksize=block_frames, dtype='float32'):
            if block.ndim == 1: block = block[:, None]
            
            block = block - global_mean
            block = (0.95 * block / global_peak).astype(np.float32)
            
            # FOA Encoding
            if mode == "tetra_4mic":
                if block.shape[1] < 4:
                    raise ValueError("El modo tetra requiere 4 canales.")
                W, X, Y, Z = tetra_aformat_to_foa(block)
            else:
                if block.shape[1] < 2:
                    block = np.repeat(block, 2, axis=1)
                W, X, Y, Z, last_az, last_el = stereo_to_foa(block, sr, last_az, last_el)
                
            # NO normalizamos FOA por bloque para evitar breathing.
            foa = np.stack([W, Y, Z, X], axis=1)
            f_foa.write(foa)
            
            # FOA_to_Binaural (OLA)
            if hrtf is not None and pos is not None:
                bin_block, tail_bin_L, tail_bin_R = foa_to_binaural(
                    W, X, Y, Z, sr, hrtf, pos, flip_az=False, overlap_L=tail_bin_L, overlap_R=tail_bin_R
                )
            else:
                bin_block = foa_to_binaural_fallback(W, X, Y, Z)
            
            # 3D Perceptual
            W_3d, X_3d, Y_3d, Z_3d = foa_motion_convert(
                W, X, Y, Z, sr,
                rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5,
                t_start=current_time
            )
            if hrtf is not None and pos is not None:
                bin3d_block, tail_bin3d_L, tail_bin3d_R = foa_to_binaural(
                    W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False, overlap_L=tail_bin3d_L, overlap_R=tail_bin3d_R
                )
            else:
                bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
                
            bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
            
            # Escritura asíncrona a disco (usamos FLOAT temporal para no perder fidelidad)
            f_bin.write(bin_block)
            f_bin3d.write(bin3d_block)
            
            current_time += len(W) / sr
            
        # Escribir colas residuales (reverb decay)
        if tail_bin_L is not None:
            tail_bin = np.stack([tail_bin_L, tail_bin_R], axis=1)
            f_bin.write(tail_bin)
        if tail_bin3d_L is not None:
            tail_bin3d = np.stack([tail_bin3d_L, tail_bin3d_R], axis=1)
            f_bin3d.write(tail_bin3d)
            
        f_foa.close()
        f_bin.close()
        f_bin3d.close()
        
        time_proc = time.time() - start_proc
        logger.info(f"[TIMING] Procesamiento Streaming (Bloques de {block_sec}s): {time_proc:.2f}s")
    
        # 9. Normalizar todo a nivel global y aplicar stabilize_loudness
        logger.info("Normalizando globalmente y estabilizando loudness...")
        
        # FOA
        final_foa, _ = sf.read(foa_wav)
        final_foa /= np.max(np.abs(final_foa)) + 1e-9
        sf.write(foa_wav, final_foa, sr, subtype='PCM_16')
        
        # Archivos que solo requieren normalización
        for fpath in [binaural_wav]:
            arr, _ = sf.read(fpath)
            arr = normalize_audio(arr, peak_target=0.95)
            sf.write(fpath, arr, sr, subtype='PCM_16')
            
        # Binaural 3D: Pre-normalizar a 1.0 (como en notebook) y luego estabilizar
        final_3d, _ = sf.read(binaural_3d_wav)
        final_3d /= np.max(np.abs(final_3d)) + 1e-9
        final_3d = stabilize_loudness(
            final_3d, sr, 
            win_ms=450, strength=0.55, min_gain=0.88, max_gain=2.0
        )
        sf.write(binaural_3d_wav, final_3d, sr, subtype='PCM_16')
        
    # 5. Convertir a MP3
    start_exp = time.time()
    binaural_wav = os.path.join(output_dir, "output_binaural.wav")
    binaural_3d_wav = os.path.join(output_dir, "output_binaural_3D_perceptual.wav")
    binaural_mp3 = os.path.join(output_dir, "output_binaural.mp3")
    binaural_3d_mp3 = os.path.join(output_dir, "output_binaural_3D_perceptual.mp3")
    try:
        subprocess.Popen([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", binaural_wav,
            "-codec:a", "libmp3lame", "-b:a", "320k",
            binaural_mp3
        ])
        subprocess.Popen([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", binaural_3d_wav,
            "-codec:a", "libmp3lame", "-b:a", "320k",
            binaural_3d_mp3
        ])
    except Exception as e:
        logger.error(f"Error iniciando conversión MP3: {e}")
        
    time_exp = time.time() - start_exp
    logger.info(f"[TIMING] Lanzamiento MP3 asíncrono: {time_exp:.2f}s")
    
    time_total = time.time() - start_total
    logger.info(f"[TIMING] PROCESO TOTAL: {time_total:.2f}s (Audio: {audio_duration:.2f}s)")
    return audio_duration, time_total, sr
