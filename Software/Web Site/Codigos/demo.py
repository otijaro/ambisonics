# Parameters
input_audio_path = ""
output_dir = ""
use_external_input = False

direccion = 0
altura = 25
apertura = 50
movimiento = 40
hrtf_path = ""

import io
import os
import math
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.signal import stft, istft, fftconvolve
from IPython.display import Audio, display, clear_output
import ipywidgets as widgets

try:
    from google.colab import files
except ImportError:
    files = None

try:
    from pysofaconventions import SOFAFile
    SOFA_OK = True
except:
    SOFA_OK = False

print("Imports OK")


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

VIRTUAL_SPEAKERS = [
    (0.0,    0.0, 1.00),
    (60.0,   0.0, 0.75),
    (-60.0,  0.0, 0.75),
    (180.0,  0.0, 0.30),
    (0.0,   45.0, 0.35),
    (0.0,  -45.0, 0.18),
]

def normalize_multichannel(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float64)
    if audio.ndim == 1:
        audio = audio[:, None]
    audio = audio - np.mean(audio, axis=0, keepdims=True)
    peak = np.max(np.abs(audio)) + 1e-9
    return 0.95 * audio / peak

def wrap_deg(x):
    return ((x + 180) % 360) - 180

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

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

def build_demo_params(
    azimuth_shift_deg=0.0,
    elevation_boost_pct=10.0,
    width_pct=45.0,
    movement_pct=35.0,
):
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

print("Funciones base OK")

def stereo_to_foa_demo(audio_stereo: np.ndarray, sr: int, params: dict):
    N_FFT = int(params["N_FFT"])
    hop = N_FFT // 4
    eps = 1e-12

    L = audio_stereo[:, 0]
    R = audio_stereo[:, 1]

    f, t, ZL = stft(L, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)
    _, _, ZR = stft(R, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)

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

    _, W = istft(W_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)
    _, X = istft(X_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)
    _, Y = istft(Y_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)
    _, Z = istft(Z_tf, fs=sr, nperseg=N_FFT, noverlap=N_FFT - hop)

    N = min(len(W), len(X), len(Y), len(Z), len(L), len(R))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    peak = np.max(np.abs(np.stack([W, X, Y, Z], axis=1))) + 1e-9
    W /= peak
    X /= peak
    Y /= peak
    Z /= peak

    diagnostics = {
        "el_mean_deg": float(np.mean(np.rad2deg(el_frame))),
        "z_conf_mean": float(np.mean(z_conf)),
        "channel_order_internal": "W, X, Y, Z"
    }

    return W, X, Y, Z, diagnostics

def normalize_audio(x, peak_target=0.95):
    peak = np.max(np.abs(x)) + 1e-9
    if peak > 0:
        x = peak_target * x / peak
    return x


def foa_motion_preview(W, X, Y, Z, sr,
                       rate_az=0.12,
                       rate_el=0.09,
                       max_el_deg=58.0,
                       z_preview_gain=3.0):

    N = min(len(W), len(X), len(Y), len(Z))

    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    t = np.arange(N) / sr

    az = 2 * np.pi * rate_az * t

    X_rot = np.cos(az) * X - np.sin(az) * Y
    Y_rot = -(np.sin(az) * X + np.cos(az) * Y)

    el = np.deg2rad(max_el_deg) * np.sin(2 * np.pi * rate_el * t)

    X_3d = np.cos(el) * X_rot - np.sin(el) * (z_preview_gain * Z)
    Z_3d = np.sin(el) * X_rot + np.cos(el) * (z_preview_gain * Z)

    W_3d = W
    Y_3d = Y_rot

    return W_3d, X_3d, Y_3d, Z_3d


def stabilize_loudness(y, sr,
                       win_ms=455,
                       strength=0.70,
                       min_gain=2,
                       max_gain=2.5):
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
    return normalize_audio(y_out, peak_target=0.95)

print("Movimiento 3D perceptual OK")

