# -*- coding: utf-8 -*-
import os, time, subprocess, logging, math
import numpy as np
import soundfile as sf
from backend.demo import (
    demo_normalize_audio,
    demo_stabilize_loudness,
    demo_encode_stereo_to_foa_manual,
    demo_foa_to_binaural,
    demo_foa_to_binaural_fallback,
    demo_build_params,
    demo_apply_motion
)
from backend.core_dsp import validate_sample_rate, SUPPORTED_SAMPLING_RATES

logger = logging.getLogger("ambisonic-demo")
DEMO_MAX_SECONDS = 15.0

def _restore_demo(result, reference_padding=512):
    if not isinstance(result, tuple):
        return result
    block, tl, tr = result
    tail = np.stack([tl, tr], axis=1)
    missing = max(reference_padding - len(tail), 0)
    if missing:
        tail = np.pad(tail, ((0, missing), (0, 0)))
    return np.concatenate([block, tail], axis=0)

def _mp3(wav, mp3):
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "quiet", "-i", wav,
                        "-codec:a", "libmp3lame", "-b:a", "320k", mp3], check=True)
        return True
    except Exception as e:
        logger.error("MP3 DEMO: %s", e)
        return False

def process_demo(input_path, output_dir, direccion=0, altura=0, apertura=0, movimiento=0,
                 hrtf=None, pos=None, **kwargs):
    t0 = time.time()
    os.makedirs(output_dir, exist_ok=True)

    info = sf.info(input_path)
    sr = validate_sample_rate(info.samplerate)
    logger.info(f"Demo: frecuencia de muestreo validada nativamente: {sr} Hz (sin remuestreo)")

    frames = min(int(DEMO_MAX_SECONDS * sr), int(info.frames))
    audio, sr = sf.read(input_path, frames=frames, dtype="float64", always_2d=True)

    audio = audio.astype(np.float64)
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = 0.95 * audio / peak
    if audio.shape[1] < 2:
        audio = np.repeat(audio, 2, axis=1)

    p = demo_build_params(direccion, altura, apertura, movimiento)

    # 1. Generar FOA directamente desde los controles del usuario (sin estimación automática previa)
    W, X, Y, Z = demo_encode_stereo_to_foa_manual(
        audio, sr,
        direccion_deg=p["direccion_deg"],
        altura_deg=p["altura_deg"],
        apertura_pct=p["apertura_pct"]
    )

    # 2. Generar salida Binaural Normal (estrictamente estática, sin movimiento)
    if hrtf is not None and pos is not None:
        b = _restore_demo(demo_foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False))
        b /= np.max(np.abs(b)) + 1e-9
    else:
        b = demo_foa_to_binaural_fallback(W, X, Y, Z)
    b = demo_normalize_audio(b, peak_target=0.95)

    # 3. Generar salida Binaural 3D Perceptual
    if p["movimiento_pct"] > 0:
        W3, X3, Y3, Z3 = demo_apply_motion(W, X, Y, Z, sr, movimiento=p["movimiento_pct"])
        if hrtf is not None and pos is not None:
            b3 = _restore_demo(demo_foa_to_binaural(W3, X3, Y3, Z3, sr, hrtf, pos, flip_az=False))
            b3 /= np.max(np.abs(b3)) + 1e-9
        else:
            b3 = demo_foa_to_binaural_fallback(W3, X3, Y3, Z3)
        b3 = 0.90 * b3 + 0.10 * b
        b3 = demo_stabilize_loudness(b3, sr, win_ms=450, strength=0.55, min_gain=0.88, max_gain=2.0)
    else:
        # Movimiento = 0: ausencia de movimiento dinámico
        if hrtf is not None and pos is not None:
            b3 = _restore_demo(demo_foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False))
            b3 /= np.max(np.abs(b3)) + 1e-9
        else:
            b3 = demo_foa_to_binaural_fallback(W, X, Y, Z)
        b3 = demo_stabilize_loudness(b3, sr, win_ms=450, strength=0.55, min_gain=0.88, max_gain=2.0)

    bw = os.path.join(output_dir, "preview_binaural.wav")
    dw = os.path.join(output_dir, "preview_3d_perceptual.wav")
    bm = os.path.join(output_dir, "preview_binaural.mp3")
    dm = os.path.join(output_dir, "preview_3d_perceptual.mp3")

    sf.write(bw, b, sr, subtype="PCM_16")
    sf.write(dw, b3, sr, subtype="PCM_16")

    if sr <= 48000:
        ok1 = _mp3(bw, bm)
        ok2 = _mp3(dw, dm)
    else:
        ok1 = False
        ok2 = False
        logger.info(f"Demo: exportación MP3 omitida para {sr} Hz (límite del estándar MP3 <= 48 kHz).")

    return {
        "sample_rate": sr,
        "duration_seconds": len(audio) / float(sr),
        "binaural_wav": bw,
        "binaural_mp3": bm if ok1 else None,
        "perceptual_wav": dw,
        "perceptual_mp3": dm if ok2 else None,
        "diagnostics_normal": {
            "direction_deg": p["direccion_deg"],
            "height_deg": p["altura_deg"],
            "width_pct": p["apertura_pct"]
        },
        "diagnostics_3d": {
            "movement_pct": p["movimiento_pct"],
            "dynamic": p["movimiento_pct"] > 0
        }
    }

native_process_demo = process_demo
