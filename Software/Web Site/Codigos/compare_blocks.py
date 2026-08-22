import os
import sys
import numpy as np
import soundfile as sf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.processor import convert_audio

def compare_wavs(ref_path, test_path, sr, block_frames):
    ref, _ = sf.read(ref_path)
    test, _ = sf.read(test_path)
    
    min_len = min(len(ref), len(test))
    ref = ref[:min_len]
    test = test[:min_len]
    
    err = ref - test
    rms_err = np.sqrt(np.mean(err**2))
    max_err = np.max(np.abs(err))
    
    # correlación
    corr = np.corrcoef(ref.flatten(), test.flatten())[0, 1]
    
    peak_diff = np.max(np.abs(ref)) - np.max(np.abs(test))
    
    # loudness
    ref_rms = 20 * np.log10(np.sqrt(np.mean(ref**2)) + 1e-9)
    test_rms = 20 * np.log10(np.sqrt(np.mean(test**2)) + 1e-9)
    loudness_diff = ref_rms - test_rms
    
    print(f"RMS Error: {rms_err:.6f}")
    print(f"Max Error: {max_err:.6f}")
    print(f"Correlation: {corr:.6f}")
    print(f"Peak Diff: {peak_diff:.6f}")
    print(f"Loudness Diff (dB): {loudness_diff:.6f}")
    
    print("\nChecking boundaries...")
    for i in range(1, len(ref) // block_frames):
        idx = i * block_frames
        if idx < len(ref):
            diff_around = np.max(np.abs(err[idx-10:idx+10]))
            print(f"Boundary at {idx} ({(idx/sr):.2f}s): Max diff around boundary = {diff_around:.6f}")

if __name__ == "__main__":
    sr = 48000
    t = np.linspace(0, 150, 150 * sr, endpoint=False) # > 120s para forzar streaming en convert_audio
    audio = np.sin(2 * np.pi * 440 * t) * np.exp(-t/20)
    audio = np.stack([audio, audio], axis=1)
    
    input_wav = "test_input_long.wav"
    sf.write(input_wav, audio, sr)
    
    # Run blocks method
    print("Running blocks...")
    convert_audio(input_wav, "out_blocks", mode="stereo", hrtf=None, pos=None)
    
    # Generate short audio to force full memory mode
    t_short = np.linspace(0, 20, 20 * sr, endpoint=False)
    audio_short = np.sin(2 * np.pi * 440 * t_short) * np.exp(-t_short/20)
    audio_short = np.stack([audio_short, audio_short], axis=1)
    
    input_short = "test_input_short.wav"
    sf.write(input_short, audio_short, sr)
    
    # Run full memory method
    print("Running full memory...")
    convert_audio(input_short, "out_memory", mode="stereo", hrtf=None, pos=None)
    
    print("\n--- Comparando los primeros 20s de out_blocks vs out_memory ---")
    compare_wavs("out_memory/output_binaural_3D_perceptual.wav", "out_blocks/output_binaural_3D_perceptual.wav", sr, int(10.0 * sr))
