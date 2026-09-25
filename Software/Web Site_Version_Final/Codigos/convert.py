# =========================================================
# CONVERSIÓN A FOA DESDE:
#   1) AUDIO ESTÉREO (2 canales)
#   2) 4 MICRÓFONOS CARDIOIDES TETRAÉDRICOS (4 canales)
#
# Salidas:
#   - output_foa.wav        -> FOA en orden ambiX [W, Y, Z, X]
#   - output_binaural.wav   -> render binaural aproximado
#
# NOTA:
# - Modo estéreo: usa estimación 3D coherente con el análisis del libro
# - Modo 4 canales: usa matriz tetraédrica tipo FLU, FRD, BLD, BRU
# =========================================================

# Parameters
input_audio_path = ""
output_dir = ""
use_external_input = False
mode = "auto"

hrtf_path = ""

import subprocess
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

from scipy.signal import stft, istft, fftconvolve
from pysofaconventions import SOFAFile
try:
    from google.colab import files
except ImportError:
    files = None
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import os
import subprocess
import soundfile as sf
try:
    from google.colab import files
except ImportError:
    files = None

def upload_and_load_audio():
    if files is None:
        raise RuntimeError('No google.colab package available y no se provee input_audio_path.')
    uploaded = files.upload()
    audio_file = list(uploaded.keys())[0]

    if audio_file.lower().endswith(".mp3"):
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", audio_file,
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "converted.wav"
        ], check=True)
        audio_file = "converted.wav"

    audio, sr = sf.read(audio_file)
    return audio, sr, audio_file

def load_audio_entry():
    if use_external_input and input_audio_path:
        audio_file = input_audio_path

        if audio_file.lower().endswith(".mp3"):
            converted = os.path.join(output_dir if output_dir else ".", "converted_input.wav")
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "quiet",
                "-i", audio_file,
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                converted
            ], check=True)
            audio_file = converted

        audio, sr = sf.read(audio_file)
        return audio, sr, audio_file
    else:
        return upload_and_load_audio()

def out_path(name):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, name)
    return name


# =========================================================
# PARÁMETROS GENERALES
# =========================================================
SHOW_PLOTS = True
DB_MIN = -80
DB_MAX = 0
N_FFT = 2048  #tamaño del análisis en frecuencia
HOP = N_FFT // 4 #cuanto se mueve la ventana Overlap = N_FFT - HOP
FREQ_PLOT_MAX_DEFAULT = 12000

# Parámetros del modo estéreo -> FOA
MAX_ELEV_DEG = 45.0 #elevación máxima, conservador, realista, evita errores grandes
ALPHA_AZ = 0.20 #filtros de suavizado
ALPHA_EL = 0.85
X_GAIN = 0.90
Y_GAIN = 0.90
Z_GAIN = 0.80

# Render binaural desde FOA
VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),   # frente
    (60.0,   0.0, 0.90),   # izquierda-frente
    (-60.0,  0.0, 0.90),   # derecha-frente
    (180.0,  0.0, 0.55),   # atrás
    (0.0,   55.0, 0.80),   # arriba más perceptible
    (0.0,  -45.0, 0.35),   # abajo
]


def normalize_multichannel(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float64)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    return 0.95 * audio / peak

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def rms(x): #energía promedio
    return np.sqrt(np.mean(x**2) + 1e-12)

def db_mag(x): #convierte a decibeles
    return 20 * np.log10(np.abs(x) + 1e-12)

def time_axis(x, sr):
    return np.arange(len(x)) / sr #sampling rate (cuantas muestras hay por segundo) arange.. valores en orden

def smooth1d(y, win=9): #suaviza señales (10+50+10)/3 = 23 .. ángulo posición 1 →[10, 12, 11, 50, 10, 12] (10+12+11)/3 = 11  posición 2 → (12+11+50)/3 = 24
    y = np.asarray(y, dtype=float) #asarray convierte en array
    if win < 2 or len(y) < win:
        return y.copy() #devuelve la señal tal cual
    if win % 2 == 0:
        win += 1
    k = np.ones(win) / win #crea promedio
    pad = win // 2
    ypad = np.pad(y, (pad, pad), mode="edge")
    return np.convolve(ypad, k, mode="valid") #solo multiplica y suma

def wrap_deg(x):
    return ((x + 180) % 360) - 180

def wrap_rad(x):
    return ((x + np.pi) % (2*np.pi)) - np.pi


# =========================================================
# FUNCIONES DE PLOT
# =========================================================
def plot_waveforms_stereo(L, R, sr, title):
    tt = time_axis(L, sr)
    plt.figure(figsize=(14, 4))
    plt.plot(tt, L, label="L", alpha=0.8)
    plt.plot(tt, R, label="R", alpha=0.8)
    plt.title(title)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_curve(t, y, title, ylabel):
    plt.figure(figsize=(14, 4))
    plt.plot(t, y)
    plt.title(title)
    plt.xlabel("Tiempo (s)")
    plt.ylabel(ylabel)
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_pair_spectrograms(f, t, Z1, Z2, title1, title2, fmax):
    idx = f <= fmax
    f2 = f[idx]
    Z1 = Z1[idx, :]
    Z2 = Z2[idx, :]

    Z1db = np.clip(db_mag(Z1), DB_MIN, DB_MAX)
    Z2db = np.clip(db_mag(Z2), DB_MIN, DB_MAX)

    fig, axs = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    pcm1 = axs[0].pcolormesh(t, f2, Z1db, shading="auto", cmap="magma", vmin=DB_MIN, vmax=DB_MAX)
    axs[0].set_title(title1)
    axs[0].set_ylabel("Frecuencia (Hz)")

    pcm2 = axs[1].pcolormesh(t, f2, Z2db, shading="auto", cmap="magma", vmin=DB_MIN, vmax=DB_MAX)
    axs[1].set_title(title2)
    axs[1].set_xlabel("Tiempo (s)")
    axs[1].set_ylabel("Frecuencia (Hz)")

    fig.colorbar(pcm1, ax=axs[0], label="dB")
    fig.colorbar(pcm2, ax=axs[1], label="dB")
    plt.tight_layout()
    plt.show()

