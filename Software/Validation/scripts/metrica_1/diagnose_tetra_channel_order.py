import os
import sys
import csv
import re
import itertools
import numpy as np
import soundfile as sf


# =========================================================
# RUTAS DEL PROYECTO
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Funciona si el script está en validation/ o validation/scripts/
if os.path.basename(SCRIPT_DIR).lower() == "scripts":
    VALIDATION_DIR = os.path.dirname(SCRIPT_DIR)
else:
    VALIDATION_DIR = SCRIPT_DIR

PROJECT_DIR = os.path.dirname(VALIDATION_DIR)

TETRA_DIR = os.path.join(
    VALIDATION_DIR,
    "audios_tests",
    "studio_4mic"
)

RESULTS_DIR = os.path.join(
    VALIDATION_DIR,
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# Buscar backend
backend_candidates = [
    os.path.join(PROJECT_DIR, "ambisonics_backend"),
    os.path.join(PROJECT_DIR, "Web Site", "backend"),
    os.path.join(PROJECT_DIR, "backend"),
]

BACKEND_DIR = next(
    (p for p in backend_candidates if os.path.isdir(p)),
    None
)

if BACKEND_DIR is None:
    raise FileNotFoundError(
        "No se encontró el backend. Rutas probadas:\n- "
        + "\n- ".join(backend_candidates)
    )

sys.path.insert(0, BACKEND_DIR)

from core_dsp import tetra_aformat_to_foa


# =========================================================
# CONFIGURACIÓN DE LA PRUEBA
# =========================================================

# Orden que espera la función tetra_aformat_to_foa()
EXPECTED_MIC_ORDER = ["FLU", "FRD", "BLD", "BRU"]

# Dirección física -> componente FOA esperada y signo esperado
DIRECTION_RULES = [
    ("+X", "Frente",    "X", +1),
    ("-X", "Atrás",     "X", -1),
    ("+Y", "Izquierda", "Y", +1),
    ("-Y", "Derecha",   "Y", -1),
    ("+Z", "Arriba",    "Z", +1),
    ("-Z", "Abajo",     "Z", -1),
]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def relative_coefficient(reference, signal):
    """
    Proyección de signal sobre reference conservando el signo.
    """
    reference = np.asarray(reference, dtype=np.float64)
    signal = np.asarray(signal, dtype=np.float64)

    den = np.dot(reference, reference) + 1e-12
    return np.dot(reference, signal) / den


def is_probable_original_tetra(path):
    """
    Excluye salidas previas y conserva WAV originales de 4 canales.
    """
    name = os.path.basename(path).lower()

    excluded_terms = [
        "output_", "foa", "binaural", "speaker", "parlante",
        "quad", "horizontal", "altura", "3d", "render"
    ]

    if any(term in name for term in excluded_terms):
        return False

    try:
        return sf.info(path).channels >= 4
    except Exception:
        return False


def find_tetra_file(direction):
    """
    Busca el archivo original asociado a +X, -X, +Y, -Y, +Z o -Z.
    """
    candidates = []

    if not os.path.isdir(TETRA_DIR):
        return None

    for root, _, files in os.walk(TETRA_DIR):
        if direction.upper() not in root.upper():
            continue

        for filename in files:
            if not filename.lower().endswith(".wav"):
                continue

            path = os.path.join(root, filename)

            if is_probable_original_tetra(path):
                candidates.append(path)

    if not candidates:
        return None

    candidates.sort(
        key=lambda p: (
            direction.upper() not in os.path.basename(p).upper(),
            len(p)
        )
    )

    return candidates[0]


def analyze_reordered_audio(audio, permutation):
    """
    permutation indica qué canal grabado se utilizará como:
    [FLU, FRD, BLD, BRU]

    Ejemplo:
    (0, 1, 2, 3) = orden actual
    (2, 0, 3, 1) = FLU<-ch3, FRD<-ch1, BLD<-ch4, BRU<-ch2
    """
    reordered = audio[:, permutation]

    result = tetra_aformat_to_foa(reordered)

    W = np.asarray(result[0], dtype=np.float64)
    X = np.asarray(result[1], dtype=np.float64)
    Y = np.asarray(result[2], dtype=np.float64)
    Z = np.asarray(result[3], dtype=np.float64)

    cx = relative_coefficient(W, X)
    cy = relative_coefficient(W, Y)
    cz = relative_coefficient(W, Z)

    return cx, cy, cz


def score_direction(cx, cy, cz, expected_component, expected_sign):
    """
    Puntúa qué tan bien coincide el vector direccional con el eje esperado.

    alignment:
      +1 = perfectamente alineado con la dirección esperada
       0 = perpendicular
      -1 = dirección opuesta

    dominance:
      1 = toda la contribución direccional está en el eje esperado
      0 = el eje esperado no participa
    """
    c = {
        "X": cx,
        "Y": cy,
        "Z": cz,
    }

    vec = np.array([cx, cy, cz], dtype=np.float64)
    norm = np.linalg.norm(vec) + 1e-12

    expected_value = expected_sign * c[expected_component]

    alignment = expected_value / norm

    abs_sum = abs(cx) + abs(cy) + abs(cz) + 1e-12
    dominance = abs(c[expected_component]) / abs_sum

    # 70 % signo/alineación + 30 % predominio
    score = 0.70 * alignment + 0.30 * dominance

    return float(score), float(alignment), float(dominance)


def mapping_text(permutation):
    """
    Texto legible del mapeo:
    FLU<-Canal 1, FRD<-Canal 2, ...
    """
    return ", ".join(
        f"{mic}<-Canal {idx + 1}"
        for mic, idx in zip(EXPECTED_MIC_ORDER, permutation)
    )


# =========================================================
# CARGAR LAS SEIS GRABACIONES
# =========================================================

direction_audio = {}

print()
print("=" * 86)
print("DIAGNÓSTICO DEL ORDEN DE CANALES - BANCO TETRA")
print("=" * 86)

for direction, interpretation, component, sign in DIRECTION_RULES:

    path = find_tetra_file(direction)

    if path is None:
        raise FileNotFoundError(
            f"No se encontró el WAV original de 4 canales para "
            f"{direction} ({interpretation})."
        )

    audio, sr = sf.read(
        path,
        dtype="float32",
        always_2d=True
    )

    if audio.shape[1] < 4:
        raise ValueError(
            f"{path} tiene {audio.shape[1]} canales; se requieren 4."
        )

    # Solo usamos los cuatro primeros canales de la grabación.
    audio = audio[:, :4]

    direction_audio[direction] = {
        "audio": audio,
        "sr": sr,
        "path": path,
        "interpretation": interpretation,
        "component": component,
        "sign": sign,
    }

    print(
        f"{direction:>2} | {interpretation:<10} | "
        f"{os.path.basename(path)} | "
        f"{audio.shape[1]} canales | {sr} Hz"
    )


# =========================================================
# PROBAR LAS 24 PERMUTACIONES
# =========================================================

permutations = list(itertools.permutations(range(4)))

ranking_rows = []
detail_rows = []

for permutation in permutations:

    direction_scores = []

    for direction, interpretation, component, sign in DIRECTION_RULES:

        info = direction_audio[direction]
        audio = info["audio"]

        cx, cy, cz = analyze_reordered_audio(
            audio,
            permutation
        )

        score, alignment, dominance = score_direction(
            cx, cy, cz,
            component,
            sign
        )

        direction_scores.append(score)

        detail_rows.append({
            "permutation": "-".join(str(i + 1) for i in permutation),
            "mapping": mapping_text(permutation),
            "direction": direction,
            "interpretation": interpretation,
            "expected_component": component,
            "expected_sign": sign,
            "coef_X_W": cx,
            "coef_Y_W": cy,
            "coef_Z_W": cz,
            "alignment": alignment,
            "dominance": dominance,
            "direction_score": score,
        })

    mean_score = float(np.mean(direction_scores))
    min_score = float(np.min(direction_scores))
    std_score = float(np.std(direction_scores))

    ranking_rows.append({
        "permutation": "-".join(str(i + 1) for i in permutation),
        "mapping": mapping_text(permutation),
        "mean_score": mean_score,
        "min_direction_score": min_score,
        "std_score": std_score,
    })


# Ordenar: mejor promedio primero.
# En empate, preferimos mejor peor-caso y menor dispersión.
ranking_rows.sort(
    key=lambda r: (
        r["mean_score"],
        r["min_direction_score"],
        -r["std_score"],
    ),
    reverse=True
)

# Añadir ranking
for i, row in enumerate(ranking_rows, start=1):
    row["rank"] = i

# Reordenar columnas con rank primero
ranking_rows = [
    {
        "rank": r["rank"],
        "permutation": r["permutation"],
        "mapping": r["mapping"],
        "mean_score": r["mean_score"],
        "min_direction_score": r["min_direction_score"],
        "std_score": r["std_score"],
    }
    for r in ranking_rows
]


# =========================================================
# GUARDAR CSV
# =========================================================

ranking_csv = os.path.join(
    RESULTS_DIR,
    "diagnostico_orden_canales_tetra_ranking.csv"
)

detail_csv = os.path.join(
    RESULTS_DIR,
    "diagnostico_orden_canales_tetra_detalle.csv"
)

with open(
    ranking_csv,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=ranking_rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(ranking_rows)


with open(
    detail_csv,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=detail_rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(detail_rows)


# =========================================================
# MOSTRAR TOP 10
# =========================================================

print()
print("=" * 86)
print("TOP 10 ÓRDENES DE CANALES")
print("=" * 86)

for row in ranking_rows[:10]:
    print(
        f"#{row['rank']:02d} | "
        f"score={row['mean_score']:+.4f} | "
        f"peor dirección={row['min_direction_score']:+.4f} | "
        f"{row['mapping']}"
    )


# =========================================================
# COMPARAR ORDEN ACTUAL VS MEJOR
# =========================================================

current_perm = "1-2-3-4"

current_row = next(
    r for r in ranking_rows
    if r["permutation"] == current_perm
)

best_row = ranking_rows[0]

print()
print("=" * 86)
print("COMPARACIÓN")
print("=" * 86)

print("\nOrden actualmente asumido:")
print(" ", current_row["mapping"])
print(f"  Ranking: #{current_row['rank']}")
print(f"  Score promedio: {current_row['mean_score']:+.4f}")

print("\nMejor orden encontrado:")
print(" ", best_row["mapping"])
print(f"  Ranking: #{best_row['rank']}")
print(f"  Score promedio: {best_row['mean_score']:+.4f}")


# =========================================================
# DETALLE DEL MEJOR ORDEN
# =========================================================

best_perm = best_row["permutation"]

best_details = [
    r for r in detail_rows
    if r["permutation"] == best_perm
]

print()
print("=" * 86)
print("DETALLE DEL MEJOR ORDEN")
print("=" * 86)

for r in best_details:
    print(
        f"{r['direction']:>2} {r['interpretation']:<10} | "
        f"X/W={r['coef_X_W']:+.4f} "
        f"Y/W={r['coef_Y_W']:+.4f} "
        f"Z/W={r['coef_Z_W']:+.4f} | "
        f"score={r['direction_score']:+.4f}"
    )


print()
print("=" * 86)
print("ARCHIVOS GENERADOS")
print("=" * 86)

print(ranking_csv)
print(detail_csv)

print()
print(
    "IMPORTANTE: este script NO modifica los audios ni el algoritmo. "
    "Solo prueba los 24 órdenes posibles para identificar si el problema "
    "puede explicarse por un mapeo incorrecto de los cuatro canales."
)
