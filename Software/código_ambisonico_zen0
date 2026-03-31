#Código conversión estéreo a ambisónico con componente z sin variar, z es una matriz de ceros
# INSTALACIÓN
# =========================================================
!pip install soundfile scipy pysofaconventions
!apt-get install ffmpeg -y
!apt-get install curl -y

# IMPORTS
# =========================================================
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

from scipy.signal import stft, istft, fftconvolve
from pysofaconventions import SOFAFile
from google.colab import files

# =========================================================
# DESCARGAR HRTF
# =========================================================
!curl -L -o hrtf.sofa https://sofacoustics.org/data/database/cipic/subject_003.sofa

# =========================================================
# SUBIR AUDIO
# =========================================================
uploaded = files.upload()
audio_file = list(uploaded.keys())[0]

if audio_file.lower().endswith(".mp3"):
    !ffmpeg -y -loglevel quiet -i "{audio_file}" -acodec pcm_s16le -ar 44100 converted.wav
    audio_file = "converted.wav"

# =========================================================
# CARGAR AUDIO
# =========================================================
audio, sr = sf.read(audio_file)

if audio.ndim == 1:
    audio = np.stack([audio, audio], axis=1)

audio = audio[:, :2]

L = audio[:, 0].astype(np.float64)
R = audio[:, 1].astype(np.float64)

# quitar DC
L -= np.mean(L)
R -= np.mean(R)

# normalizar
peak = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-9)
L = 0.95 * L / peak
R = 0.95 * R / peak

# =========================================================
# HRTF
# =========================================================
def load_sofa(path):
    s = SOFAFile(path, 'r')
    ir = s.getDataIR() #filtros del oído
    pos = s.getVariableValue('SourcePosition') #ángulos de cada medición
    return ir, pos

hrtf, pos = load_sofa("hrtf.sofa")

def wrap_deg(x): #buscar htrf mas cercanas
    return ((x + 180) % 360) - 180

def get_hrtf_interp(az_deg):
    az_deg = wrap_deg(az_deg)
    az_all = pos[:, 0]

    diff = np.abs(az_all - az_deg)
    diff = np.minimum(diff, 360 - diff)

    idx = np.argsort(diff)[:3] #interpola

    hL = np.mean(hrtf[idx, 0, :], axis=0)
    hR = np.mean(hrtf[idx, 1, :], axis=0)

    return hL, hR

# =========================================================
# STFT Short-Time Fourier Transform
# =========================================================
n_fft = 2048 #en vez de ver solo la señal se ve qué frecuencias hay en cada instante
hop = n_fft // 4

f, t, ZL = stft(L, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)
_, _, ZR = stft(R, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)

eps = 1e-12 #Interaural Level Difference___ más energía en L, izquierda___ más energía en R, derecha

magL = np.abs(ZL)
magR = np.abs(ZR)

# =========================================================
# ESTIMACIÓN ROBUSTA (PANE0 REAL) diferencia de volumen entre oídos
# =========================================================

balance = (magL - magR) / (magL + magR + eps)
balance = np.clip(balance, -1, 1)

# azimut: -90° a +90°
az = balance * (np.pi / 2)

# suavizado temporal
alpha = 0.7
print(az.shape[1])
for k in range(1, az.shape[1]):
    az[:, k] = alpha * az[:, k-1] + (1 - alpha) * az[:, k]
    #print("Valores de az (primeros):")
    #print("Shape de az:", az.shape)
    #print(az[:5, :5]
print(k)
print(az.shape)


# =========================================================
# SEÑAL BASE
# =========================================================
M = (ZL + ZR) / 2

# =========================================================
# FOA
# =========================================================
W_tf = M / np.sqrt(2)
X_tf = M * np.cos(az)
Y_tf = M * np.sin(az)
Z_tf = np.zeros_like(W_tf)

# =========================================================
# ISTFT
# =========================================================
_, W = istft(W_tf, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)
_, X = istft(X_tf, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)
_, Y = istft(Y_tf, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)
_, Z = istft(Z_tf, fs=sr, nperseg=n_fft, noverlap=n_fft-hop)

N = min(len(W), len(X), len(Y), len(L))
W, X, Y, Z = W[:N], X[:N], Y[:N], Z[:N]

# =========================================================
# FOA AMBIX
# =========================================================
foa = np.stack([W, Y, Z, X], axis=1)
foa /= np.max(np.abs(foa)) + 1e-9

# =========================================================
# VALIDACIÓN AMBISONICS (FOA)
# =========================================================
print("\n===== VALIDACIÓN FOA =====")

print("Shape FOA:", foa.shape)
print("Número de canales:", foa.shape[1])

if foa.shape[1] == 4:
    print("✔ FOA válido (4 canales: W, Y, Z, X)")
else:
    print("No es FOA correcto")

print("\nDuración (samples):", foa.shape[0])
print("Sample rate:", sr)

def rms(x):
    return np.sqrt(np.mean(x**2) + 1e-12)

print("\nRMS por canal:")
print("W (omni):", rms(foa[:,0]))
print("Y (izq-der):", rms(foa[:,1]))
print("Z (arriba-abajo):", rms(foa[:,2]))
print("X (frente-atras):", rms(foa[:,3]))

print("\nChequeo de energía:")
print("Max abs W:", np.max(np.abs(foa[:,0])))
print("Max abs Y:", np.max(np.abs(foa[:,1])))
print("Max abs Z:", np.max(np.abs(foa[:,2])))
print("Max abs X:", np.max(np.abs(foa[:,3])))
# =========================================================
# DECODIFICACIÓN BINAURAL
# =========================================================
angles = np.arange(-90, 91, 10)

bin_L = np.zeros(N)
bin_R = np.zeros(N)

for phi_deg in angles:
    phi = np.deg2rad(phi_deg)

    s = (W/np.sqrt(2)) + (X*np.cos(phi) + Y*np.sin(phi))
    s /= np.sqrt(len(angles))

    hL, hR = get_hrtf_interp(phi_deg)

    yL = fftconvolve(s, hL, mode="same")
    yR = fftconvolve(s, hR, mode="same")

    bin_L += yL
    bin_R += yR

binaural = np.stack([bin_L, bin_R], axis=1)
binaural /= np.max(np.abs(binaural)) + 1e-9

# =========================================================
# VISUALIZACIÓN
# =========================================================
weight = np.abs(M)**2
az_deg = -np.rad2deg(az)

az_mean = np.sum(az_deg * weight, axis=0) / (np.sum(weight, axis=0) + 1e-9)

plt.figure(figsize=(10,4))
plt.plot(t, az_mean)
plt.axhline(0, linestyle="--")
plt.title("Azimut estimado (paneo estéreo)")
plt.xlabel("Tiempo")
plt.ylabel("Azimut (°)  [+ derecha | - izquierda]")
plt.grid()
plt.show()

# =========================================================
# GUARDAR
# =========================================================
sf.write("output_foa.wav", foa, sr)
sf.write("output_binaural.wav", binaural, sr)

files.download("output_foa.wav")
files.download("output_binaural.wav")

print("FUNCIONANDO CORRECTAMENTE")