def plot_foa_channels(W, X, Y, Z, sr, title):
    tt = time_axis(W, sr)
    fig, axs = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    axs[0].plot(tt, W); axs[0].set_title("W"); axs[0].grid()
    axs[1].plot(tt, X); axs[1].set_title("X"); axs[1].grid()
    axs[2].plot(tt, Y); axs[2].set_title("Y"); axs[2].grid()
    axs[3].plot(tt, Z); axs[3].set_title("Z"); axs[3].grid()
    axs[3].set_xlabel("Tiempo (s)")
    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_spectrogram_3d(signal, sr, title, fmax=None,
                        n_fft=N_FFT, hop=HOP,
                        stride_t=2, stride_f=2, cmap="magma"):
    """
    Espectrograma 3D con ejes:
    - Tiempo (s)
    - Frecuencia (Hz)
    - Potencia (dB)
    """
    f, t, Z = stft(signal, fs=sr, nperseg=n_fft, noverlap=n_fft - hop)

    if fmax is None:
        fmax = min(FREQ_PLOT_MAX_DEFAULT, sr / 2)

    idx = f <= fmax
    f = f[idx][::stride_f]
    t = t[::stride_t]

    S_pow = np.abs(Z[idx, :]) ** 2
    S_db = 10 * np.log10(S_pow + 1e-12)
    S_db = np.clip(S_db, DB_MIN, DB_MAX)
    S_db = S_db[::stride_f, ::stride_t]

    T, F = np.meshgrid(t, f)

    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(T, F, S_db, cmap=cmap, linewidth=0, antialiased=True)

    ax.set_title(title)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Frecuencia (Hz)")
    ax.set_zlabel("Potencia (dB)")
    ax.view_init(elev=28, azim=-135)

    fig.colorbar(surf, ax=ax, shrink=0.65, pad=0.10, label="dB")
    plt.tight_layout()
    plt.show()


def frame_signal(x, frame_size=N_FFT, hop=HOP):
    x = np.asarray(x, dtype=np.float64).flatten()
    if len(x) < frame_size:
        x = np.pad(x, (0, frame_size - len(x)))

    n_frames = 1 + (len(x) - frame_size) // hop
    idx = np.arange(frame_size)[None, :] + hop * np.arange(n_frames)[:, None]
    return x[idx]

def foa_direction_statistics(W, X, Y, Z, sr, frame_size=N_FFT, hop=HOP):
    """
    Dirección dominante por trama usando un vector energético
    tipo intensidad activa simplificada: [<W*X>, <W*Y>, <W*Z>].
    """
    Wf = frame_signal(W, frame_size, hop)
    Xf = frame_signal(X, frame_size, hop)
    Yf = frame_signal(Y, frame_size, hop)
    Zf = frame_signal(Z, frame_size, hop)

    Ix = np.mean(Wf * Xf, axis=1)
    Iy = np.mean(Wf * Yf, axis=1)
    Iz = np.mean(Wf * Zf, axis=1)

    energy = np.mean(Wf**2 + Xf**2 + Yf**2 + Zf**2, axis=1)

    vec_frames = np.stack([Ix, Iy, Iz], axis=1)
    norms = np.linalg.norm(vec_frames, axis=1, keepdims=True) + 1e-12
    unit_frames = vec_frames / norms

    weights = energy / (np.sum(energy) + 1e-12)
    mean_vec = np.sum(unit_frames * weights[:, None], axis=0)
    mean_vec /= np.linalg.norm(mean_vec) + 1e-12

    az_deg = np.rad2deg(np.arctan2(unit_frames[:, 1], unit_frames[:, 0]))
    el_deg = np.rad2deg(np.arctan2(
        unit_frames[:, 2],
        np.sqrt(unit_frames[:, 0]**2 + unit_frames[:, 1]**2) + 1e-12
    ))
    t_frames = (np.arange(len(az_deg)) * hop + frame_size / 2) / sr

    return {
        "t": t_frames,
        "az_deg": az_deg,
        "el_deg": el_deg,
        "energy": energy,
        "mean_vec": mean_vec,
        "mean_az_deg": float(np.rad2deg(np.arctan2(mean_vec[1], mean_vec[0]))),
        "mean_el_deg": float(np.rad2deg(np.arctan2(
            mean_vec[2],
            np.sqrt(mean_vec[0]**2 + mean_vec[1]**2) + 1e-12
        ))),
    }

def _draw_wire_cube(ax, half=1.0, color="gray", alpha=0.12):
    v = np.array([
        [-half, -half, -half],
        [ half, -half, -half],
        [ half,  half, -half],
        [-half,  half, -half],
        [-half, -half,  half],
        [ half, -half,  half],
        [ half,  half,  half],
        [-half,  half,  half],
    ])

    edges = [
        (0,1),(1,2),(2,3),(3,0),
        (4,5),(5,6),(6,7),(7,4),
        (0,4),(1,5),(2,6),(3,7)
    ]
    for i, j in edges:
        ax.plot(*zip(v[i], v[j]), color=color, alpha=0.45, linewidth=1)

    faces_idx = [
        (0,1,2,3),(4,5,6,7),(0,1,5,4),
        (2,3,7,6),(1,2,6,5),(0,3,7,4)
    ]
    faces = [[v[k] for k in face] for face in faces_idx]
    ax.add_collection3d(
        Poly3DCollection(faces, facecolors=color, edgecolors="none", alpha=alpha)
    )

