import sys
import psutil
import tracemalloc
import time
import numpy as np
import soundfile as sf
import os
import gc

from backend.processor import convert_audio

def memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def run_diagnostic():
    tracemalloc.start()
    sr = 44100
    duration = 35 # 35s
    t = np.linspace(0, duration, int(sr*duration), endpoint=False)
    audio_f32 = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    audio_f32 = np.column_stack((audio_f32, audio_f32))
    
    input_path = "test_input_35s.wav"
    sf.write(input_path, audio_f32, sr, subtype='PCM_16')
    
    print("=== DIAGNÓSTICO DE MEMORIA STREAMING (35s) ===")
    print(f"Memoria base: {memory_usage():.2f} MB")
    
    # Dummy HRTF
    hrtf_dummy = np.random.randn(6, 2, 512).astype(np.float32)
    pos_dummy = np.zeros((6, 3))
    
    out_dir = "test_output_stream"
    convert_audio(input_path, out_dir, "stereo", hrtf_dummy, pos_dummy)
    
    print(f"Memoria tras convert_audio: {memory_usage():.2f} MB")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Peak memory interno detectado por tracemalloc: {peak / 1024 / 1024:.2f} MB")
    tracemalloc.stop()

if __name__ == '__main__':
    run_diagnostic()
