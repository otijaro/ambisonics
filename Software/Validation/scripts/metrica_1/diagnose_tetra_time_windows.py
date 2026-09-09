import os, sys, csv
import numpy as np
import soundfile as sf

try:
    import matplotlib.pyplot as plt
    HAS_PLOT = True
except Exception:
    HAS_PLOT = False

# =========================================================
# RUTAS
# =========================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATION_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR).lower() == "scripts" else SCRIPT_DIR
PROJECT_DIR = os.path.dirname(VALIDATION_DIR)

TETRA_DIR = os.path.join(VALIDATION_DIR, "audios_tests", "studio_4mic")
RESULTS_DIR = os.path.join(VALIDATION_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

backend_candidates = [
    os.path.join(PROJECT_DIR, "ambisonics_backend"),
    os.path.join(PROJECT_DIR, "Web Site", "backend"),
    os.path.join(PROJECT_DIR, "backend"),
]
BACKEND_DIR = next((p for p in backend_candidates if os.path.isdir(p)), None)

if BACKEND_DIR is None:
    raise FileNotFoundError("No se encontró el backend.")

sys.path.insert(0, BACKEND_DIR)
from core_dsp import tetra_aformat_to_foa

# =========================================================
# CONFIGURACIÓN
# =========================================================
WINDOW_SEC = 0.50
HOP_SEC = 0.25

DIRECTIONS = [
    ("+X", "Frente",    "X", +1),
    ("-X", "Atrás",     "X", -1),
    ("+Y", "Izquierda", "Y", +1),
    ("-Y", "Derecha",   "Y", -1),
    ("+Z", "Arriba",    "Z", +1),
    ("-Z", "Abajo",     "Z", -1),
]

# =========================================================
# FUNCIONES
# =========================================================
def rms(x):
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt(np.mean(x*x)))

def relative_coefficient(ref, sig):
    ref = np.asarray(ref, dtype=np.float64)
    sig = np.asarray(sig, dtype=np.float64)
    return float(np.dot(ref, sig) / (np.dot(ref, ref) + 1e-12))

def pair_energy(audio, a, b):
    aa = np.asarray(audio[:, a], dtype=np.float64)
    bb = np.asarray(audio[:, b], dtype=np.float64)
    return float(np.sqrt(0.5*(np.mean(aa*aa) + np.mean(bb*bb))))

def balance(pos, neg):
    return float((pos-neg)/(pos+neg+1e-12))

def is_original(path):
    name = os.path.basename(path).lower()
    excluded = ["output_", "foa", "binaural", "speaker", "parlante",
                "quad", "horizontal", "altura", "3d", "render"]
    if any(x in name for x in excluded):
        return False
    try:
        return sf.info(path).channels >= 4
    except Exception:
        return False

def find_file(direction):
    candidates = []
    for root, _, files in os.walk(TETRA_DIR):
        if direction.upper() not in root.upper():
            continue
        for fn in files:
            if fn.lower().endswith(".wav"):
                p = os.path.join(root, fn)
                if is_original(p):
                    candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda p: (direction.upper() not in os.path.basename(p).upper(), len(p)))
    return candidates[0]

def analyze_raw(block):
    front = pair_energy(block, 0, 1)
    back  = pair_energy(block, 2, 3)
    left  = pair_energy(block, 0, 2)
    right = pair_energy(block, 1, 3)
    up    = pair_energy(block, 0, 3)
    down  = pair_energy(block, 1, 2)
    return balance(front, back), balance(left, right), balance(up, down)

def analyze_foa(block):
    res = tetra_aformat_to_foa(block[:, :4])
    W, X, Y, Z = [np.asarray(res[i], dtype=np.float64) for i in range(4)]
    return {
        "RMS_W": rms(W), "RMS_X": rms(X), "RMS_Y": rms(Y), "RMS_Z": rms(Z),
        "coef_X_W": relative_coefficient(W, X),
        "coef_Y_W": relative_coefficient(W, Y),
        "coef_Z_W": relative_coefficient(W, Z),
    }

# =========================================================
# PROCESAMIENTO TEMPORAL
# =========================================================
all_rows = []
summary_rows = []

print("\n" + "="*90)
print("DIAGNOSTICO TEMPORAL POR VENTANAS - BANCO TETRA")
print("="*90)
print(f"Ventana: {WINDOW_SEC:.2f} s | Salto: {HOP_SEC:.2f} s")