def plot_spatial_direction_head(stats, title="Dirección espacial dominante", show_trajectory=True):
    mean_vec = np.asarray(stats["mean_vec"], dtype=float)
    mean_vec = mean_vec / (np.linalg.norm(mean_vec) + 1e-12)

    fig = plt.figure(figsize=(10, 9))
    ax = fig.add_subplot(111, projection="3d")

    _draw_wire_cube(ax, half=1.0)

    # cabeza simplificada
    u = np.linspace(0, 2*np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    r = 0.18
    xs = r * np.outer(np.cos(u), np.sin(v))
    ys = r * np.outer(np.sin(u), np.sin(v))
    zs = r * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(xs, ys, zs, alpha=0.25, linewidth=0)

    # ejes Ambisonics
    ax.quiver(0, 0, 0, 1.25, 0, 0, arrow_length_ratio=0.10, linewidth=2)
    ax.quiver(0, 0, 0, 0, 1.25, 0, arrow_length_ratio=0.10, linewidth=2)
    ax.quiver(0, 0, 0, 0, 0, 1.25, arrow_length_ratio=0.10, linewidth=2)

    ax.text( 1.32, 0.00, 0.00, "+X frente", fontsize=10)
    ax.text(-1.35, 0.00, 0.00, "-X atrás", fontsize=10)
    ax.text( 0.00, 1.32, 0.00, "+Y izquierda", fontsize=10)
    ax.text( 0.00,-1.42, 0.00, "-Y derecha", fontsize=10)
    ax.text( 0.00, 0.00, 1.32, "+Z arriba", fontsize=10)
    ax.text( 0.00, 0.00,-1.42, "-Z abajo", fontsize=10)

    # vértices tetraédricos
    tetra = {
        "FLU": np.array([ 1,  1,  1]) / np.sqrt(3),
        "FRD": np.array([ 1, -1, -1]) / np.sqrt(3),
        "BLD": np.array([-1,  1, -1]) / np.sqrt(3),
        "BRU": np.array([-1, -1,  1]) / np.sqrt(3),
    }
    for lab, vec in tetra.items():
        ax.scatter(*vec, s=35)
        ax.text(*(1.08 * vec), lab, fontsize=10)

    # trayectoria temporal opcional
    if show_trajectory and "az_deg" in stats and "el_deg" in stats:
        az = np.deg2rad(stats["az_deg"])
        el = np.deg2rad(stats["el_deg"])
        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)
        ax.scatter(x, y, z, s=5, alpha=0.15)

    # flecha promedio dominante
    ax.quiver(0, 0, 0, *(1.15 * mean_vec), arrow_length_ratio=0.12, linewidth=3)
    ax.text(
        *(1.23 * mean_vec),
        f"Promedio\\naz={stats['mean_az_deg']:.1f}°\\nel={stats['mean_el_deg']:.1f}°",
        fontsize=10
    )

    ax.set_title(title)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_zlim(-1.4, 1.4)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=22, azim=-55)

    plt.tight_layout()
    plt.show()

 # =========================================================
# DECODIFICADOR FOA -> 4 PARLANTES
# Dos modos:
# 1) horizontal: [Frente, Izquierda, Atrás, Derecha]
# 2) altura:     [Frente, Izquierda, Derecha, Arriba]
# =========================================================

def foa_to_4_speakers(W, X, Y, Z, layout="horizontal", sharpen=True):
    """
    Decodifica FOA W, X, Y, Z a 4 parlantes.

    layout="horizontal":
        Canal 0 = Frente
        Canal 1 = Izquierda
        Canal 2 = Atrás
        Canal 3 = Derecha

    layout="altura":
        Canal 0 = Frente
        Canal 1 = Izquierda
        Canal 2 = Derecha
        Canal 3 = Arriba

    Convención:
        +X = frente
        +Y = izquierda
        +Z = arriba
    """

    # Esto solo es para hacer más clara la direccionalidad en la demostración.
    # No modifica el archivo FOA original.
    if sharpen:
        W_use = W / np.sqrt(3)
    else:
        W_use = W

    if layout == "horizontal":
        F = 0.5 * (W_use + X)   # Frente
        L = 0.5 * (W_use + Y)   # Izquierda
        B = 0.5 * (W_use - X)   # Atrás
        R = 0.5 * (W_use - Y)   # Derecha

        speakers4 = np.stack([F, L, B, R], axis=1)

    elif layout == "altura":
        F = 0.5 * (W_use + X)   # Frente
        L = 0.5 * (W_use + Y)   # Izquierda
        R = 0.5 * (W_use - Y)   # Derecha
        T = 0.5 * (W_use + Z)   # Arriba

        speakers4 = np.stack([F, L, R, T], axis=1)

    else:
        raise ValueError("layout debe ser 'horizontal' o 'altura'.")

    # Normalización para evitar saturación
    peak = np.max(np.abs(speakers4)) + 1e-9
    if peak > 0.99:
        speakers4 = 0.99 * speakers4 / peak

    return speakers4

# =========================================================
# HRTF
# =========================================================
def load_sofa(path): #formato estándar para guardar: htrf, posiciones espaciale, respuestas impulsionales, cómo escucha la cabeza humana desde muchas direcciones
    s = SOFAFile(path, 'r') #r : leer, no modificar, abre el archivo SOFA
    ir = s.getDataIR() #impulse Response: cómo responde el oído a un sonido desde cierta dirección - ir[posición, oído, muestras]
    ''' oído
            L        R
pos 0   [1 2 3]  [4 5 6]

pos 1   [7 8 9]  [10 11 12]

pos 2   [13 14 15] [16 17 18]'''

    pos = s.getVariableValue('SourcePosition') #búscame una variable dentro del archivo SOFA - Las direcciones donde fueron medidas las HRTFs - [azimut, elevación, distancia]
    return ir, pos

