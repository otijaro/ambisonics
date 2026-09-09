import os
import csv
import re
import numpy as np
import soundfile as sf

# Matplotlib es opcional.
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


# =========================================================
# RUTAS
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Permite ejecutar desde validation/ o validation/scripts/
if os.path.basename(SCRIPT_DIR).lower() == "scripts":
    VALIDATION_DIR = os.path.dirname(SCRIPT_DIR)
else:
    VALIDATION_DIR = SCRIPT_DIR

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


# =========================================================
# CONFIGURACIÓN FÍSICA ASUMIDA
# =========================================================
#
# Orden de canales que actualmente se está usando:
#
# Canal 1 = FLU  (Front Left Up)
# Canal 2 = FRD  (Front Right Down)
# Canal 3 = BLD  (Back Left Down)
# Canal 4 = BRU  (Back Right Up)
#
# A partir de esa geometría:
#
# +X (Frente)    -> energía frontal (C1+C2) > trasera (C3+C4)
# -X (Atrás)     -> energía trasera (C3+C4) > frontal (C1+C2)
#
# +Y (Izquierda) -> energía izquierda (C1+C3) > derecha (C2+C4)
# -Y (Derecha)   -> energía derecha (C2+C4) > izquierda (C1+C3)
#
# +Z (Arriba)    -> energía superior (C1+C4) > inferior (C2+C3)
# -Z (Abajo)     -> energía inferior (C2+C3) > superior (C1+C4)
#
# Este script NO modifica el audio ni la matriz FOA.
# Solo analiza las grabaciones A-format originales.
# =========================================================

CHANNEL_NAMES = {
    0: "C1_FLU",
    1: "C2_FRD",
    2: "C3_BLD",
    3: "C4_BRU",
}

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

def rms(x):
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt(np.mean(np.square(x))))


def safe_corr(a, b):
    """
    Correlación normalizada entre dos canales después de remover DC.
    Devuelve valor entre -1 y +1.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    a = a - np.mean(a)
    b = b - np.mean(b)

    den = np.linalg.norm(a) * np.linalg.norm(b)

    if den < 1e-15:
        return 0.0

    return float(np.dot(a, b) / den)


def pair_energy(audio, idx_a, idx_b):
    """
    Energía RMS combinada de dos cápsulas.
    Se calcula a partir de la potencia media de ambos canales,
    no sumando las formas de onda, para evitar que la fase/correlación
    altere artificialmente la estimación de energía.
    """
    a = np.asarray(audio[:, idx_a], dtype=np.float64)
    b = np.asarray(audio[:, idx_b], dtype=np.float64)

    power = 0.5 * (
        np.mean(np.square(a)) +
        np.mean(np.square(b))
    )

    return float(np.sqrt(power))


def normalized_balance(positive_energy, negative_energy):
    """
    Balance normalizado entre dos grupos:
        (positivo - negativo) / (positivo + negativo)

    +1  -> totalmente hacia el grupo positivo
     0  -> misma energía
    -1  -> totalmente hacia el grupo negativo
    """
    den = positive_energy + negative_energy + 1e-12
    return float((positive_energy - negative_energy) / den)


def is_probable_original_tetra(path):
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
    Busca recursivamente el WAV original de 4 canales
    correspondiente a una dirección principal.
    """
    if not os.path.isdir(TETRA_DIR):
        return None

    candidates = []

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


def sanitize(text):
    text = (
        text.replace("+", "plus_")
            .replace("-", "minus_")
            .replace(" ", "_")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
    )
    return re.sub(r"[^A-Za-z0-9_.]", "_", text)


# =========================================================
# ANALIZAR CADA GRABACIÓN
# =========================================================

rows = []
corr_rows = []

print()
print("=" * 90)
print("DIAGNÓSTICO DE LOS 4 CANALES ORIGINALES - BANCO TETRA")
print("=" * 90)

