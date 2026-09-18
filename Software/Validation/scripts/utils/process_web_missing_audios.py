import os
import sys
import time
import shutil
import requests
import soundfile as sf

# =========================================================
# CONFIGURACIÓN Y RUTAS
# =========================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UTILS_DIR = SCRIPT_DIR
SCRIPTS_DIR = os.path.dirname(UTILS_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)
SOFTWARE_DIR = os.path.dirname(VALIDATION_DIR)
REPO_ROOT = os.path.dirname(SOFTWARE_DIR)

API_BASE_URL = "http://127.0.0.1:8000"
STATIC_DIR = os.path.join(SOFTWARE_DIR, "Web Site", "backend", "static")
AUDIOS_ROOT = os.path.join(VALIDATION_DIR, "audios_tests")

TASKS = [
    # -----------------------------------------------------
    # 1. Banco auxiliar espacial (5 audios, modo estéreo)
    # -----------------------------------------------------
    (
        os.path.join("3. auxiliary_spatial_tests", "test_alternating"),
        "test_alternating.wav",
        "stereo"
    ),
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

    # -----------------------------------------------------
    # 2. Banco experimental 4 micrófonos (14 audios, modo tetraédrico)
    # -----------------------------------------------------
    (
        os.path.join("2. studio_4mic", "DIR BLD"),
        "7.BLD.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR BLU"),
        "5.BLU.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR BRD"),
        "8.BRD.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR BRU"),
        "6.BRU.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR FLD"),
        "3.FLD.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR FLU"),
        "1.FLU.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR FRD"),
        "4.FRD.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "DIR FRU"),
        "2.FRU.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE +X"),
        "EJE +X.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE +Y"),
        "EJE +Y.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE +Z"),
        "EJE +Z.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE -X"),
        "EJE -X.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE -Y"),
        "EJE -Y.wav",
        "tetra_4mic"
    ),
    (
        os.path.join("2. studio_4mic", "EJE -Z"),
        "EJE -Z.wav",
        "tetra_4mic"
    ),
]


def check_health():
    try:
        r = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if r.status_code == 200:
            return True
    except Exception as e:
        print(f"Error conectando al backend: {e}")
    return False


def extract_session_id(resp_json):
    for out in resp_json.get("outputs", []):
        url = out.get("wavUrl", "")
        # Formato esperado: /static/<session_id>/output_binaural.wav
        parts = url.strip("/").split("/")
        if len(parts) >= 3 and parts[0] == "static":
            return parts[1]
    return None