def get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4): #compara con posiciones reales,busca las más cercanas, hace promedio - función recibe un ángulo deseado
    az_deg = wrap_deg(az_deg)

    az_all = wrap_deg(pos[:, 0]) #toma TODOS los azimuts del SOFA y los normaliza
    el_all = pos[:, 1]

    az_diff = np.abs(wrap_deg(az_all - az_deg)) #diferencia entre ángulo real y ángulo deseado - distancia angular horizontal - qué tan cerca está cada HRTF -pequeña diferencia = buena HRTF candidata
    el_diff = np.abs(el_all - el_deg)

    dist = np.sqrt((az_diff / 180.0)**2 + (el_diff / 90.0)**2) #calcula distancia espacial aproximada - pitágoras - qué tan lejos está cada HRTF de la dirección deseada
    idx = np.argsort(dist)[:k] #ordena índices de menor a mayor - es un vector de índices - tomar los primeros k elementos

    w = 1.0 / (dist[idx] + 1e-6) #crea pesos- HRTF más cercana = más importante.
    w /= np.sum(w) #normaliza pesos - w = w / suma_total

    hL = np.sum(hrtf[idx, 0, :] * w[:, None], axis=0)  #Hace la interpolación - las HRTFs izquierdas más cercanas, none pasa de fila a columna para poder multiplicar fila a fila - Porque las dimensiones no coinciden bien para broadcasting.
    hR = np.sum(hrtf[idx, 1, :] * w[:, None], axis=0)

    return hL, hR #filtro izquierdo final, filtro derecho final


# =========================================================
# CARGA DE HRTF (INYECTADO)
# =========================================================
hrtf, pos = load_sofa(globals().get("hrtf_path", "hrtf.sofa"))
print("HRTF cargado correctamente.")

# =========================================================
# MODO 1: ESTÉREO -> FOA 3D ESTIMADO
# Salida compatible con AmbiX ACN/SN3D
# =========================================================

from scipy.ndimage import gaussian_filter1d