for direction, interpretation, expected_axis, expected_sign in DIRECTION_RULES:

    path = find_tetra_file(direction)

    if path is None:
        print(
            f"ADVERTENCIA: no se encontró archivo original para "
            f"{direction} ({interpretation})."
        )
        continue

    audio, sr = sf.read(
        path,
        dtype="float32",
        always_2d=True
    )

    if audio.shape[1] < 4:
        print(
            f"ADVERTENCIA: {path} tiene {audio.shape[1]} canales; "
            "se requieren al menos 4."
        )
        continue

    audio = audio[:, :4]

    n_samples = audio.shape[0]
    duration = n_samples / sr

    # -----------------------------------------------------
    # 1. RMS / PICO / MEDIA POR CANAL
    # -----------------------------------------------------

    ch_rms = [rms(audio[:, i]) for i in range(4)]

    ch_peak = [
        float(np.max(np.abs(audio[:, i])))
        for i in range(4)
    ]

    ch_mean = [
        float(np.mean(audio[:, i]))
        for i in range(4)
    ]

    dominant_channel = int(np.argmax(ch_rms))
    dominant_channel_name = CHANNEL_NAMES[dominant_channel]

    # -----------------------------------------------------
    # 2. ENERGÍA POR PARES FÍSICOS
    # -----------------------------------------------------

    # X
    front = pair_energy(audio, 0, 1)  # FLU + FRD
    back  = pair_energy(audio, 2, 3)  # BLD + BRU

    # Y
    left  = pair_energy(audio, 0, 2)  # FLU + BLD
    right = pair_energy(audio, 1, 3)  # FRD + BRU

    # Z
    up    = pair_energy(audio, 0, 3)  # FLU + BRU
    down  = pair_energy(audio, 1, 2)  # FRD + BLD

    balance_X = normalized_balance(front, back)
    balance_Y = normalized_balance(left, right)
    balance_Z = normalized_balance(up, down)

    balances = {
        "X": balance_X,
        "Y": balance_Y,
        "Z": balance_Z,
    }

    observed_expected_axis = balances[expected_axis]

    # Para +X/+Y/+Z esperamos balance positivo.
    # Para -X/-Y/-Z esperamos balance negativo.
    signed_expected_balance = expected_sign * observed_expected_axis

    direction_ok = signed_expected_balance > 0

    # -----------------------------------------------------
    # 3. CORRELACIONES ENTRE CANALES
    # -----------------------------------------------------

    corr_pairs = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    ]

    corr_values = {}

    for a, b in corr_pairs:
        value = safe_corr(audio[:, a], audio[:, b])

        key = f"corr_C{a+1}_C{b+1}"
        corr_values[key] = value

        corr_rows.append({
            "direccion": direction,
            "interpretacion": interpretation,
            "archivo": os.path.basename(path),
            "canal_A": CHANNEL_NAMES[a],
            "canal_B": CHANNEL_NAMES[b],
            "correlacion": value,
        })

    # -----------------------------------------------------
    # 4. GUARDAR FILA GENERAL
    # -----------------------------------------------------

    row = {
        "direccion": direction,
        "interpretacion": interpretation,
        "archivo": os.path.basename(path),
        "sample_rate_Hz": sr,
        "muestras": n_samples,
        "duracion_s": duration,

        "RMS_C1_FLU": ch_rms[0],
        "RMS_C2_FRD": ch_rms[1],
        "RMS_C3_BLD": ch_rms[2],
        "RMS_C4_BRU": ch_rms[3],

        "Pico_C1_FLU": ch_peak[0],
        "Pico_C2_FRD": ch_peak[1],
        "Pico_C3_BLD": ch_peak[2],
        "Pico_C4_BRU": ch_peak[3],

        "Media_C1_FLU": ch_mean[0],
        "Media_C2_FRD": ch_mean[1],
        "Media_C3_BLD": ch_mean[2],
        "Media_C4_BRU": ch_mean[3],

        "canal_RMS_dominante": dominant_channel_name,

        "energia_frente_C1C2": front,
        "energia_atras_C3C4": back,
        "balance_X_frente_menos_atras": balance_X,

        "energia_izquierda_C1C3": left,
        "energia_derecha_C2C4": right,
        "balance_Y_izquierda_menos_derecha": balance_Y,

        "energia_arriba_C1C4": up,
        "energia_abajo_C2C3": down,
        "balance_Z_arriba_menos_abajo": balance_Z,

        "eje_esperado": expected_axis,
        "signo_esperado": expected_sign,
        "balance_eje_esperado": observed_expected_axis,
        "balance_corregido_por_signo_esperado": signed_expected_balance,
        "coherencia_bruta_direccion": direction_ok,

        **corr_values,
    }

    rows.append(row)

    # -----------------------------------------------------
    # 5. MOSTRAR RESULTADO
    # -----------------------------------------------------

    print()
    print("-" * 90)
    print(
        f"{direction} | {interpretation} | "
        f"{os.path.basename(path)}"
    )
    print("-" * 90)

    print(f"Fs       : {sr} Hz")
    print(f"Duración : {duration:.3f} s")

    print("\nRMS por canal:")
    for i in range(4):
        print(
            f"  {CHANNEL_NAMES[i]:<8} = "
            f"{ch_rms[i]:.6f}"
        )

    print(
        "\nCanal con mayor RMS:",
        dominant_channel_name
    )

    print("\nEnergías por pares:")
    print(f"  Frente    C1+C2 = {front:.6f}")
    print(f"  Atrás     C3+C4 = {back:.6f}")
    print(f"  Balance X       = {balance_X:+.6f}")

    print(f"  Izquierda C1+C3 = {left:.6f}")
    print(f"  Derecha   C2+C4 = {right:.6f}")
    print(f"  Balance Y       = {balance_Y:+.6f}")

    print(f"  Arriba    C1+C4 = {up:.6f}")
    print(f"  Abajo     C2+C3 = {down:.6f}")
    print(f"  Balance Z       = {balance_Z:+.6f}")

    print(
        f"\nDirección esperada: {direction} "
        f"-> eje {expected_axis}, "
        f"signo {'+' if expected_sign > 0 else '-'}"
    )

    print(
        "Balance sobre el eje esperado:",
        f"{observed_expected_axis:+.6f}"
    )

    print(
        "Coherencia bruta con la dirección esperada:",
        "SI" if direction_ok else "NO"
    )

    print("\nCorrelaciones:")
    for key, value in corr_values.items():
        print(f"  {key} = {value:+.6f}")


