import os
import sys
import numpy as np
import soundfile as sf
import warnings
from scipy.signal import stft, istft, fftconvolve

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core_dsp import (
    stereo_to_foa, foa_to_binaural, foa_motion_convert, 
    normalize_audio, stabilize_loudness, load_sofa
)

# === NOTEBOOK FUNCTIONS EXACTLY AS IN IPYNB ===
def nb_normalize_multichannel(audio):
    audio = audio.astype(np.float64)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    return 0.95 * audio / peak

def nb_stereo_to_foa(audio_stereo, sr):
    audio_stereo = np.asarray(audio_stereo, dtype=np.float64)
    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]
    
    N_FFT = 2048
    HOP = 512
    f, t, ZL = stft(L, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, _, ZR = stft(R, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    
    eps = 1e-12
    magL = np.abs(ZL)
    magR = np.abs(ZR)
    
    M = (ZL + ZR) / 2.0
    S = (ZL - ZR) / 2.0
    E = np.abs(M) ** 2
    
    balance = (magL - magR) / (magL + magR + eps)
    balance = np.clip(balance, -1.0, 1.0)
    az = np.arcsin(balance)
    az = np.clip(az, -np.pi / 2, np.pi / 2)
    
    ALPHA_AZ = 0.20
    for k in range(1, az.shape[1]):
        az[:, k] = ALPHA_AZ * az[:, k - 1] + (1 - ALPHA_AZ) * az[:, k]
        
    az_frame = np.sum(az * E, axis=0) / (np.sum(E, axis=0) + eps)
    az_frame = np.clip(az_frame, -np.pi / 2, np.pi / 2)
    
    coh = np.abs(ZL * np.conj(ZR)) / (magL * magR + eps)
    coh = np.clip(coh, 0.0, 1.0)
    
    hf_mask = f >= 3000.0
    if not np.any(hf_mask):
        hf_mask = f >= 0.5 * np.max(f)
        
    E_hf = E[hf_mask, :]
    coh_hf = np.sum(coh[hf_mask, :] * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps)
    diffuse_hf = 1.0 - coh_hf
    diffuse_hf = np.clip(diffuse_hf, 0.0, 1.0)
    
    ild = (magL - magR) / (magL + magR + eps)
    ild_hf = np.sum(np.abs(ild[hf_mask, :]) * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps)
    ild_hf = np.clip(ild_hf, 0.0, 1.0)
    
    spectral_tilt = np.sum(E * f[:, None], axis=0) / (np.sum(E, axis=0) + eps)
    spectral_tilt = (spectral_tilt - np.min(spectral_tilt)) / (np.max(spectral_tilt) - np.min(spectral_tilt) + eps)
    spectral_tilt = np.clip(spectral_tilt, 0.0, 1.0)
    
    z_conf = 0.4 * spectral_tilt + 0.3 * diffuse_hf + 0.3 * ild_hf
    z_conf *= np.cos(az_frame)
    z_conf = np.clip(z_conf, 0.0, 1.0)
    
    from scipy.ndimage import gaussian_filter1d
    z_conf = gaussian_filter1d(z_conf, sigma=2)
    
    MAX_ELEV_DEG = 45.0
    el_frame = np.deg2rad(MAX_ELEV_DEG) * (z_conf ** 0.7)
    
    ALPHA_EL = 0.85
    for k in range(1, len(el_frame)):
        el_frame[k] = ALPHA_EL * el_frame[k - 1] + (1 - ALPHA_EL) * el_frame[k]
        
    if len(el_frame) > 20:
        el_frame[:20] = el_frame[20]
        
    el = np.tile(el_frame[None, :], (len(f), 1))
    
    theta_z = np.sin(el)
    theta_h = np.cos(el)
    theta_x = theta_h * np.cos(az)
    theta_y = theta_h * np.sin(az)
    
    W_tf = M
    X_tf = M * theta_x
    Y_tf = M * theta_y
    Z_tf = M * theta_z
    
    _, W = istft(W_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, X = istft(X_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Y = istft(Y_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Z = istft(Z_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    
    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    return W[:N], X[:N], Y[:N], Z[:N]

def nb_wrap_deg(x):
    return ((x + 180) % 360) - 180

def nb_get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4):
    az_deg = nb_wrap_deg(az_deg)
    az_all = nb_wrap_deg(pos[:, 0])
    el_all = pos[:, 1]
    az_diff = np.abs(nb_wrap_deg(az_all - az_deg))
    el_diff = np.abs(el_all - el_deg)
    dist = np.sqrt((az_diff / 180.0)**2 + (el_diff / 90.0)**2)
    idx = np.argsort(dist)[:k]
    w = 1.0 / (dist[idx] + 1e-6)
    w /= np.sum(w)
    hL = np.sum(hrtf[idx, 0, :] * w[:, None], axis=0)
    hR = np.sum(hrtf[idx, 1, :] * w[:, None], axis=0)
    return hL, hR

VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),
    (60.0,   0.0, 0.90),
    (-60.0,  0.0, 0.90),
    (180.0,  0.0, 0.55),
    (0.0,   55.0, 0.80),
    (0.0,  -45.0, 0.35),
]

def nb_foa_to_binaural(W, X, Y, Z, sr, hrtf, pos):
    N = min(len(W), len(X), len(Y), len(Z))
    W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]
    
    outL = np.zeros(N + 512)
    outR = np.zeros(N + 512)
    
    for az_deg, el_deg, gain in VIRTUAL_SPEAKERS:
        az = np.deg2rad(az_deg)
        el = np.deg2rad(el_deg)
        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)
        
        spk = gain * ((W / np.sqrt(2)) + x * X + y * Y + z * Z)
        hL, hR = nb_get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4)
        
        convL = fftconvolve(spk, hL, mode="full")
        convR = fftconvolve(spk, hR, mode="full")
        outL[:len(convL)] += convL
        outR[:len(convR)] += convR
        
    N2 = min(len(outL), len(outR))
    binaural = np.stack([outL[:N2], outR[:N2]], axis=1)
    binaural /= np.max(np.abs(binaural)) + 1e-9
    return binaural