def stereo_to_foa(audio_stereo, sr):
    """
    Convierte audio estéreo L/R a una representación FOA 3D estimada.

    Importante:
    - El audio estéreo original NO es ambisónico.
    - El código estima una dirección espacial a partir de balance L/R,
      coherencia, difusión, ILD y contenido en altas frecuencias.
    - La salida se construye como FOA compatible con AmbiX ACN/SN3D.
    """

    # -----------------------------
    # SEPARAR CANALES
    # -----------------------------
    audio_stereo = np.asarray(audio_stereo, dtype=np.float64)

    if audio_stereo.ndim != 2 or audio_stereo.shape[1] < 2:
        raise ValueError("El modo estéreo requiere un audio de mínimo 2 canales: L y R.")

    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]

    # -----------------------------
    # STFT
    # -----------------------------
    f, t, ZL = stft(L, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, _, ZR = stft(R, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)

    eps = 1e-12
    magL = np.abs(ZL)
    magR = np.abs(ZR)

    # Mid / Side
    M = (ZL + ZR) / 2.0
    S = (ZL - ZR) / 2.0

    # Energía base
    E = np.abs(M) ** 2

    # =====================================================
    # AZIMUT ESTIMADO
    # =====================================================
    balance = (magL - magR) / (magL + magR + eps)
    balance = np.clip(balance, -1.0, 1.0)

    az = np.arcsin(balance)
    az = np.clip(az, -np.pi / 2, np.pi / 2)

    # Suavizado temporal del azimut por frecuencia
    for k in range(1, az.shape[1]):
        az[:, k] = ALPHA_AZ * az[:, k - 1] + (1 - ALPHA_AZ) * az[:, k]

    # Azimut promedio por trama, ponderado por energía
    az_frame = np.sum(az * E, axis=0) / (np.sum(E, axis=0) + eps)
    az_frame = np.clip(az_frame, -np.pi / 2, np.pi / 2)

    # =====================================================
    # ELEVACIÓN MEJORADA
    # =====================================================

    # Coherencia intercanal, qué tan parecidos son L y R
    coh = np.abs(ZL * np.conj(ZR)) / (magL * magR + eps)
    coh = np.clip(coh, 0.0, 1.0)

    # Frecuencias altas para estimación vertical, f Vector de frecuencias del STFT.
    hf_mask = f >= 3000.0

    # Seguridad por si el audio tiene frecuencia de muestreo baja
    if not np.any(hf_mask):
        hf_mask = f >= 0.5 * np.max(f)

    E_hf = E[hf_mask, :] #todas las frecuencias altas, para todos los tiempos

    # Difusión en altas frecuencias
    coh_hf = np.sum(coh[hf_mask, :] * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps) #qué tan parecidos son los agudos importantes
    diffuse_hf = 1.0 - coh_hf
    diffuse_hf = np.clip(diffuse_hf, 0.0, 1.0)

    # ILD en altas frecuencias, diferencia de volumen entre oídos, Interaural Level Difference, El cerebro usa eso para dirección.
    ild = (magL - magR) / (magL + magR + eps)
    ild_hf = np.sum(np.abs(ild[hf_mask, :]) * E_hf, axis=0) / (np.sum(E_hf, axis=0) + eps) #qué tan lateralizados están los agudos
    ild_hf = np.clip(ild_hf, 0.0, 1.0)

    # Tilt espectral / centroide normalizado, dónde está concentrada la energía, grave - bajo, agudo - alto
    spectral_tilt = np.sum(E * f[:, None], axis=0) / (np.sum(E, axis=0) + eps)
    spectral_tilt = (
        spectral_tilt - np.min(spectral_tilt)
    ) / (
        np.max(spectral_tilt) - np.min(spectral_tilt) + eps
    )
    spectral_tilt = np.clip(spectral_tilt, 0.0, 1.0)

    # Confianza vertical, voy a inventarme una probabilidad de que el sonido esté arriba
    z_conf = (
        0.4 * spectral_tilt +
        0.3 * diffuse_hf +
        0.3 * ild_hf
    )

    # Reducir elevación cuando el sonido está muy lateralizado
    z_conf *= np.cos(az_frame)

    # Asegurar rango válido
    z_conf = np.clip(z_conf, 0.0, 1.0)

    # Suavizado de la confianza vertical, quita cambios bruscos, sigma controla cuánto suaviza.
    z_conf = gaussian_filter1d(z_conf, sigma=2)

    # Elevación final por trama,            Potencia
    el_frame = np.deg2rad(MAX_ELEV_DEG) * (z_conf ** 0.7) #para exagerar un poco, elevación humana es poco sensible.

    # Suavizado temporal de elevación, no cambies elevación bruscament
    for k in range(1, len(el_frame)):
        el_frame[k] = ALPHA_EL * el_frame[k - 1] + (1 - ALPHA_EL) * el_frame[k]

    # Evitar artefactos iniciales, Infinite Impulse Response, ELEGIR VALOR ESTABLE
    if len(el_frame) > 20:
        el_frame[:20] = el_frame[20]

    # Expandir elevación a todos los bits de frecuencia
    el = np.tile(el_frame[None, :], (len(f), 1))

    # =====================================================
    # VECTOR DIRECCIÓN 3D
    # Convención:
    # +X = frente
    # +Y = izquierda
    # +Z = arriba
    # ángulos → coordenadas 3D
    # =====================================================
    theta_z = np.sin(el)
    theta_h = np.cos(el)
    theta_x = theta_h * np.cos(az)
    theta_y = theta_h * np.sin(az)

    # =====================================================
    # CONSTRUCCIÓN FOA - BASE AmbiX ACN/SN3D
    # =====================================================
    # En SN3D de primer orden:
    # W = señal omnidireccional
    # X = señal * componente frontal/trasera
    # Y = señal * componente izquierda/derecha
    # Z = señal * componente arriba/abajo
    #
    # Aquí NO se usa M/sqrt(2), ni X_GAIN, Y_GAIN, Z_GAIN,
    # para no alterar la normalización relativa SN3D.

    W_tf = M
    X_tf = M * theta_x
    Y_tf = M * theta_y
    Z_tf = M * theta_z

    # =====================================================
    # VOLVER AL DOMINIO DEL TIEMPO
    # =====================================================
    _, W = istft(W_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, X = istft(X_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Y = istft(Y_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)
    _, Z = istft(Z_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - HOP)

    # Igualar longitudes (Por el solapamiento de ventanas la ISTFT puede devolver
    # arrays con longitudes ligeramente diferentes. Esta parte simplemente los
    # recorta todos al mismo tamaño para que puedan empacarse juntos sin problemas.)
    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    diagnostics = {
        "f": f,
        "t": t,
        "ZL": ZL,
        "ZR": ZR,
        "M": M,
        "S": S,
        "az_frame_deg": smooth1d(np.rad2deg(az_frame), 9),
        "el_frame_deg": smooth1d(np.rad2deg(el_frame), 11),
        "z_conf": z_conf,
        "normalization": "AmbiX ACN/SN3D compatible",
        "input_mode": "stereo_to_estimated_foa"
    }

    return W, X, Y, Z, diagnostics

# =========================================================
# MODO 2: 4 MICRÓFONOS TETRAÉDRICOS -> FOA 3D
# Salida compatible con AmbiX ACN/SN3D
# =========================================================

def tetra_aformat_to_foa(audio4):
    """
    Convierte A-format tetraédrico idealizado a FOA 3D.

    Orden esperado de entrada:
    canal 0 = FLU
    canal 1 = FRD
    canal 2 = BLD
    canal 3 = BRU

    Salida interna:
    W, X, Y, Z

    Luego, al guardar, se debe ordenar como AmbiX/ACN:
    [W, Y, Z, X]
    """

    audio4 = np.asarray(audio4, dtype=np.float64)

    if audio4.ndim != 2 or audio4.shape[1] < 4:
        raise ValueError("Se requieren 4 canales en orden FLU, FRD, BLD, BRU.")

    # Matriz tetraédrica compatible con FOA/SN3D
    M_tetra = 0.5 * np.array([
        [1.0,        1.0,        1.0,        1.0],
        [np.sqrt(3), np.sqrt(3), -np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), np.sqrt(3), -np.sqrt(3)],
        [np.sqrt(3), -np.sqrt(3), -np.sqrt(3), np.sqrt(3)],
    ], dtype=np.float64)

    WXYZ = audio4[:, :4] @ M_tetra.T

    W = WXYZ[:, 0]
    X = WXYZ[:, 1]
    Y = WXYZ[:, 2]
    Z = WXYZ[:, 3]

    diagnostics = {
        "encoder_matrix": M_tetra,
        "normalization": "AmbiX ACN/SN3D compatible",
        "input_mode": "tetra_aformat_to_foa",
        "channel_order_input": "FLU, FRD, BLD, BRU",
        "channel_order_internal": "W, X, Y, Z"
    }

    return W, X, Y, Z, diagnostics

# =========================================================
# FOA -> BINAURAL
# usando decodificación a altavoces virtuales + HRTF
# =========================================================
def foa_to_binaural(W, X, Y, Z, sr, hrtf, pos):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    outL = np.zeros(N + 512)
    outR = np.zeros(N + 512)

    for az_deg, el_deg, gain in VIRTUAL_SPEAKERS:
        az = np.deg2rad(az_deg)
        el = np.deg2rad(el_deg)

        # vector dirección del altavoz virtual
        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)

        # feed FOA -> altavoz virtual
        spk = gain * ((W / np.sqrt(2)) + x * X + y * Y + z * Z)

        hL, hR = get_hrtf_interp(az_deg, el_deg, hrtf, pos, k=4)

        convL = fftconvolve(spk, hL, mode="full")
        convR = fftconvolve(spk, hR, mode="full")

        outL[:len(convL)] += convL
        outR[:len(convR)] += convR

    N2 = min(len(outL), len(outR))
    binaural = np.stack([outL[:N2], outR[:N2]], axis=1)

    binaural /= np.max(np.abs(binaural)) + 1e-9
    return binaural

# =========================================================
# PREVISUALIZACIÓN 3D EN DOMINIO AMBISÓNICO
# Movimiento aplicado sobre W, X, Y, Z
# =========================================================

def foa_motion_preview(W, X, Y, Z, sr,
                       rate_az=0.12,
                       rate_el=0.09,
                       max_el_deg=58.0,
                       z_preview_gain=3):
    """
    Genera una versión perceptual con movimiento 3D a partir del FOA.

    Esta función NO reemplaza el FOA limpio.
    No trabaja directamente sobre L/R como un efecto 8D estéreo.
    Trabaja sobre los canales ambisónicos W, X, Y, Z.

    W = componente omnidireccional
    X = frente / atrás
    Y = izquierda / derecha
    Z = arriba / abajo
    """

    N = min(len(W), len(X), len(Y), len(Z))

    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    t = np.arange(N) / sr

    # -----------------------------------------------------
    # Movimiento horizontal alrededor del oyente
    # -----------------------------------------------------
    az = 2 * np.pi * rate_az * t

    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = np.sin(az) * X + np.cos(az) * Y

    # -----------------------------------------------------
    # Movimiento vertical suave
    # -----------------------------------------------------
    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)

    # Mezcla entre eje frontal X y eje vertical Z.
    # Esto hace más perceptible la altura en la escucha.
    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)

    # W no se rota porque es omnidireccional
    W_3d = W
    Y_3d = Y_rot

    return W_3d, X_3d, Y_3d, Z_3d