# =========================================================
# GUARDAR CSV
# =========================================================

summary_csv = os.path.join(
    RESULTS_DIR,
    "diagnostico_tetra_canales_originales.csv"
)

corr_csv = os.path.join(
    RESULTS_DIR,
    "diagnostico_tetra_correlaciones.csv"
)

if rows:
    with open(
        summary_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)

if corr_rows:
    with open(
        corr_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=corr_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(corr_rows)


# =========================================================
# GRÁFICAS
# =========================================================

if HAS_MATPLOTLIB and rows:

    labels = [r["direccion"] for r in rows]
    x = np.arange(len(labels))
    width = 0.19

    # -----------------------------------------------------
    # Gráfica 1: RMS de los cuatro canales originales
    # -----------------------------------------------------

    fig, ax = plt.subplots(figsize=(11, 5))

    ax.bar(
        x - 1.5 * width,
        [r["RMS_C1_FLU"] for r in rows],
        width,
        label="C1 FLU"
    )

    ax.bar(
        x - 0.5 * width,
        [r["RMS_C2_FRD"] for r in rows],
        width,
        label="C2 FRD"
    )

    ax.bar(
        x + 0.5 * width,
        [r["RMS_C3_BLD"] for r in rows],
        width,
        label="C3 BLD"
    )

    ax.bar(
        x + 1.5 * width,
        [r["RMS_C4_BRU"] for r in rows],
        width,
        label="C4 BRU"
    )

    ax.set_title(
        "RMS de los cuatro canales originales del banco tetra"
    )

    ax.set_xlabel("Dirección física")
    ax.set_ylabel("RMS")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "diagnostico_tetra_RMS_canales_originales.png"
        ),
        dpi=200
    )

    plt.close(fig)

    # -----------------------------------------------------
    # Gráfica 2: balances físicos X/Y/Z
    # -----------------------------------------------------

    fig, ax = plt.subplots(figsize=(11, 5))

    ax.bar(
        x - width,
        [r["balance_X_frente_menos_atras"] for r in rows],
        width,
        label="Balance X"
    )

    ax.bar(
        x,
        [r["balance_Y_izquierda_menos_derecha"] for r in rows],
        width,
        label="Balance Y"
    )

    ax.bar(
        x + width,
        [r["balance_Z_arriba_menos_abajo"] for r in rows],
        width,
        label="Balance Z"
    )

    ax.axhline(0.0, linewidth=1)

    ax.set_title(
        "Balances de energía en las grabaciones A-format originales"
    )

    ax.set_xlabel("Dirección física")
    ax.set_ylabel("Balance normalizado")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        os.path.join(
            RESULTS_DIR,
            "diagnostico_tetra_balances_originales.png"
        ),
        dpi=200
    )

    plt.close(fig)


# =========================================================
# RESUMEN FINAL
# =========================================================

print()
print("=" * 90)
print("RESUMEN DEL DIAGNÓSTICO")
print("=" * 90)

for r in rows:
    status = (
        "COHERENTE"
        if r["coherencia_bruta_direccion"]
        else "REVISAR"
    )

    print(
        f"{r['direccion']:>2} "
        f"{r['interpretacion']:<10} | "
        f"X={r['balance_X_frente_menos_atras']:+.4f} "
        f"Y={r['balance_Y_izquierda_menos_derecha']:+.4f} "
        f"Z={r['balance_Z_arriba_menos_abajo']:+.4f} | "
        f"{status}"
    )

print()
print("Archivos generados:")

if rows:
    print("-", summary_csv)

if corr_rows:
    print("-", corr_csv)

if HAS_MATPLOTLIB and rows:
    print(
        "-",
        os.path.join(
            RESULTS_DIR,
            "diagnostico_tetra_RMS_canales_originales.png"
        )
    )
    print(
        "-",
        os.path.join(
            RESULTS_DIR,
            "diagnostico_tetra_balances_originales.png"
        )
    )

print()
print(
    "Interpretación principal:"
)
print(
    "Si una grabación ya presenta en los canales A-format un balance "
    "contrario a su etiqueta física, el problema está antes de la conversión FOA "
    "(captura, orientación, etiquetado o calibración)."
)
print(
    "Si el balance bruto sí coincide con la dirección física pero el FOA no, "
    "entonces se debe revisar la matriz/convención usada por tetra_aformat_to_foa()."
)