for direction, interpretation, expected_axis, expected_sign in DIRECTIONS:
    path = find_file(direction)
    if path is None:
        print(f"NO ENCONTRADO: {direction}")
        continue

    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    audio = audio[:, :4]

    win = int(round(WINDOW_SEC*sr))
    hop = int(round(HOP_SEC*sr))
    rows_dir = []
    k = 0

    for start in range(0, len(audio), hop):
        end = min(start + win, len(audio))
        if end-start < 0.5*win:
            break

        block = audio[start:end]
        bx, by, bz = analyze_raw(block)
        foa = analyze_foa(block)

        raw_axis = {"X":bx, "Y":by, "Z":bz}[expected_axis]
        foa_axis = {
            "X":foa["coef_X_W"],
            "Y":foa["coef_Y_W"],
            "Z":foa["coef_Z_W"]
        }[expected_axis]

        row = {
            "direccion": direction,
            "interpretacion": interpretation,
            "archivo": os.path.basename(path),
            "ventana": k,
            "t_inicio_s": start/sr,
            "t_fin_s": end/sr,
            "t_centro_s": 0.5*((start/sr)+(end/sr)),
            "balance_X_raw": bx,
            "balance_Y_raw": by,
            "balance_Z_raw": bz,
            **foa,
            "eje_esperado": expected_axis,
            "signo_esperado": expected_sign,
            "valor_eje_esperado_raw": raw_axis,
            "valor_eje_esperado_foa": foa_axis,
            "raw_coherente": (expected_sign*raw_axis) > 0,
            "foa_coherente": (expected_sign*foa_axis) > 0,
        }
        all_rows.append(row)
        rows_dir.append(row)
        k += 1

    raw_vals = np.array([r["valor_eje_esperado_raw"] for r in rows_dir], dtype=float)
    foa_vals = np.array([r["valor_eje_esperado_foa"] for r in rows_dir], dtype=float)

    summary = {
        "direccion": direction,
        "interpretacion": interpretation,
        "archivo": os.path.basename(path),
        "numero_ventanas": len(rows_dir),
        "eje_esperado": expected_axis,
        "signo_esperado": expected_sign,
        "raw_media_eje": float(np.mean(raw_vals)),
        "raw_mediana_eje": float(np.median(raw_vals)),
        "raw_min_eje": float(np.min(raw_vals)),
        "raw_max_eje": float(np.max(raw_vals)),
        "raw_porcentaje_ventanas_coherentes": float(100*np.mean([r["raw_coherente"] for r in rows_dir])),
        "foa_media_eje": float(np.mean(foa_vals)),
        "foa_mediana_eje": float(np.median(foa_vals)),
        "foa_min_eje": float(np.min(foa_vals)),
        "foa_max_eje": float(np.max(foa_vals)),
        "foa_porcentaje_ventanas_coherentes": float(100*np.mean([r["foa_coherente"] for r in rows_dir])),
    }
    summary_rows.append(summary)

    print(
        f"{direction:>2} {interpretation:<10} | "
        f"A-format coherente={summary['raw_porcentaje_ventanas_coherentes']:6.1f}% | "
        f"FOA coherente={summary['foa_porcentaje_ventanas_coherentes']:6.1f}%"
    )

# =========================================================
# CSV
# =========================================================
detail_csv = os.path.join(RESULTS_DIR, "diagnostico_tetra_ventanas_detalle.csv")
summary_csv = os.path.join(RESULTS_DIR, "diagnostico_tetra_ventanas_resumen.csv")

if all_rows:
    with open(detail_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        w.writeheader()
        w.writerows(all_rows)

if summary_rows:
    with open(summary_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        w.writeheader()
        w.writerows(summary_rows)

# =========================================================
# GRAFICAS: UNA FIGURA POR DIRECCION
# =========================================================
if HAS_PLOT:
    for direction, interpretation, _, _ in DIRECTIONS:
        rows_dir = [r for r in all_rows if r["direccion"] == direction]
        if not rows_dir:
            continue

        t = [r["t_centro_s"] for r in rows_dir]
        tag = direction.replace("+", "plus").replace("-", "minus")

        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(t, [r["balance_X_raw"] for r in rows_dir], label="Balance X")
        ax.plot(t, [r["balance_Y_raw"] for r in rows_dir], label="Balance Y")
        ax.plot(t, [r["balance_Z_raw"] for r in rows_dir], label="Balance Z")
        ax.axhline(0, linewidth=1)
        ax.set_title(f"Balances A-format por ventanas - {direction} ({interpretation})")
        ax.set_xlabel("Tiempo [s]")
        ax.set_ylabel("Balance normalizado")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(os.path.join(RESULTS_DIR, f"diagnostico_ventanas_raw_{tag}.png"), dpi=200)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(t, [r["coef_X_W"] for r in rows_dir], label="X/W")
        ax.plot(t, [r["coef_Y_W"] for r in rows_dir], label="Y/W")
        ax.plot(t, [r["coef_Z_W"] for r in rows_dir], label="Z/W")
        ax.axhline(0, linewidth=1)
        ax.set_title(f"Coeficientes FOA por ventanas - {direction} ({interpretation})")
        ax.set_xlabel("Tiempo [s]")
        ax.set_ylabel("Coeficiente respecto a W")
        ax.legend()
        ax.grid(alpha=0.25)
        fig.tight_layout()
        fig.savefig(os.path.join(RESULTS_DIR, f"diagnostico_ventanas_foa_{tag}.png"), dpi=200)
        plt.close(fig)

print("\nArchivos generados:")
print(detail_csv)
print(summary_csv)
print("\nInterpretacion:")
print("- Si A-format y FOA fallan durante casi toda la grabacion, el problema ya esta en la captura.")
print("- Si A-format es coherente y FOA no, revisar matriz/convencion de tetra_aformat_to_foa().")
print("- Si solo fallan ventanas aisladas, revisar silencios, transitorios, movimiento o reverberacion.")