def normalize_audio(x, peak_target=0.95):
    """
    Normaliza un audio para evitar saturación.
    Esto NO es normalización SN3D.
    Solo ajusta volumen para escucha.
    """

    peak = np.max(np.abs(x)) + 1e-9

    if peak > 0:
        x = peak_target * x / peak

    return x

# =========================================================
# ESTABILIZAR VOLUMEN SIN MATAR EL EFECTO 3D
# =========================================================

def stabilize_loudness(y, sr,
                       win_ms=300,
                       strength=0.55,
                       min_gain=0.80,
                       max_gain=1.25):
    """
    Reduce bajones fuertes de volumen en el binaural 3D.

    No modifica el FOA limpio.
    No elimina el movimiento espacial.
    Solo compensa suavemente las partes donde el audio cae mucho.
    """

    eps = 1e-9

    y = np.asarray(y, dtype=np.float64)

    # Energía promedio entre L y R
    power = np.mean(y**2, axis=1)

    # Ventana de suavizado
    win = int(sr * win_ms / 1000)
    win = max(win, 1)

    kernel = np.ones(win) / win

    # Envolvente RMS
    env = np.sqrt(np.convolve(power, kernel, mode="same") + eps)

    # Nivel objetivo: mediana de la envolvente
    target = np.median(env) + eps

    # Ganancia correctiva
    gain = target / (env + eps)

    # Suavizar para que no bombee
    gain = gain ** strength

    # Evitar que suba o baje demasiado
    gain = np.clip(gain, min_gain, max_gain)

    # Suavizado final de ganancia
    gain = np.convolve(gain, kernel, mode="same")

    y_out = y * gain[:, None]

    return normalize_audio(y_out, peak_target=0.95)

audio, sr, audio_file = load_audio_entry()
audio = normalize_multichannel(audio)

if audio.ndim == 1:
    audio = audio[:, None]

num_ch = audio.shape[1]
print(f"Archivo cargado: {audio_file}")
print(f"Frecuencia de muestreo: {sr}")
print(f"Número de canales detectados: {num_ch}")

# =========================================================
# SELECCIÓN DE MODO
# =========================================================

if use_external_input:
    # En backend/web no se pide input manual
    if 'mode' in globals() and mode in ["stereo", "tetra_4mic"]:
        print(f"Modo recibido de backend: {mode}")
    else:
        if num_ch >= 4:
            mode = "tetra_4mic"
        elif num_ch == 2:
            mode = "stereo"
        else:
            raise ValueError("Se requiere un archivo estéreo (2 canales) o tetra (4 canales).")

    print(f"\nModo final usado automáticamente: {mode}")

else:
    print("\n===== SELECCIÓN DE MODO =====")
    print("1 -> auto")
    print("2 -> stereo")
    print("3 -> tetra_4mic")

    mode_input = input("Elige modo [auto/stereo/tetra_4mic] (Enter = auto): ").strip().lower()
    if mode_input == "":
        mode_input = "auto"

    if mode_input not in ["auto", "stereo", "tetra_4mic"]:
        print("Modo no válido. Se usará 'auto'.")
        mode_input = "auto"

    if mode_input == "auto":
        if num_ch >= 4:
            mode = "tetra_4mic"
        elif num_ch == 2:
            mode = "stereo"
        else:
            raise ValueError("Se requiere un archivo estéreo (2 canales) o tetra (4 canales).")
    else:
        mode = mode_input

    print(f"\nModo final usado: {mode}")


# =========================================================
# EJECUTAR CONVERSIÓN SEGÚN EL MODO
# =========================================================
if mode == "stereo":
    W, X, Y, Z, diagnostics = stereo_to_foa(audio, sr)
elif mode == "tetra_4mic":
    W, X, Y, Z, diagnostics = tetra_aformat_to_foa(audio)
else:
    raise ValueError(f"Modo no reconocido: {mode}")


# =========================================================
# NORMALIZAR FOA Y EMPACAR EN AMBIX [W, Y, Z, X]
# =========================================================
N = min(len(W), len(X), len(Y), len(Z))
W = W[:N]
X = X[:N]
Y = Y[:N]
Z = Z[:N]

