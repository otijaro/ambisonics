import os
import sys
import gc
import time
import numpy as np
import soundfile as sf
from scipy.signal import stft, istft, fftconvolve
from scipy.ndimage import gaussian_filter1d
from pysofaconventions import SOFAFile

# =========================================================
# PARÁMETROS DEL NOTEBOOK ORIGINAL
# =========================================================
N_FFT = 2048
HOP = N_FFT // 4
MAX_ELEV_DEG = 45.0
ALPHA_AZ = 0.20
ALPHA_EL = 0.85

VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),   # frente
    (60.0,   0.0, 0.90),   # izquierda-frente
    (-60.0,  0.0, 0.90),   # derecha-frente
    (180.0,  0.0, 0.55),   # atrás
    (0.0,   55.0, 0.80),   # arriba más perceptible
    (0.0,  -45.0, 0.35),   # abajo
]

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def rms(x):
    return np.sqrt(np.mean(x**2) + 1e-12)

def smooth1d(y, win=9):
    y = np.asarray(y, dtype=float)
    if win < 2 or len(y) < win:
        return y.copy()
    if win % 2 == 0:
        win += 1
    k = np.ones(win) / win
    pad = win // 2
    ypad = np.pad(y, (pad, pad), mode="edge")
    return np.convolve(ypad, k, mode="valid")

def wrap_deg(x):
    return ((x + 180) % 360) - 180

def load_sofa(path):
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

def normalize_multichannel(audio):
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    audio = 0.95 * audio / peak
    return audio

