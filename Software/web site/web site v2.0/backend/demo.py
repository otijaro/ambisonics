# -*- coding: utf-8 -*-
"""Copia aislada del core del CONVERT para el DEMO."""
import numpy as np
import soundfile as sf
from scipy.signal import stft, istft, fftconvolve
from scipy.ndimage import gaussian_filter1d

# =========================================================
# PARÁMETROS GENERALES
# =========================================================
DEMO_N_FFT = 2048
DEMO_HOP = DEMO_N_FFT // 4

DEMO_MAX_ELEV_DEG = 45.0
DEMO_ALPHA_AZ = 0.20
DEMO_ALPHA_EL = 0.85

# Render binaural desde FOA
CONVERT_VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),
    (60.0,   0.0, 0.90),
    (-60.0,  0.0, 0.90),
    (180.0,  0.0, 0.55),
    (0.0,   55.0, 0.80),
    (0.0,  -45.0, 0.35),
]


# Compatibilidad con llamadas existentes de Convert
DEMO_VIRTUAL_SPEAKERS = CONVERT_VIRTUAL_SPEAKERS


# =========================================================
# UTILIDADES
# =========================================================
def demo_normalize_multichannel(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    return (0.95 * audio / peak).astype(np.float32)

def demo_normalize_audio(x, peak_target=0.95):
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0:
        x = peak_target * x / peak
    return x

def demo_wrap_deg(x):
    return ((x + 180) % 360) - 180

def demo_clamp(v, lo, hi):
    return max(lo, min(hi, v))

def demo_stabilize_loudness(y, sr,
                       win_ms=455,
                       strength=0.70,
                       min_gain=2,
                       max_gain=2.5):
    eps = 1e-9

    y = np.asarray(y, dtype=np.float64)

    power = np.mean(y**2, axis=1)

    win = int(sr * win_ms / 1000)
    win = max(win, 1)

    kernel = np.ones(win, dtype=np.float64) / win

    smoothed_power = fftconvolve(power, kernel, mode="same")

    # La potencia suavizada es matemáticamente no negativa.
    # fftconvolve puede producir valores negativos diminutos
    # por error de redondeo, por lo que se eliminan únicamente
    # esos valores imposibles antes de aplicar sqrt.
    smoothed_power = np.maximum(smoothed_power, 0.0)

    env = np.sqrt(smoothed_power + eps)

    target = np.median(env) + eps

    gain = target / (env + eps)
    gain = gain ** strength
    gain = np.clip(gain, min_gain, max_gain)

    gain = fftconvolve(gain, kernel, mode="same")
    gain = np.maximum(gain, 0.0)

    y_out = y * gain[:, None]

    return demo_normalize_audio(y_out, peak_target=0.95)

# =========================================================
# SOFA/HRTF
# =========================================================
def demo_get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4):
    az_deg = demo_wrap_deg(az_deg)
    az_all = demo_wrap_deg(pos[:, 0])
    el_all = pos[:, 1]
    az_diff = np.abs(demo_wrap_deg(az_all - az_deg))
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
def demo_stereo_to_foa(audio_stereo, sr, last_az=None, last_el=None):
    audio_stereo = np.asarray(audio_stereo, dtype=np.float32)
    if audio_stereo.ndim != 2 or audio_stereo.shape[1] < 2:
        raise ValueError("El modo estéreo requiere un audio de mínimo 2 canales: L y R.")
    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]

    f, t, ZL = stft(L, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)
    _, _, ZR = stft(R, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)
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
        az[:, 0] = DEMO_ALPHA_AZ * last_az + (1 - DEMO_ALPHA_AZ) * az[:, 0]

    for k in range(1, az.shape[1]):
        az[:, k] = DEMO_ALPHA_AZ * az[:, k - 1] + (1 - DEMO_ALPHA_AZ) * az[:, k]

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

    el_frame = np.deg2rad(DEMO_MAX_ELEV_DEG) * (z_conf ** 0.7)
    
    if last_el is not None:
        el_frame[0] = DEMO_ALPHA_EL * last_el + (1 - DEMO_ALPHA_EL) * el_frame[0]
        
    for k in range(1, len(el_frame)):
        el_frame[k] = DEMO_ALPHA_EL * el_frame[k - 1] + (1 - DEMO_ALPHA_EL) * el_frame[k]

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

    _, W = istft(W_tf, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)
    _, X = istft(X_tf, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)
    _, Y = istft(Y_tf, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)
    _, Z = istft(Z_tf, fs=sr, nperseg=DEMO_N_FFT, noverlap=DEMO_N_FFT - DEMO_HOP)

    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    return W[:N], X[:N], Y[:N], Z[:N], az[:, -1], el_frame[-1]

def demo_tetra_aformat_to_foa(audio4):
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

def demo_foa_to_binaural(W, X, Y, Z, sr, hrtf, pos, flip_az=False, overlap_L=None, overlap_R=None, virtual_speakers=None):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    overlap_len = hrtf.shape[2] - 1
    outL = np.zeros(N + overlap_len, dtype=np.float32)
    outR = np.zeros(N + overlap_len, dtype=np.float32)

    speakers = DEMO_VIRTUAL_SPEAKERS if virtual_speakers is None else virtual_speakers
    for az_deg, el_deg, gain in speakers:
        az = np.deg2rad(az_deg) if not flip_az else -np.deg2rad(az_deg)
        el = np.deg2rad(el_deg)

        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)

        spk = gain * ((W / np.sqrt(2)) + x * X + y * Y + z * Z)
        hL, hR = demo_get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4)

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

def demo_foa_to_binaural_fallback(W, X, Y, Z):
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




def demo_foa_motion_original(W, X, Y, Z, sr, rate_az=0.12, rate_el=0.10, max_el_deg=60.0, z_preview_gain=3.5, t_start=0.0):
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


def demo_build_params(direccion=0.0, altura=0.0, apertura=0.0, movimiento=0.0):
    def n(v):
        try: return float(v)
        except: return 0.0
    d=demo_clamp(n(direccion),-90,90); h=demo_clamp(n(altura),0,100)
    a=demo_clamp(n(apertura),0,100); mv=demo_clamp(n(movimiento),0,100)
    return {"direccion_deg":d,"altura_pct":h,"apertura_pct":a,"movimiento_pct":mv,
            "altura_norm":h/100.0,"apertura_norm":a/100.0,"movimiento_norm":mv/100.0}

def demo_apply_static_controls(W,X,Y,Z,direccion=0,altura=0,apertura=0):
    p=demo_build_params(direccion,altura,apertura,0)
    W=np.asarray(W).copy(); X=np.asarray(X).copy(); Y=np.asarray(Y).copy(); Z=np.asarray(Z).copy()
    if p["direccion_deg"] != 0:
        q=np.deg2rad(p["direccion_deg"]); xo=X.copy(); yo=Y.copy()
        X=np.cos(q)*xo-np.sin(q)*yo; Y=np.sin(q)*xo+np.cos(q)*yo
    if p["apertura_pct"] != 0: Y*=1+p["apertura_norm"]
    if p["altura_pct"] != 0: Z*=1+p["altura_norm"]
    return W,X,Y,Z

def demo_apply_motion(W,X,Y,Z,sr,movimiento=0):
    q=demo_build_params(movimiento=movimiento)["movimiento_norm"]
    if q<=0: return W,X,Y,Z
    return demo_foa_motion_original(W,X,Y,Z,sr,0.12*q,0.10*q,60.0*q,1.0+2.5*q)