foa = np.stack([W, Y, Z, X], axis=1)
foa /= np.max(np.abs(foa)) + 1e-9

print("\n===== VALIDACIÓN FOA =====")
print("Shape FOA:", foa.shape)
print(f"RMS W: {rms(W):.6f}")
print(f"RMS X: {rms(X):.6f}")
print(f"RMS Y: {rms(Y):.6f}")
print(f"RMS Z: {rms(Z):.6f}")

# =========================================================
# RENDER BINAURAL
# =========================================================

# ---------------------------------------------------------
# 1) Binaural normal desde el FOA limpio
# ---------------------------------------------------------
# Este render usa W, X, Y, Z directamente con HRTF.
# No agrega movimiento extra.

binaural = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos)
binaural = normalize_audio(binaural, peak_target=0.95)


# ---------------------------------------------------------
# 2) Binaural 3D perceptual con movimiento ambisónico
# ---------------------------------------------------------
# Aquí NO se modifica el FOA limpio.
# Se crea una copia W_3d, X_3d, Y_3d, Z_3d con movimiento espacial.
# Esto se hace para que el efecto 3D sea más notorio en audífonos.

W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(
    W, X, Y, Z, sr,
    rate_az=0.08,       # velocidad del giro horizontal
    rate_el=0.10,       # velocidad del movimiento vertical
    max_el_deg=60.0,    # elevación máxima perceptual
    z_preview_gain=3.5 # refuerzo de Z solo para escucha perceptual
)

binaural_3d = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos)

# Mezcla pequeña con el binaural normal para conservar cuerpo
# y evitar que el sonido desaparezca en algunas posiciones.
binaural_3d = 0.90 * binaural_3d + 0.10 * binaural

# Estabilizar volumen sin quitar el movimiento 3D
binaural_3d = stabilize_loudness(
    binaural_3d,
    sr,
    win_ms=450,
    strength=0.55,
    min_gain=0.88,
    max_gain=2
)

# ---------------------------------------------------------
# 3) Validación básica
# ---------------------------------------------------------

ild_out = 20 * np.log10(
    (rms(binaural[:, 0]) + 1e-12) /
    (rms(binaural[:, 1]) + 1e-12)
)

ild_3d = 20 * np.log10(
    (rms(binaural_3d[:, 0]) + 1e-12) /
    (rms(binaural_3d[:, 1]) + 1e-12)
)

print("\n===== VALIDACIÓN BINAURAL NORMAL =====")
print(f"RMS L salida: {rms(binaural[:,0]):.6f}")
print(f"RMS R salida: {rms(binaural[:,1]):.6f}")
print(f"ILD salida  : {ild_out:.2f} dB")

print("\n===== VALIDACIÓN BINAURAL 3D PERCEPTUAL =====")
print(f"RMS L salida 3D: {rms(binaural_3d[:,0]):.6f}")
print(f"RMS R salida 3D: {rms(binaural_3d[:,1]):.6f}")
print(f"ILD salida 3D  : {ild_3d:.2f} dB")
print("Se generó una versión con movimiento espacial aplicado sobre W, X, Y, Z.")

from IPython.display import Audio
from IPython.display import HTML, display
import base64
import os

# =========================================================
# GUARDAR RESULTADOS
# =========================================================

# ---------------------------------------------------------
# RUTAS DE SALIDA
# ---------------------------------------------------------
foa_wav_path = out_path("output_foa.wav")
binaural_wav_path = out_path("output_binaural.wav")
binaural_mp3_path = out_path("output_binaural.mp3")
perceptual_wav_path = out_path("output_binaural_3D_perceptual.wav")
perceptual_mp3_path = out_path("output_binaural_3D_perceptual.mp3")

spk_horizontal_path = out_path("output_4_speakers_horizontal_FLBR.wav")
spk_altura_path = out_path("output_4_speakers_altura_FLRT.wav")
spk_horizontal_3d_path = out_path("output_4_speakers_horizontal_3D_FLBR.wav")
spk_altura_3d_path = out_path("output_4_speakers_altura_3D_FLRT.wav")

# ---------------------------------------------------------
# 1) Guardar FOA limpio
# ---------------------------------------------------------
sf.write(foa_wav_path, foa, sr, subtype="PCM_16")

# ---------------------------------------------------------
# 2) Guardar binaural normal
# ---------------------------------------------------------
sf.write(binaural_wav_path, binaural, sr, subtype="PCM_16")