def stereo_to_foa(audio_stereo, sr):
    audio_stereo = np.asarray(audio_stereo, dtype=np.float32)
    if audio_stereo.ndim != 2 or audio_stereo.shape[1] < 2:
        raise ValueError("El modo estéreo requiere al menos 2 canales: L y R.")

    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]

    f, t, ZL = stft(L, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, _, ZR = stft(R, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)

    eps = 1e-12
    magL = np.abs(ZL)
    magR = np.abs(ZR)

    M = (ZL + ZR) * 0.5

    coh = np.abs(ZL * np.conj(ZR)) / (magL * magR + eps)
    coh = np.clip(coh, 0.0, 1.0)
    del ZL, ZR
    gc.collect()

    E = np.abs(M) ** 2

    balance = (magL - magR) / (magL + magR + eps)
    balance = np.clip(balance, -1.0, 1.0)

    az = np.arcsin(balance)
    az = np.clip(az, -np.pi / 2, np.pi / 2)

    for k in range(1, az.shape[1]):
        az[:, k] = ALPHA_AZ * az[:, k - 1] + (1 - ALPHA_AZ) * az[:, k]

    az_frame = np.sum(az * E, axis=0) / (np.sum(E, axis=0) + eps)
    az_frame = np.clip(az_frame, -np.pi / 2, np.pi / 2)

    hf_mask = f >= 3000.0
    if not np.any(hf_mask):
        hf_mask = f >= 0.5 * np.max(f)

    E_hf = E[hf_mask, :]
    coh_hf = np.sum(coh[hf_mask, :] * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps)
    del coh
    diffuse_hf = 1.0 - coh_hf
    diffuse_hf = np.clip(diffuse_hf, 0.0, 1.0)

    ild = (magL - magR) / (magL + magR + eps)
    del magL, magR
    gc.collect()

    ild_hf = np.sum(np.abs(ild[hf_mask, :]) * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps)
    del ild, E_hf
    ild_hf = np.clip(ild_hf, 0.0, 1.0)

    spectral_tilt = np.sum(E * f[:, None], axis=0) / (np.sum(E, axis=0) + eps)
    del E
    gc.collect()

    spectral_tilt = (
        spectral_tilt - np.min(spectral_tilt)
    ) / (
        np.max(spectral_tilt) - np.min(spectral_tilt) + eps
    )
    spectral_tilt = np.clip(spectral_tilt, 0.0, 1.0)

    z_conf = (
        0.4 * spectral_tilt +
        0.3 * diffuse_hf +
        0.3 * ild_hf
    )
    z_conf *= np.cos(az_frame)
    z_conf = np.clip(z_conf, 0.0, 1.0)
    z_conf = gaussian_filter1d(z_conf, sigma=2)

    el_frame = np.deg2rad(MAX_ELEV_DEG) * (z_conf ** 0.7)
    for k in range(1, len(el_frame)):
        el_frame[k] = ALPHA_EL * el_frame[k - 1] + (1 - ALPHA_EL) * el_frame[k]

    if len(el_frame) > 20:
        el_frame[:20] = el_frame[20]

    theta_z = np.sin(el_frame)[None, :]
    theta_h = np.cos(el_frame)[None, :]

    _, W = istft(M, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Z = istft(M * theta_z, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, X = istft(M * (theta_h * np.cos(az)), fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Y = istft(M * (theta_h * np.sin(az)), fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    del M, az
    gc.collect()

    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    return W[:N], X[:N], Y[:N], Z[:N]

def tetra_aformat_to_foa(audio4):
    audio4 = np.asarray(audio4, dtype=np.float32)
    if audio4.ndim != 2 or audio4.shape[1] < 4:
        raise ValueError("Se requieren al menos 4 canales en orden FLU, FRD, BLD, BRU.")

    M_tetra = 0.5 * np.array([
        [1.0,        1.0,        1.0,        1.0],
        [np.sqrt(3), np.sqrt(3), -np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), -np.sqrt(3), np.sqrt(3)],
    ], dtype=np.float32)

    WXYZ = audio4[:, :4] @ M_tetra.T
    W = WXYZ[:, 0]
    X = WXYZ[:, 1]
    Y = WXYZ[:, 2]
    Z = WXYZ[:, 3]
    return W, X, Y, Z

def foa_to_binaural(W, X, Y, Z, sr, hrtf, pos):
    N = min(len(W), len(X), len(Y), len(Z))
    W = np.asarray(W[:N], dtype=np.float32)
    X = np.asarray(X[:N], dtype=np.float32)
    Y = np.asarray(Y[:N], dtype=np.float32)
    Z = np.asarray(Z[:N], dtype=np.float32)

    outL = np.zeros(N + 512, dtype=np.float32)
    outR = np.zeros(N + 512, dtype=np.float32)

    for az_deg, el_deg, gain in VIRTUAL_SPEAKERS:
        az = np.deg2rad(az_deg)
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
        del spk, convL, convR

    gc.collect()
    N2 = min(len(outL), len(outR))
    binaural = np.stack([outL[:N2], outR[:N2]], axis=1)
    binaural /= np.max(np.abs(binaural)) + 1e-9
    return binaural

def foa_motion_preview(W, X, Y, Z, sr,
                       rate_az=0.12,
                       rate_el=0.10,
                       max_el_deg=60.0,
                       z_preview_gain=3.5):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    t = np.arange(N) / sr

    az = 2 * np.pi * rate_az * t
    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = np.sin(az) * X + np.cos(az) * Y

    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)

    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)

    W_3d = W
    Y_3d = Y_rot
    return W_3d, X_3d, Y_3d, Z_3d

def normalize_audio(x, peak_target=0.95):
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0:
        x = peak_target * x / peak
    return x

def stabilize_loudness(y, sr,
                       win_ms=450,
                       strength=0.55,
                       min_gain=0.88,
                       max_gain=2.0):
    eps = 1e-9
    y = np.asarray(y, dtype=np.float64)
    power = np.mean(y**2, axis=1)

    win = int(sr * win_ms / 1000)
    win = max(win, 1)

    kernel = np.ones(win) / win

    # Use fftconvolve to compute convolve efficiently
    env = np.sqrt(fftconvolve(power, kernel, mode="same") + eps)

    target = np.median(env) + eps
    gain = target / (env + eps)
    gain = gain ** strength
    gain = np.clip(gain, min_gain, max_gain)
    gain = fftconvolve(gain, kernel, mode="same")

    y_out = y * gain[:, None]
    return normalize_audio(y_out, peak_target=0.95)

# =========================================================
# PROCESAMIENTO PRINCIPAL
# =========================================================
def process_file(in_path, mode, out_folder, hrtf, pos):
    print(f"\n--- Procesando: {os.path.basename(in_path)} (Modo: {mode}) ---")
    t0 = time.time()

    raw_audio, sr = sf.read(in_path)
    audio = normalize_multichannel(raw_audio)

    if mode == "stereo":
        W, X, Y, Z = stereo_to_foa(audio[:, :2], sr)
    elif mode == "tetra":
        W, X, Y, Z = tetra_aformat_to_foa(audio[:, :4])
    else:
        raise ValueError(f"Modo desconocido: {mode}")

    # Normalizar FOA y ordenar en AmbiX [W, Y, Z, X]
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    foa = np.stack([W, Y, Z, X], axis=1)
    foa /= np.max(np.abs(foa)) + 1e-9

    foa_path = os.path.join(out_folder, "Notebook_output_foa.wav")
    sf.write(foa_path, foa, sr, subtype='PCM_16')
    print(f"  [+] Guardado FOA: {foa_path} ({foa.shape})")

    # Render Binaural Normal
    binaural = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos)
    binaural = normalize_audio(binaural, peak_target=0.95)

    bin_path = os.path.join(out_folder, "Notebook_output_binaural.wav")
    sf.write(bin_path, binaural, sr, subtype='PCM_16')
    print(f"  [+] Guardado Binaural: {bin_path} ({binaural.shape})")

    # Render Binaural 3D Perceptual
    W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(
        W, X, Y, Z, sr,
        rate_az=0.12,
        rate_el=0.10,
        max_el_deg=60.0,
        z_preview_gain=3.5
    )
    binaural_3d = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos)
    binaural_3d = 0.90 * binaural_3d + 0.10 * binaural
    binaural_3d = stabilize_loudness(
        binaural_3d,
        sr,
        win_ms=450,
        strength=0.55,
        min_gain=0.88,
        max_gain=2.0
    )

    perc_path = os.path.join(out_folder, "Notebook_output_binaural_3D_perceptual.wav")
    sf.write(perc_path, binaural_3d, sr, subtype='PCM_16')
    print(f"  [+] Guardado Perceptual: {perc_path} ({binaural_3d.shape})")

    elapsed = time.time() - t0
    print(f"  Completado en {elapsed:.2f} s")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    validation_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))
    software_dir = os.path.abspath(os.path.join(validation_dir, ".."))

    sofa_path = os.path.join(software_dir, "Web Site", "hrtf.sofa")
    if not os.path.exists(sofa_path):
        sofa_path = os.path.join(software_dir, "hrtf.sofa")
    print("Cargando HRTF desde:", sofa_path)
    hrtf, pos = load_sofa(sofa_path)

    audios_root = os.path.join(validation_dir, "audios_tests")

    # Lista de archivos a procesar: (subcarpeta_relativa, archivo_entrada, modo)
    tasks = [
        # 1. Banco Espacial Auxiliar: test_center, test_left, test_right, test_sweep
        (
            os.path.join("3. auxiliary_spatial_tests", "test_center"),
            "test_center.wav",
            "stereo"
        ),
        (
            os.path.join("3. auxiliary_spatial_tests", "test_left"),
            "test_left.wav",
            "stereo"
        ),
        (
            os.path.join("3. auxiliary_spatial_tests", "test_right"),
            "test_right.wav",
            "stereo"
        ),
        (
            os.path.join("3. auxiliary_spatial_tests", "test_sweep"),
            "test_sweep.wav",
            "stereo"
        ),
        # 2. Banco Studio 4_mic: todos los 14
        (
            os.path.join("2. studio_4mic", "DIR BLD"),
            "7.BLD.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR BLU"),
            "5.BLU.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR BRD"),
            "8.BRD.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR BRU"),
            "6.BRU.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR FLD"),
            "3.FLD.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR FLU"),
            "1.FLU.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR FRD"),
            "4.FRD.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "DIR FRU"),
            "2.FRU.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE +X"),
            "EJE +X.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE +Y"),
            "EJE +Y.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE +Z"),
            "EJE +Z.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE -X"),
            "EJE -X.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE -Y"),
            "EJE -Y.wav",
            "tetra"
        ),
        (
            os.path.join("2. studio_4mic", "EJE -Z"),
            "EJE -Z.wav",
            "tetra"
        ),
        # 3. Banco Estéreo: A07 (al final por ser el más largo)
        (
            os.path.join("1. stereo_tests", "A07_cancion_larga_10mins"),
            "A07_cancion_larga_10mins.wav",
            "stereo"
        ),
    ]

    print(f"\nTotal audios a procesar: {len(tasks)}")
    t_start = time.time()

    for idx, (subfolder, in_filename, mode) in enumerate(tasks, 1):
        target_dir = os.path.join(audios_root, subfolder)
        in_file = os.path.join(target_dir, in_filename)
        print(f"\n[{idx}/{len(tasks)}] Carpeta: {subfolder}")
        if not os.path.exists(in_file):
            print(f"  [!] ERROR: No existe {in_file}")
            continue

        foa_file = os.path.join(target_dir, "Notebook_output_foa.wav")
        bin_file = os.path.join(target_dir, "Notebook_output_binaural.wav")
        perc_file = os.path.join(target_dir, "Notebook_output_binaural_3D_perceptual.wav")

        if os.path.exists(foa_file) and os.path.exists(bin_file) and os.path.exists(perc_file) and len(sys.argv) <= 1:
            print(f"  [*] Ya procesado con éxito. Omitiendo...")
            continue

        process_file(in_file, mode, target_dir, hrtf, pos)

    total_time = time.time() - t_start
    print(f"\n=======================================================")
    print(f"PROCESAMIENTO FINALIZADO CON ÉXITO")
    print(f"Tiempo total: {total_time:.2f} s ({total_time/60:.2f} min)")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
