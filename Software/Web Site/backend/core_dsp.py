import numpy as np
import soundfile as sf
from scipy.signal import stft, istft, fftconvolve
from scipy.ndimage import gaussian_filter1d
from pysofaconventions import SOFAFile

# =========================================================
# PARÁMETROS GENERALES
# =========================================================
N_FFT = 2048
HOP = N_FFT // 4

MAX_ELEV_DEG = 45.0
ALPHA_AZ = 0.20
ALPHA_EL = 0.85

# Render binaural desde FOA
CONVERT_VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),
    (60.0,   0.0, 0.90),
    (-60.0,  0.0, 0.90),
    (180.0,  0.0, 0.55),
    (0.0,   55.0, 0.80),
    (0.0,  -45.0, 0.35),
]

DEMO_VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),
    (60.0,   0.0, 0.75),
    (-60.0,  0.0, 0.75),
    (180.0,  0.0, 0.30),
    (0.0,   45.0, 0.35),
    (0.0,  -45.0, 0.18),
]

# Compatibilidad con llamadas existentes de Convert
VIRTUAL_SPEAKERS = CONVERT_VIRTUAL_SPEAKERS

# Demo base params
BASE_PARAMS = {
    "N_FFT": 2048,
    "MAX_ELEV_DEG": 45.0,
    "ALPHA_AZ": 0.20,
    "ALPHA_EL": 0.85,
    "X_GAIN": 1.15,
    "Y_GAIN": 1.35,
    "Z_GAIN": 1.20,
    "WIDTH_BLEND": 0.40,
    "DEMO_MOVEMENT_GAIN": 1.20,
}

# =========================================================
# UTILIDADES
# =========================================================
def normalize_multichannel(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    return (0.95 * audio / peak).astype(np.float32)

def normalize_audio(x, peak_target=0.95):
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0:
        x = peak_target * x / peak
    return x

def wrap_deg(x):
    return ((x + 180) % 360) - 180

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def stabilize_loudness(y, sr, win_ms=455, strength=0.70, min_gain=2, max_gain=2.5):
    eps = 1e-9
    y = np.asarray(y, dtype=np.float32)
    power = np.mean(y**2, axis=1)
    win = int(sr * win_ms / 1000)
    win = max(win, 1)
    kernel = np.ones(win) / win
    env = np.sqrt(fftconvolve(power, kernel, mode="same") + eps)
    target = np.median(env) + eps
    gain = target / (env + eps)
    gain = gain ** strength
    gain = np.clip(gain, min_gain, max_gain)
    gain = fftconvolve(gain, kernel, mode="same")
    y_out = y * gain[:, None]
    return normalize_audio(y_out, peak_target=0.95)

# =========================================================
# SOFA/HRTF
# =========================================================
def load_sofa(path: str):
    s = SOFAFile(path, 'r')
    ir = s.getDataIR()
    pos = s.getVariableValue('SourcePosition')
    return ir, pos

def get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4):
    az_deg = wrap_deg(az_deg)
    az_all = wrap_deg(pos[:, 0])
    el_all = pos[:, 1]
    az_diff = np.abs(wrap_deg(az_all - az_deg))
    el_diff = np.abs(el_all - el_deg)
    dist = np.sqrt((az_diff / 180.0)**2 + (el_diff / 90.0)**2)
    idx = np.argsort(dist)[:k]
    w = 1.0 / (dist[idx] + 1e-6)
    w /= np.sum(w)
    hL = np.sum(hrtf[idx, 0, :] * w[:, None], axis=0)
    hR = np.sum(hrtf[idx, 1, :] * w[:, None], axis=0)
    return hL, hR

# =========================================================
# FOA ENCODERS
# =========================================================
def stereo_to_foa(audio_stereo, sr, last_az=None, last_el=None):
    audio_stereo = np.asarray(audio_stereo, dtype=np.float32)
    if audio_stereo.ndim != 2 or audio_stereo.shape[1] < 2:
        raise ValueError("El modo estéreo requiere un audio de mínimo 2 canales: L y R.")
    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]

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
    
    if last_az is not None:
        az[:, 0] = ALPHA_AZ * last_az + (1 - ALPHA_AZ) * az[:, 0]

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

    z_conf = (0.4 * spectral_tilt + 0.3 * diffuse_hf + 0.3 * ild_hf)
    z_conf *= np.cos(az_frame)
    z_conf = np.clip(z_conf, 0.0, 1.0)
    z_conf = gaussian_filter1d(z_conf, sigma=2)

    el_frame = np.deg2rad(MAX_ELEV_DEG) * (z_conf ** 0.7)
    
    if last_el is not None:
        el_frame[0] = ALPHA_EL * last_el + (1 - ALPHA_EL) * el_frame[0]
        
    for k in range(1, len(el_frame)):
        el_frame[k] = ALPHA_EL * el_frame[k - 1] + (1 - ALPHA_EL) * el_frame[k]

    if len(el_frame) > 20 and last_el is None:
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
    return W[:N], X[:N], Y[:N], Z[:N], az[:, -1], el_frame[-1]