def foa_to_binaural(W, X, Y, Z, sr, hrtf, pos):
    N = min(len(W), len(X), len(Y), len(Z))
    W = W[:N]
    X = X[:N]
    Y = Y[:N]
    Z = Z[:N]

    outL = np.zeros(N + 512)
    outR = np.zeros(N + 512)

    for az_deg, el_deg, gain in VIRTUAL_SPEAKERS:
        az = -np.deg2rad(az_deg)
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

    N2 = min(len(outL), len(outR))
    binaural = np.stack([outL[:N2], outR[:N2]], axis=1)
    binaural /= np.max(np.abs(binaural)) + 1e-9
    return binaural


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

print("Binaural OK")

audio, sr, audio_path = load_audio_entry()

print("Audio detectado:", audio_path)

if audio_path is None:
    print("No se detectó ningún audio.")

az_slider = widgets.IntSlider(
    value=0, min=-90, max=90, step=1,
    description='Azimut', style={'description_width': 'initial'},
    layout=widgets.Layout(width='500px')
)

el_slider = widgets.IntSlider(
    value=20, min=0, max=100, step=1,
    description='Altura', style={'description_width': 'initial'},
    layout=widgets.Layout(width='500px')
)

width_slider = widgets.IntSlider(
    value=45, min=0, max=100, step=1,
    description='Apertura', style={'description_width': 'initial'},
    layout=widgets.Layout(width='500px')
)

move_slider = widgets.IntSlider(
    value=35, min=0, max=100, step=1,
    description='Movimiento', style={'description_width': 'initial'},
    layout=widgets.Layout(width='500px')
)

process_button = widgets.Button(
    description="Procesar preview",
    button_style='primary'
)

output_box = widgets.Output()

display(widgets.VBox([
    widgets.HTML("<h3>Demo interactiva ambisónica</h3>"),
    widgets.HTML("<p>Mueve los controles y genera una vista previa.</p>"),
    az_slider, el_slider, width_slider, move_slider, process_button, output_box
]))



from IPython.display import HTML, Audio, display
import os
import base64

def process_demo(_):
    if not use_external_input:
        with output_box:
            clear_output()
            _run_processing()
    else:
        _run_processing()

