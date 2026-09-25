import sys
import psutil
import tracemalloc
import time
import numpy as np
import soundfile as sf
import os
import gc

from backend.core_dsp import stereo_to_foa, foa_to_binaural

def memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def run_diagnostic():
    tracemalloc.start()
    sr = 44100
    duration = 35
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    audio_f32 = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    audio_f32 = np.column_stack((audio_f32, audio_f32))
    
    print("=== DIAGNÓSTICO DE MEMORIA (35s) ===")
    print(f"Duración: {duration}s, SR: {sr}, Canales: 2")
    
    mem_base = memory_usage()
    print(f"Memoria base: {mem_base:.2f} MB")
    
    # FOA (float32)
    start = time.time()
    W, X, Y, Z = stereo_to_foa(audio_f32, sr)
    mem_foa = memory_usage()
    print(f"Memoria tras FOA: {mem_foa:.2f} MB")
    
    # Binaural
    hrtf_dummy = np.random.randn(6, 2, 512).astype(np.float32)
    pos_dummy = np.zeros((6, 3))
    
    binaural = foa_to_binaural(W, X, Y, Z, sr, hrtf_dummy, pos_dummy)
    mem_bin = memory_usage()
    print(f"Memoria tras Binaural: {mem_bin:.2f} MB")

    current, peak = tracemalloc.get_traced_memory()
    print(f"Peak memory interno detectado por tracemalloc: {peak / 1024 / 1024:.2f} MB")
    
    print(f"Binaural shape: {binaural.shape}, dtype: {binaural.dtype}")
    print(f"NaNs: {np.isnan(binaural).any()}, Infs: {np.isinf(binaural).any()}")
    print(f"Max Amplitude: {np.max(np.abs(binaural))}")
    tracemalloc.stop()

if __name__ == '__main__':
    run_diagnostic()