def tetra_aformat_to_foa(audio4):
    audio4 = np.asarray(audio4, dtype=np.float32)
    if audio4.ndim != 2 or audio4.shape[1] < 4:
        raise ValueError("Se requieren 4 canales en orden FLU, FRD, BLD, BRU.")
    M_tetra = 0.5 * np.array([
        [1.0,        1.0,        1.0,        1.0],
        [np.sqrt(3), np.sqrt(3), -np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), -np.sqrt(3), np.sqrt(3)],
    ], dtype=np.float32)
    WXYZ = audio4[:, :4] @ M_tetra.T
    return WXYZ[:, 0], WXYZ[:, 1], WXYZ[:, 2], WXYZ[:, 3]

def foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False, overlap_L=None, overlap_R=None, virtual_speakers=None):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    overlap_len = hrtf.shape[2] - 1
    outL = np.zeros(N + overlap_len, dtype=np.float32)
    outR = np.zeros(N + overlap_len, dtype=np.float32)

    speakers = VIRTUAL_SPEAKERS if virtual_speakers is None else virtual_speakers
    for az_deg, el_deg, gain in speakers:
        az = np.deg2rad(az_deg) if not flip_az else -np.deg2rad(az_deg)
        el = np.deg2rad(el_deg)

        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)

        spk = gain * ((W / np.sqrt(2)) + x * X + y * Y + z * Z)
        hL, hR = get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4)

        convL = fftconvolve(spk, hL, mode="full")
        convR = fftconvolve(spk, hR, mode="full")

        outL[:len(convL)] += convL
        outR[:len(convR)] += convR

    if overlap_L is not None:
        n_ol = min(len(overlap_L), len(outL))
        outL[:n_ol] += overlap_L[:n_ol]
    if overlap_R is not None:
        n_ol = min(len(overlap_R), len(outR))
        outR[:n_ol] += overlap_R[:n_ol]

    blockL = outL[:N]
    blockR = outR[:N]
    tailL = outL[N:N+overlap_len]
    tailR = outR[N:N+overlap_len]

    binaural = np.stack([blockL, blockR], axis=1)
    return binaural, tailL, tailR

def foa_to_binaural_fallback(W, X, Y, Z):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]
    left = 0.60 * W + 1.00 * Y + 0.35 * X + 0.20 * Z
    right = 0.60 * W - 1.00 * Y + 0.35 * X + 0.20 * Z
    binaural = np.stack([left, right], axis=1)
    binaural /= np.max(np.abs(binaural)) + 1e-9
    return binaural

def foa_to_4_speakers(W, X, Y, Z, layout="horizontal", sharpen=True):
    if sharpen:
        W_use = W / np.sqrt(3)
    else:
        W_use = W

    if layout == "horizontal":
        F = 0.5 * (W_use + X)
        L = 0.5 * (W_use + Y)
        B = 0.5 * (W_use - X)
        R = 0.5 * (W_use - Y)
        speakers4 = np.stack([F, L, B, R], axis=1)
    elif layout == "altura":
        F = 0.5 * (W_use + X)
        L = 0.5 * (W_use + Y)
        R = 0.5 * (W_use - Y)
        T = 0.5 * (W_use + Z)
        speakers4 = np.stack([F, L, R, T], axis=1)
    else:
        raise ValueError("layout debe ser 'horizontal' o 'altura'.")

    peak = np.max(np.abs(speakers4)) + 1e-9
    if peak > 0.99:
        speakers4 = 0.99 * speakers4 / peak
    return speakers4

# =========================================================
# DEMO SPECIFIC
# =========================================================
def build_demo_params(azimuth_shift_deg=0.0, elevation_boost_pct=10.0, width_pct=45.0, movement_pct=35.0):
    p = BASE_PARAMS.copy()
    width_norm = clamp(width_pct, 0, 100) / 100.0
    p["WIDTH_BLEND"] = 0.05 + 0.85 * width_norm
    elev_norm = clamp(elevation_boost_pct, 0, 100) / 100.0
    p["MAX_ELEV_DEG"] = 10.0 + 65.0 * elev_norm
    p["Z_GAIN"] = 0.20 + 1.80 * elev_norm
    move_norm = clamp(movement_pct, 0, 100) / 100.0
    p["ALPHA_AZ"] = 0.60 - 0.50 * move_norm
    p["ALPHA_EL"] = 0.95 - 0.35 * move_norm
    p["DEMO_MOVEMENT_GAIN"] = 0.60 + 1.80 * move_norm
    p["USER_AZ_SHIFT_DEG"] = clamp(azimuth_shift_deg, -90, 90)
    return p