def process_audio_item(idx, total, subfolder, in_filename, mode):
    target_dir = os.path.join(AUDIOS_ROOT, subfolder)
    in_path = os.path.join(target_dir, in_filename)

    target_foa = os.path.join(target_dir, "WEB_output_foa.wav")
    target_bin = os.path.join(target_dir, "WEB_output_binaural.wav")
    target_perc = os.path.join(target_dir, "WEB_output_binaural_3D_perceptual.wav")

    print(f"\n======================================================================")
    print(f"[{idx}/{total}] Procesando: {subfolder} -> {in_filename} (Modo: {mode})")
    print(f"======================================================================")

    if not os.path.exists(in_path):
        print(f"  [!] ERROR: No se encontró el archivo de entrada: {in_path}")
        return False

    if (
        os.path.exists(target_foa) and os.path.getsize(target_foa) > 0 and
        os.path.exists(target_bin) and os.path.getsize(target_bin) > 0 and
        os.path.exists(target_perc) and os.path.getsize(target_perc) > 0
    ):
        print("  [*] Ya procesado anteriormente con éxito. Omitiendo...")
        return True

    t0 = time.time()
    print(f"  [1/4] Enviando solicitud POST a {API_BASE_URL}/api/convert...")
    with open(in_path, "rb") as f:
        files = {"audio": (in_filename, f, "audio/wav")}
        data = {"mode": mode}
        try:
            response = requests.post(f"{API_BASE_URL}/api/convert", files=files, data=data, timeout=300)
        except Exception as e:
            print(f"  [!] ERROR de conexión al convertir: {e}")
            return False

    if response.status_code != 200:
        print(f"  [!] ERROR en API ({response.status_code}): {response.text}")
        return False

    resp_data = response.json()
    proc_sec = resp_data.get("processing_seconds", 0)
    orig_sec = resp_data.get("original_duration_seconds", 0)
    session_id = extract_session_id(resp_data)
    print(f"  [2/4] Conversión exitosa. Audio: {orig_sec:.2f}s, DSP: {proc_sec:.2f}s, Session: {session_id}")

    if not session_id:
        print("  [!] ERROR: No se pudo determinar el session_id de la respuesta.")
        return False

    session_dir = os.path.join(STATIC_DIR, session_id)
    if not os.path.exists(session_dir):
        print(f"  [!] ERROR: Directorio de sesión no encontrado en disco: {session_dir}")
        return False

    src_foa = os.path.join(session_dir, "output_foa.wav")
    src_bin = os.path.join(session_dir, "output_binaural.wav")
    src_perc = os.path.join(session_dir, "output_binaural_3D_perceptual.wav")

    for src_file, name in [(src_foa, "FOA"), (src_bin, "Binaural"), (src_perc, "Perceptual 3D")]:
        if not os.path.exists(src_file) or os.path.getsize(src_file) == 0:
            print(f"  [!] ERROR: Archivo generado {name} no existe o está vacío: {src_file}")
            return False

    print(f"  [3/4] Copiando salidas a la carpeta de validación...")
    shutil.copy2(src_foa, target_foa)
    shutil.copy2(src_bin, target_bin)
    shutil.copy2(src_perc, target_perc)

    # Validar integridad de las salidas copiadas
    foa_info = sf.info(target_foa)
    bin_info = sf.info(target_bin)
    perc_info = sf.info(target_perc)

    t_total = time.time() - t0
    print(f"  [4/4] Verificación de archivos generados:")
    print(f"        -> {os.path.basename(target_foa)}: {foa_info.channels} ch, {foa_info.samplerate} Hz, {os.path.getsize(target_foa)/1024:.1f} KB")
    print(f"        -> {os.path.basename(target_bin)}: {bin_info.channels} ch, {bin_info.samplerate} Hz, {os.path.getsize(target_bin)/1024:.1f} KB")
    print(f"        -> {os.path.basename(target_perc)}: {perc_info.channels} ch, {perc_info.samplerate} Hz, {os.path.getsize(target_perc)/1024:.1f} KB")
    print(f"  [OK] Completado en {t_total:.2f}s.")
    return True


def main():
    print("======================================================================")
    print("PROCESAMIENTO POR LOTES VIA PLATAFORMA WEB (FASTAPI BACKEND)")
    print("======================================================================")
    print(f"Backend URL: {API_BASE_URL}")
    print(f"Static Temp Dir: {STATIC_DIR}")
    print(f"Audios Root: {AUDIOS_ROOT}")

    if not check_health():
        print("[!] ERROR: El backend de FastAPI no esta respondiendo en", API_BASE_URL)
        print("    Por favor asegurate de iniciar el backend antes de ejecutar.")
        sys.exit(1)

    print("[OK] Backend FastAPI operativo y respondiendo.\n")

    t_start = time.time()
    success_count = 0
    total = len(TASKS)

    for idx, (subfolder, in_filename, mode) in enumerate(TASKS, 1):
        ok = process_audio_item(idx, total, subfolder, in_filename, mode)
        if ok:
            success_count += 1
        else:
            print(f"[!] Falló el procesamiento de {subfolder}")

    total_time = time.time() - t_start
    print("\n======================================================================")
    print(f"RESUMEN FINAL")
    print(f"Audios procesados con éxito: {success_count}/{total}")
    print(f"Tiempo total: {total_time:.2f}s ({total_time/60:.2f} min)")
    print("======================================================================")


if __name__ == "__main__":
    main()