def nb_foa_motion_preview(W, X, Y, Z, sr, rate_az=0.08, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5):
    N = min(len(W), len(X), len(Y), len(Z))
    W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]
    t = np.arange(N) / sr
    
    az = 2 * np.pi * rate_az * t
    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = np.sin(az) * X + np.cos(az) * Y
    
    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)
    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)
    
    return W, X_3d, Y_rot, Z_3d

def nb_normalize_audio(x, peak_target=0.95):
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0:
        x = peak_target * x / peak
    return x

def nb_stabilize_loudness(y, sr, win_ms=450, strength=0.55, min_gain=0.88, max_gain=2):
    eps = 1e-9
    y = np.asarray(y, dtype=np.float64)
    power = np.mean(y**2, axis=1)
    win = int(sr * win_ms / 1000)
    win = max(win, 1)
    kernel = np.ones(win) / win
    env = np.sqrt(np.convolve(power, kernel, mode="same") + eps)
    target = np.median(env) + eps
    gain = target / (env + eps)
    gain = gain ** strength
    gain = np.clip(gain, min_gain, max_gain)
    gain = np.convolve(gain, kernel, mode="same")
    y_out = y * gain[:, None]
    return nb_normalize_audio(y_out, peak_target=0.95)

# === ANALYSIS SCRIPT ===
def run_analysis(input_file):
    print("Iniciando análisis de degradación...")
    
    out_dir = os.path.join(os.path.dirname(input_file), "analysis_out")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load Data
    audio, sr = sf.read(input_file)
    if audio.ndim == 1: audio = audio[:, None]
    if audio.shape[1] < 2: audio = np.repeat(audio, 2, axis=1)
    
    hrtf_path = os.path.join(os.path.dirname(input_file), "Codigos", "hrtf.sofa")
    if not os.path.exists(hrtf_path): hrtf_path = os.path.join(os.path.dirname(input_file), "hrtf.sofa")
    hrtf, pos = load_sofa(hrtf_path)
    
    print("--- 1. NORMALIZACION ---")
    nb_audio = nb_normalize_multichannel(audio)
    
    pg_audio, _ = sf.read(input_file)
    pg_audio = pg_audio.astype(np.float64)
    if pg_audio.ndim == 1: pg_audio = pg_audio[:, None]
    pg_audio = pg_audio - np.mean(pg_audio, axis=0, keepdims=True)
    pg_peak = np.max(np.abs(pg_audio)) + 1e-9
    pg_audio = 0.95 * pg_audio / pg_peak
    if pg_audio.shape[1] < 2: pg_audio = np.repeat(pg_audio, 2, axis=1)
    
    print(f"Error Normalización (Max diff): {np.max(np.abs(nb_audio - pg_audio)):.6f}")
    
    print("--- 2. STEREO TO FOA ---")
    nb_W, nb_X, nb_Y, nb_Z = nb_stereo_to_foa(nb_audio, sr)
    pg_res = stereo_to_foa(pg_audio, sr)
    pg_W, pg_X, pg_Y, pg_Z = pg_res[0], pg_res[1], pg_res[2], pg_res[3]
    
    N = min(len(nb_W), len(pg_W))
    err_foa = max([
        np.max(np.abs(nb_W[:N] - pg_W[:N])),
        np.max(np.abs(nb_X[:N] - pg_X[:N])),
        np.max(np.abs(nb_Y[:N] - pg_Y[:N])),
        np.max(np.abs(nb_Z[:N] - pg_Z[:N]))
    ])
    print(f"Error Stereo->FOA (Max diff): {err_foa:.6f}")
    
    print("--- 3. FOA NORMALIZATION ---")
    nb_foa = np.stack([nb_W, nb_Y, nb_Z, nb_X], axis=1)
    nb_foa /= np.max(np.abs(nb_foa)) + 1e-9
    nb_W, nb_Y, nb_Z, nb_X = nb_foa[:,0], nb_foa[:,1], nb_foa[:,2], nb_foa[:,3]
    
    pg_foa = np.stack([pg_W, pg_Y, pg_Z, pg_X], axis=1)
    pg_foa /= np.max(np.abs(pg_foa)) + 1e-9
    pg_W, pg_Y, pg_Z, pg_X = pg_foa[:,0], pg_foa[:,1], pg_foa[:,2], pg_foa[:,3]
    
    err_foa_norm = np.max(np.abs(nb_foa[:N] - pg_foa[:N]))
    print(f"Error FOA Normalization (Max diff): {err_foa_norm:.6f}")
    
    print("--- 4. BINAURAL NORMAL ---")
    nb_bin = nb_foa_to_binaural(nb_W, nb_X, nb_Y, nb_Z, sr, hrtf, pos)
    nb_bin = nb_normalize_audio(nb_bin, peak_target=0.95)
    
    pg_bin_res = foa_to_binaural(pg_W, pg_X, pg_Y, pg_Z, sr, hrtf, pos, flip_az=False)
    pg_bin = pg_bin_res[0] if isinstance(pg_bin_res, tuple) else pg_bin_res
    pg_bin /= np.max(np.abs(pg_bin)) + 1e-9  # NUEVA NORMALIZACIÓN
    pg_bin = normalize_audio(pg_bin, peak_target=0.95)
    
    N_bin = min(len(nb_bin), len(pg_bin))
    print(f"Error Binaural Normal (Max diff): {np.max(np.abs(nb_bin[:N_bin] - pg_bin[:N_bin])):.6f}")
    
    print("--- 5. FOA MOTION ---")
    nb_W3d, nb_X3d, nb_Y3d, nb_Z3d = nb_foa_motion_preview(
        nb_W, nb_X, nb_Y, nb_Z, sr, rate_az=0.08, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5
    )
    
    pg_W3d, pg_X3d, pg_Y3d, pg_Z3d = foa_motion_convert(
        pg_W, pg_X, pg_Y, pg_Z, sr, rate_az=0.08, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5
    )
    
    print(f"Error FOA Motion X3d (Max diff): {np.max(np.abs(nb_X3d[:N] - pg_X3d[:N])):.6f}")
    
    print("--- 6. BINAURAL 3D PERCEPTUAL (ANTES DE LOUDNESS) ---")
    nb_bin3d = nb_foa_to_binaural(nb_W3d, nb_X3d, nb_Y3d, nb_Z3d, sr, hrtf, pos)
    nb_bin3d = 0.90 * nb_bin3d + 0.10 * nb_bin
    
    pg_bin3d_res = foa_to_binaural(pg_W3d, pg_X3d, pg_Y3d, pg_Z3d, sr, hrtf, pos, flip_az=False)
    pg_bin3d = pg_bin3d_res[0] if isinstance(pg_bin3d_res, tuple) else pg_bin3d_res
    pg_bin3d /= np.max(np.abs(pg_bin3d)) + 1e-9  # NUEVA NORMALIZACIÓN
    pg_bin3d = 0.90 * pg_bin3d + 0.10 * pg_bin
    
    N_bin3d = min(len(nb_bin3d), len(pg_bin3d))
    print(f"Error Binaural 3D Mix (Max diff): {np.max(np.abs(nb_bin3d[:N_bin3d] - pg_bin3d[:N_bin3d])):.6f}")
    
    print("--- 7. STABILIZE LOUDNESS ---")
    nb_bin3d_final = nb_stabilize_loudness(nb_bin3d, sr, win_ms=450, strength=0.55, min_gain=0.88, max_gain=2)
    
    # IMPORTANTE: processor.py usa stabilize_loudness_original con los mismos parámetros
    pg_bin3d_final = stabilize_loudness(pg_bin3d, sr, win_ms=450, strength=0.55, min_gain=0.88, max_gain=2)
    
    N_fin = min(len(nb_bin3d_final), len(pg_bin3d_final))
    print(f"Error Final (Max diff): {np.max(np.abs(nb_bin3d_final[:N_fin] - pg_bin3d_final[:N_fin])):.6f}")
    
    print("\n--- GUARDANDO ARCHIVOS ---")
    sf.write(os.path.join(out_dir, "1_notebook_original.wav"), nb_bin3d_final, sr, subtype='PCM_16')
    sf.write(os.path.join(out_dir, "2_page_current.wav"), pg_bin3d_final, sr, subtype='PCM_16')
    sf.write(os.path.join(out_dir, "3_page_no_stabilize.wav"), pg_bin3d, sr, subtype='PCM_16')
    sf.write(os.path.join(out_dir, "4_page_no_perceptual_normal_binaural.wav"), pg_bin, sr, subtype='PCM_16')
    print(f"Archivos guardados en: {out_dir}")

if __name__ == "__main__":
    audio_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_input_35s.wav")
    run_analysis(audio_path)