def stereo_to_foa_demo(audio_stereo: np.ndarray, sr: int, params: dict):
    N_FFT_DEMO = int(params["N_FFT"])
    hop = N_FFT_DEMO // 4
    eps = 1e-12

    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]
    f, t, ZL = stft(L, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)
    _, _, ZR = stft(R, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)
    magL = np.abs(ZL)
    magR = np.abs(ZR)
    M = (ZL + ZR) / 2.0
    S = (ZL - ZR) / 2.0
    balance = (magL - magR) / (magL + magR + eps)
    balance = np.clip(balance, -1.0, 1.0)
    az = np.arcsin(balance)
    az = np.clip(az, -np.pi/2, np.pi/2)

    user_shift = np.deg2rad(params.get("USER_AZ_SHIFT_DEG", 0.0))
    az = np.clip(az + user_shift, -np.pi/2, np.pi/2)
    az *= params.get("DEMO_MOVEMENT_GAIN", 1.0)
    az = np.clip(az, -np.pi/2, np.pi/2)

    alpha_az = float(params["ALPHA_AZ"])
    for k in range(1, az.shape[1]):
        az[:, k] = alpha_az * az[:, k - 1] + (1 - alpha_az) * az[:, k]

    coh = np.abs(ZL * np.conj(ZR)) / (magL * magR + eps)
    coh = np.clip(coh, 0.0, 1.0)
    diffuse = 1.0 - coh
    diff_min = np.min(diffuse)
    diff_max = np.max(diffuse)
    diffuse_n = (diffuse - diff_min) / (diff_max - diff_min + eps)

    hf_weight = np.clip((f[:, None] - 1800.0) / (7000.0 - 1800.0), 0.0, 1.0)
    E = np.abs(M)**2
    brightness_frame = np.sum(E * hf_weight, axis=0) / (np.sum(E, axis=0) + eps)
    diffuse_hf_frame = np.sum(E * diffuse_n * hf_weight, axis=0) / (np.sum(E * hf_weight, axis=0) + eps)

    z_conf = 0.55 * brightness_frame + 0.45 * diffuse_hf_frame
    z_conf = np.clip(z_conf, 0.0, 1.0)

    max_elev_deg = float(params["MAX_ELEV_DEG"])
    el_frame = np.deg2rad(max_elev_deg) * (z_conf ** 0.6)

    alpha_el = float(params["ALPHA_EL"])
    for k in range(1, len(el_frame)):
        el_frame[k] = alpha_el * el_frame[k - 1] + (1 - alpha_el) * el_frame[k]
    if len(el_frame) > 20:
        el_frame[:20] = el_frame[20]

    el = np.tile(el_frame[None, :], (len(f), 1))
    theta_z = np.sin(el)
    theta_h = np.cos(el)
    theta_x = theta_h * np.cos(az)
    theta_y = theta_h * np.sin(az)

    X_GAIN = float(params["X_GAIN"])
    Y_GAIN = float(params["Y_GAIN"])
    Z_GAIN = float(params["Z_GAIN"])
    width_blend = float(params["WIDTH_BLEND"])

    W_tf = M / np.sqrt(2)
    X_tf = X_GAIN * M * theta_x
    Y_tf = Y_GAIN * ((1.0 - width_blend) * M * theta_y + width_blend * S)
    Z_tf = Z_GAIN * M * theta_z * hf_weight

    _, W = istft(W_tf, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)
    _, X = istft(X_tf, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)
    _, Y = istft(Y_tf, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)
    _, Z = istft(Z_tf, fs=sr, nperseg=N_FFT_DEMO, noverlap=N_FFT_DEMO - hop)

    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]

    peak = np.max(np.abs(np.stack([W, X, Y, Z], axis=1))) + 1e-9
    W /= peak
    X /= peak
    Y /= peak
    Z /= peak

    return W, X, Y, Z

def foa_motion_convert(W, X, Y, Z, sr, rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5, t_start=0.0):
    N = min(len(W), len(X), len(Y), len(Z))
    W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]
    t = t_start + np.arange(N) / sr
    az = 2 * np.pi * rate_az * t
    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = np.sin(az) * X + np.cos(az) * Y
    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)
    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)
    W_3d = W
    Y_3d = Y_rot
    return W_3d, X_3d, Y_3d, Z_3d

def foa_motion_demo(W, X, Y, Z, sr, rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5, t_start=0.0):
    N = min(len(W), len(X), len(Y), len(Z))
    W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]
    t = t_start + np.arange(N) / sr
    az = 2 * np.pi * rate_az * t
    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = -(np.sin(az) * X + np.cos(az) * Y)
    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)
    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)
    W_3d = W
    Y_3d = Y_rot
    return W_3d, X_3d, Y_3d, Z_3d