subprocess.run([
    "ffmpeg", "-y",
    "-i", binaural_wav_path,
    "-codec:a", "libmp3lame",
    "-b:a", "320k",
    binaural_mp3_path
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------------------------------------------------
# 3) Guardar binaural 3D perceptual
# ---------------------------------------------------------
sf.write(perceptual_wav_path, binaural_3d, sr, subtype="PCM_16")

subprocess.run([
    "ffmpeg", "-y",
    "-i", perceptual_wav_path,
    "-codec:a", "libmp3lame",
    "-b:a", "320k",
    perceptual_mp3_path
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =========================================================
# GUARDAR VERSIONES PARA 4 PARLANTES
# =========================================================

# ---------------------------------------------------------
# 1) Parlantes horizontal LIMPIO
# ---------------------------------------------------------
speakers4_horizontal = foa_to_4_speakers(
    W, X, Y, Z,
    layout="horizontal",
    sharpen=True
)

sf.write(
    spk_horizontal_path,
    speakers4_horizontal,
    sr,
    subtype="PCM_16"
)

# ---------------------------------------------------------
# 2) Parlantes con altura LIMPIO
# ---------------------------------------------------------
speakers4_altura = foa_to_4_speakers(
    W, X, Y, Z,
    layout="altura",
    sharpen=True
)

sf.write(
    spk_altura_path,
    speakers4_altura,
    sr,
    subtype="PCM_16"
)

# ---------------------------------------------------------
# 3) Parlantes horizontal 3D PERCEPTUAL
# ---------------------------------------------------------
speakers4_horizontal_3d = foa_to_4_speakers(
    W_3d, X_3d, Y_3d, Z_3d,
    layout="horizontal",
    sharpen=True
)

sf.write(
    spk_horizontal_3d_path,
    speakers4_horizontal_3d,
    sr,
    subtype="PCM_16"
)

# ---------------------------------------------------------
# 4) Parlantes con altura 3D PERCEPTUAL
# ---------------------------------------------------------
speakers4_altura_3d = foa_to_4_speakers(
    W_3d, X_3d, Y_3d, Z_3d,
    layout="altura",
    sharpen=True
)

sf.write(
    spk_altura_3d_path,
    speakers4_altura_3d,
    sr,
    subtype="PCM_16"
)

# =========================================================
# REPRODUCIR EN COLAB
# =========================================================

print("\n🎧 BINAURAL NORMAL")
display(Audio(binaural_wav_path))

print("\n🎧 BINAURAL 3D PERCEPTUAL")
display(Audio(perceptual_wav_path))

# =========================================================
# DESCARGA OPCIONAL
# =========================================================

def make_download_link(path, label, color="#6d28d9"):
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'''
    <a download="{os.path.basename(path)}" href="data:application/octet-stream;base64,{b64}"
       style="
           display:inline-block;
           margin-right:12px;
           margin-top:8px;
           margin-bottom:8px;
           padding:10px 16px;
           background:{color};
           color:white;
           text-decoration:none;
           border-radius:10px;
           font-weight:600;
       ">
       {label}
    </a>
    '''

display(HTML("<h3>Opciones de descarga</h3>"))

display(HTML("""
<p><b>WAV (mejor calidad):</b> recomendado para escuchar en computador o en teléfonos con reproductores compatibles, como VLC.</p>
<p><b>MP3 (mayor compatibilidad):</b> recomendado para escuchar fácilmente en teléfono móvil, compartir por aplicaciones como WhatsApp y reproducir en la mayoría de dispositivos.</p>
"""))

# NO mostrar FOA en la interfaz final pública
# Se conserva internamente para fines técnicos/académicos

# Binaural
display(HTML("<h4>Binaural</h4>"))
display(HTML(
    make_download_link(binaural_wav_path, "Descargar binaural WAV", "#6d28d9") +
    make_download_link(binaural_mp3_path, "Descargar binaural MP3", "#9333ea")
))

# 3D perceptual
display(HTML("<h4>3D perceptual</h4>"))
display(HTML(
    make_download_link(perceptual_wav_path, "Descargar 3D perceptual WAV", "#2563eb") +
    make_download_link(perceptual_mp3_path, "Descargar 3D perceptual MP3", "#0ea5e9")
))

# Parlantes
display(HTML("<h4>Parlantes (solo WAV)</h4>"))
display(HTML(
    make_download_link(spk_horizontal_path, "Descargar 4 parlantes horizontal", "#15803d") +
    make_download_link(spk_altura_path, "Descargar 4 parlantes altura", "#16a34a")
))

display(HTML("<h4>Parlantes 3D perceptual (solo WAV)</h4>"))
display(HTML(
    make_download_link(spk_horizontal_3d_path, "Descargar 4 parlantes horizontal 3D", "#ca8a04") +
    make_download_link(spk_altura_3d_path, "Descargar 4 parlantes altura 3D", "#eab308")
))

# =========================================================
# MENSAJES FINALES
# =========================================================

print("\nPROCESO COMPLETADO")
print("Modo usado:", mode)

print("\nSalida FOA limpia:")
print("Archivo:", foa_wav_path)
print("Orden AmbiX / ACN: [W, Y, Z, X]")

print("\nSalida binaural normal:")
print("Archivo:", binaural_wav_path)

print("\nSalida binaural 3D perceptual:")
print("Archivo:", perceptual_wav_path)
print("Movimiento aplicado sobre canales ambisónicos W, X, Y, Z.")

print("\nSalida 4 parlantes horizontal:")
print("Archivo:", spk_horizontal_path)
print("Orden: [Frente, Izquierda, Atrás, Derecha]")

print("\nSalida 4 parlantes con altura:")
print("Archivo:", spk_altura_path)
print("Orden: [Frente, Izquierda, Derecha, Arriba]")

'''# =========================================================
# GRÁFICAS
# =========================================================
FREQ_PLOT_MAX = min(FREQ_PLOT_MAX_DEFAULT, sr / 2)

if SHOW_PLOTS:
    if mode == "stereo":
        plot_pair_spectrograms(
            diagnostics["f"], diagnostics["t"],
            diagnostics["ZL"], diagnostics["ZR"],
            "Espectrograma del canal L",
            "Espectrograma del canal R",
            FREQ_PLOT_MAX
        )

        plot_pair_spectrograms(
            diagnostics["f"], diagnostics["t"],
            diagnostics["M"], diagnostics["S"],
            "Espectrograma Mid",
            "Espectrograma Side",
            FREQ_PLOT_MAX
        )

        plot_curve(
            diagnostics["t"],
            diagnostics["az_frame_deg"],
            "Azimut estimado por trama",
            "Azimut (°)"
        )

        plot_curve(
            diagnostics["t"],
            diagnostics["el_frame_deg"],
            "Elevación estimada por trama",
            "Elevación (°)"
        )
    # nueva visualización espacial
    dir_stats = foa_direction_statistics(W, X, Y, Z, sr)
    plot_spatial_direction_head(
        dir_stats,
        title="Dirección espacial promedio del sonido",
        show_trajectory=True
    )

    plot_foa_channels(W, X, Y, Z, sr, "Canales FOA en tiempo")

    plot_waveforms_stereo(
        binaural[:, 0], binaural[:, 1], sr,
        "Salida binaural final"
    )
'''