def _run_processing():
    SOFA_DEFAULT_PATH = globals().get("hrtf_path", "hrtf.sofa")

    if not os.path.exists(SOFA_DEFAULT_PATH):
        print("Descargando HRTF por defecto...")
        try:
            import urllib.request
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/hoene/libmysofa/main/tests/CIPIC_subject_003_hrir_final_itdInDelayField.sofa",
                SOFA_DEFAULT_PATH
            )
        except Exception as dl_err:
            print("Error downloading default HRTF:", dl_err)

    print("Procesando...")

    # --------------------------------------------------
    # Preparar audio
    # --------------------------------------------------
    audio_norm = normalize_multichannel(audio)

    if audio_norm.shape[1] < 2:
        audio_norm = np.repeat(audio_norm, 2, axis=1)

    # Preview de 30 s
    N = min(len(audio_norm), int(30.0 * sr))
    audio_demo = audio_norm[:N, :2]

    # --------------------------------------------------
    # Parámetros del demo
    # --------------------------------------------------
    if use_external_input:
        params = build_demo_params(
            azimuth_shift_deg=direccion,
            elevation_boost_pct=altura,
            width_pct=apertura,
            movement_pct=movimiento,
        )
    else:
        params = build_demo_params(
            azimuth_shift_deg=az_slider.value,
            elevation_boost_pct=el_slider.value,
            width_pct=width_slider.value,
            movement_pct=move_slider.value,
        )

    # IMPORTANTE: stereo_to_foa_demo debe devolver W, X, Y, Z, diagnostics
    W, X, Y, Z, diagnostics = stereo_to_foa_demo(audio_demo, sr, params)

    # --------------------------------------------------
    # Cargar SOFA
    # --------------------------------------------------
    used_sofa = False
    hrtf = None
    pos = None

    if SOFA_OK and os.path.exists(SOFA_DEFAULT_PATH):
        try:
            hrtf, pos = load_sofa(SOFA_DEFAULT_PATH)
            used_sofa = True
        except Exception as e:
            print("No se pudo cargar el SOFA por defecto.")
            print("Detalle:", e)

    # --------------------------------------------------
    # Binaural normal
    # --------------------------------------------------
    if used_sofa:
        binaural = foa_to_binaural(W, X, Y, Z, sr, hrtf, pos)
    else:
        print("Usando fallback simple para binaural.")
        binaural = foa_to_binaural_fallback(W, X, Y, Z)

    binaural = normalize_audio(binaural, peak_target=0.95)

    # --------------------------------------------------
    # 3D perceptual
    # --------------------------------------------------
    W_3d, X_3d, Y_3d, Z_3d = foa_motion_preview(
        W, X, Y, Z, sr,
        rate_az=0.12,
        rate_el=0.10,
        max_el_deg=60.0,
        z_preview_gain=3.5
    )

    if used_sofa:
        binaural_3d = foa_to_binaural(W_3d, X_3d, Y_3d, Z_3d, sr, hrtf, pos)
    else:
        print("Usando fallback simple para 3D perceptual.")
        binaural_3d = foa_to_binaural_fallback(W_3d, X_3d, Y_3d, Z_3d)

    binaural_3d = 0.90 * binaural_3d + 0.10 * binaural
    binaural_3d = stabilize_loudness(
        binaural_3d,
        sr,
        win_ms=300,
        strength=0.70,
        min_gain=0.95,
        max_gain=1.60
    )

    # --------------------------------------------------
    # Rutas de salida
    # --------------------------------------------------
    binaural_wav_path = out_path("preview_binaural.wav")
    perceptual_wav_path = out_path("preview_3d_perceptual.wav")
    binaural_mp3_path = out_path("preview_binaural.mp3")
    perceptual_mp3_path = out_path("preview_3d_perceptual.mp3")

    # --------------------------------------------------
    # Guardar archivos WAV
    # --------------------------------------------------
    sf.write(binaural_wav_path, binaural, sr, subtype="PCM_16")
    sf.write(perceptual_wav_path, binaural_3d, sr, subtype="PCM_16")

    # --------------------------------------------------
    # Convertir a MP3
    # --------------------------------------------------
    try:
        import subprocess
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", binaural_wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", "320k",
            binaural_mp3_path
        ], check=True)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "quiet",
            "-i", perceptual_wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", "320k",
            perceptual_mp3_path
        ], check=True)
    except Exception as ffmpeg_err:
        print("Error converting to MP3 using ffmpeg:", ffmpeg_err)

    print("Preview lista.")
    print("SOFA usado:", used_sofa)
    print("Diagnóstico:", diagnostics)

    if not use_external_input:
        # --------------------------------------------------
        # Reproducción
        # --------------------------------------------------
        display(HTML("<h4>Escucha binaural</h4>"))
        display(HTML("<p><b>Recomendación:</b> usa audífonos para percibir mejor la espacialidad.</p>"))
        display(Audio(binaural_wav_path))

        display(HTML("<h4>Escucha 3D perceptual</h4>"))
        display(Audio(perceptual_wav_path))

        # --------------------------------------------------
        # Descarga opcional con links HTML
        # --------------------------------------------------
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

        display(HTML("<h4>Opciones de descarga</h4>"))
        display(HTML("""
        <p><b>WAV (mejor calidad):</b> recomendado para escuchar en computador o en teléfonos con reproductores compatibles, como VLC.</p>
        <p><b>MP3 (mayor compatibilidad):</b> recomendado para escuchar fácilmente en teléfono móvil, compartir por aplicaciones como WhatsApp y reproducir en la mayoría de dispositivos.</p>
        """))

        binaural_wav_link = make_download_link(binaural_wav_path, "Descargar binaural WAV", "#6d28d9")
        binaural_mp3_link = make_download_link(binaural_mp3_path, "Descargar binaural MP3", "#9333ea")
        perceptual_wav_link = make_download_link(perceptual_wav_path, "Descargar 3D perceptual WAV", "#2563eb")
        perceptual_mp3_link = make_download_link(perceptual_mp3_path, "Descargar 3D perceptual MP3", "#0ea5e9")

        display(HTML(binaural_wav_link + binaural_mp3_link))
        display(HTML(perceptual_wav_link + perceptual_mp3_link))

process_button.on_click(process_demo)
print("Listo.")


print("""
Controles visibles para el usuario:
- Azimut: mueve el sonido lateralmente
- Altura: refuerza la sensación vertical
- Apertura: abre o cierra la escena espacial
- Movimiento: hace la demo más suave o más reactiva

Por dentro, estos controles modifican parámetros reales del sistema.
""")

