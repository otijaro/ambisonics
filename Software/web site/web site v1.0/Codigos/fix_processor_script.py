import os

new_code = """import os
import time
import subprocess
import numpy as np
import soundfile as sf
import logging
from backend.core_dsp import (
    normalize_audio, stabilize_loudness,
    stereo_to_foa, tetra_aformat_to_foa,
    foa_to_binaural, foa_to_binaural_fallback,
    foa_to_4_speakers,
    stereo_to_foa_demo, foa_motion_preview, build_demo_params
)

logger = logging.getLogger("ambisonic-processor")

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
    
    # Restituir procesamiento en memoria si es muy corto (< 60s)
    if audio_duration < 60.0:
        logger.info("Audio corto (< 60s), usando procesamiento en memoria completa para máxima precisión.")
        audio, _ = sf.read(input_path)
        audio = audio.astype(np.float32)
        if audio.ndim == 1: audio = audio[:, None]
        audio = audio - global_mean
        audio = (0.95 * audio / global_peak).astype(np.float32)
        if audio.shape[1] < 2: audio = np.repeat(audio, 2, axis=1)
        
        if mode == "tetra_4mic":
            W, X, Y, Z = tetra_aformat_to_foa(audio)
        else:
            W, X, Y, Z, _, _ = stereo_to_foa(audio, sr)
            
        foa = np.stack([W, Y, Z, X], axis=1)
        foa /= np.max(np.abs(foa)) + 1e-9
        W, Y, Z, X = foa[:,0], foa[:,1], foa[:,2], foa[:,3]
        
        if hrtf is not None and pos is not None:
            bin_block, _, _ = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False)
        else:
            bin_block = foa_to_binaural_fallback(W, X, Y, Z)
            
        qh = foa_to_4_speakers(W, X, Y, Z, layout="horizontal", sharpen=True)
        qv = foa_to_4_speakers(W, X, Y, Z, layout="altura", sharpen=True)
        
        W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(W, X, Y, Z, sr, rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5)
        if hrtf is not None and pos is not None:
            bin3d_block, _, _ = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False)
        else:
            bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
            
        bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
        bin3d_block = stabilize_loudness(bin3d_block, sr, win_ms=300, strength=0.70, min_gain=0.95, max_gain=1.60)
        
        qh_3d = foa_to_4_speakers(W_3d, X_3d, Y_3d, Z_3d, layout="horizontal", sharpen=True)
        qv_3d = foa_to_4_speakers(W_3d, X_3d, Y_3d, Z_3d, layout="altura", sharpen=True)
        
        sf.write(os.path.join(output_dir, "output_binaural.wav"), bin_block, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_binaural_3D_perceptual.wav"), bin3d_block, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_4_speakers_horizontal_FLBR.wav"), qh, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_4_speakers_altura_FLRT.wav"), qv, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_4_speakers_horizontal_3D_FLBR.wav"), qh_3d, sr, subtype='PCM_16')
        sf.write(os.path.join(output_dir, "output_4_speakers_altura_3D_FLRT.wav"), qv_3d, sr, subtype='PCM_16')
        
    else:
        # 2. Preparar archivos de salida
        binaural_wav = os.path.join(output_dir, "output_binaural.wav")
        binaural_3d_wav = os.path.join(output_dir, "output_binaural_3D_perceptual.wav")
        quad_h_wav = os.path.join(output_dir, "output_4_speakers_horizontal_FLBR.wav")
        quad_v_wav = os.path.join(output_dir, "output_4_speakers_altura_FLRT.wav")
        quad_h_3d_wav = os.path.join(output_dir, "output_4_speakers_horizontal_3D_FLBR.wav")
        quad_v_3d_wav = os.path.join(output_dir, "output_4_speakers_altura_3D_FLRT.wav")
        
        f_bin = sf.SoundFile(binaural_wav, 'w', sr, channels=2, subtype='PCM_16')
        f_bin3d = sf.SoundFile(binaural_3d_wav, 'w', sr, channels=2, subtype='PCM_16')
        f_qh = sf.SoundFile(quad_h_wav, 'w', sr, channels=4, subtype='PCM_16')
        f_qv = sf.SoundFile(quad_v_wav, 'w', sr, channels=4, subtype='PCM_16')
        f_qh3d = sf.SoundFile(quad_h_3d_wav, 'w', sr, channels=4, subtype='PCM_16')
        f_qv3d = sf.SoundFile(quad_v_3d_wav, 'w', sr, channels=4, subtype='PCM_16')
        
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
            
            # FOA_to_Binaural (OLA)
            if hrtf is not None and pos is not None:
                bin_block, tail_bin_L, tail_bin_R = foa_to_binaural(
                    W, X, Y, Z, sr, hrtf, pos, flip_az=False, overlap_L=tail_bin_L, overlap_R=tail_bin_R
                )
            else:
                bin_block = foa_to_binaural_fallback(W, X, Y, Z)
                
            # Quad Speakers
            qh = foa_to_4_speakers(W, X, Y, Z, layout="horizontal", sharpen=True)
            qv = foa_to_4_speakers(W, X, Y, Z, layout="altura", sharpen=True)
            
            # 3D Perceptual
            W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(
                W, X, Y, Z, sr, rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5, t_start=current_time
            )
            if hrtf is not None and pos is not None:
                bin3d_block, tail_bin3d_L, tail_bin3d_R = foa_to_binaural(
                    W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False, overlap_L=tail_bin3d_L, overlap_R=tail_bin3d_R
                )
            else:
                bin3d_block = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
                
            bin3d_block = 0.90 * bin3d_block + 0.10 * bin_block
            
            qh_3d = foa_to_4_speakers(W_3d, X_3d, Y_3d, Z_3d, layout="horizontal", sharpen=True)
            qv_3d = foa_to_4_speakers(W_3d, X_3d, Y_3d, Z_3d, layout="altura", sharpen=True)
            
            # Escritura asíncrona a disco (con clipping suave)
            f_bin.write(np.clip(bin_block, -0.95, 0.95))
            f_bin3d.write(np.clip(bin3d_block, -0.95, 0.95))
            f_qh.write(np.clip(qh, -0.95, 0.95))
            f_qv.write(np.clip(qv, -0.95, 0.95))
            f_qh3d.write(np.clip(qh_3d, -0.95, 0.95))
            f_qv3d.write(np.clip(qv_3d, -0.95, 0.95))
            
            current_time += len(W) / sr
            
        # Escribir colas residuales (reverb decay)
        if tail_bin_L is not None:
            tail_bin = np.stack([tail_bin_L, tail_bin_R], axis=1)
            f_bin.write(np.clip(tail_bin, -0.95, 0.95))
        if tail_bin3d_L is not None:
            tail_bin3d = np.stack([tail_bin3d_L, tail_bin3d_R], axis=1)
            f_bin3d.write(np.clip(tail_bin3d, -0.95, 0.95))
            
        f_bin.close()
        f_bin3d.close()
        f_qh.close()
        f_qv.close()
        f_qh3d.close()
        f_qv3d.close()
        
        time_proc = time.time() - start_proc
        logger.info(f"[TIMING] Procesamiento Streaming (Bloques de {block_sec}s): {time_proc:.2f}s")
        
        # 4. Estabilización de Loudness Final (sobre el WAV completo generado)
        start_loudness = time.time()
        bin3d_final, _ = sf.read(binaural_3d_wav)
        bin3d_final = stabilize_loudness(bin3d_final, sr, win_ms=300, strength=0.70, min_gain=0.95, max_gain=1.60)
        sf.write(binaural_3d_wav, bin3d_final, sr, subtype='PCM_16')
        logger.info(f"[TIMING] Estabilización de Loudness Final: {time.time() - start_loudness:.2f}s")
        
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

# El process_demo permanece prácticamente igual
def process_demo(input_path: str, output_dir: str, direccion: float, altura: float, apertura: float, movimiento: float, hrtf, pos):
    start_total = time.time()
    logger.info(f"Iniciando process_demo: {input_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Cargar audio (max 15s)
    start_load = time.time()
    audio, sr = sf.read(input_path)
    
    # Simple normalización
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = (0.95 * audio / peak).astype(np.float32)
    
    if audio.shape[1] < 2:
        audio = np.repeat(audio, 2, axis=1)
    
    MAX_SECONDS = 15.0
    N = min(len(audio), int(MAX_SECONDS * sr))
    audio_demo = audio[:N, :2]
    time_load = time.time() - start_load
    logger.info(f"[TIMING] Carga y recorte (15s): {time_load:.2f}s")
    
    # 2. Codificación FOA Demo
    start_enc = time.time()
    params = build_demo_params(
        azimuth_shift_deg=direccion,
        elevation_boost_pct=altura,
        width_pct=apertura,
        movement_pct=movimiento
    )
    W, X, Y, Z = stereo_to_foa_demo(audio_demo, sr, params)
    time_enc = time.time() - start_enc
    logger.info(f"[TIMING] Codificación FOA Demo: {time_enc:.2f}s")
    
    # 3. Render Binaural Normal
    start_bin = time.time()
    if hrtf is not None and pos is not None:
        binaural, _, _ = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False)
    else:
        binaural = foa_to_binaural_fallback(W, X, Y, Z)
    binaural = normalize_audio(binaural, peak_target=0.95)
    time_bin = time.time() - start_bin
    logger.info(f"[TIMING] Render Binaural: {time_bin:.2f}s")
    
    # 4. Render 3D Perceptual (Movimiento)
    start_3d = time.time()
    W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(
        W, X, Y, Z, sr,
        rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5
    )
    if hrtf is not None and pos is not None:
        binaural_3d, _, _ = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos, flip_az=False)
    else:
        binaural_3d = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)
        
    binaural_3d = 0.90 * binaural_3d + 0.10 * binaural
    binaural_3d = stabilize_loudness(binaural_3d, sr, win_ms=300, strength=0.70, min_gain=0.95, max_gain=1.60)
    time_3d = time.time() - start_3d
    logger.info(f"[TIMING] Render 3D Movimiento: {time_3d:.2f}s")
    
    # 5. Exportar WAV y MP3
    start_exp = time.time()
    
    binaural_wav = os.path.join(output_dir, "preview_binaural.wav")
    binaural_mp3 = os.path.join(output_dir, "preview_binaural.mp3")
    perceptual_wav = os.path.join(output_dir, "preview_3d_perceptual.wav")
    perceptual_mp3 = os.path.join(output_dir, "preview_3d_perceptual.mp3")
    
    sf.write(binaural_wav, binaural, sr, subtype="PCM_16")
    sf.write(perceptual_wav, binaural_3d, sr, subtype="PCM_16")
    
    try:
        subprocess.Popen([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", binaural_wav,
            "-codec:a", "libmp3lame", "-b:a", "320k",
            binaural_mp3
        ])
        subprocess.Popen([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", perceptual_wav,
            "-codec:a", "libmp3lame", "-b:a", "320k",
            perceptual_mp3
        ])
    except Exception as e:
        logger.error(f"Error iniciando conversión MP3: {e}")
        
    time_exp = time.time() - start_exp
    logger.info(f"[TIMING] Exportación WAV/MP3: {time_exp:.2f}s")
    
    time_total = time.time() - start_total
    audio_duration = len(audio_demo) / sr
    logger.info(f"[TIMING] PROCESO TOTAL DEMO: {time_total:.2f}s (Audio: {audio_duration:.2f}s)")
"""

with open(r'c:\Users\Usuario\Downloads\ambisonic\backend\processor.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print("processor.py written successfully.")
