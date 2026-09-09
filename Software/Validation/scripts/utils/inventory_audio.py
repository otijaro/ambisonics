import os
import csv
import soundfile as sf


# =========================================================
# RUTAS DEL PROYECTO
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VALIDATION_DIR = os.path.dirname(SCRIPT_DIR)

AUDIO_ROOT = os.path.join(
    VALIDATION_DIR,
    "audios_tests"
)

RESULTS_DIR = os.path.join(
    VALIDATION_DIR,
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# =========================================================
# FUNCIONES DE CLASIFICACIÓN
# =========================================================

def identificar_banco(ruta):
    ruta = ruta.lower()

    if "stereo_tests" in ruta:
        return "Banco de señales estéreo"

    if "studio_4mic" in ruta:
        return "Banco experimental de cuatro micrófonos"

    if "auxiliary_spatial_tests" in ruta:
        return "Banco auxiliar de señales espaciales"

    return "Otro"


def identificar_tipo(nombre):
    nombre = nombre.lower()

    if "impulso" in nombre:
        return "Impulso"

    if "tono_1khz" in nombre:
        return "Tono sinusoidal 1 kHz"

    if "ruido_blanco" in nombre:
        return "Ruido blanco"

    if "cancion" in nombre:
        return "Audio musical"

    if "alternating" in nombre:
        return "Tono con alternancia espacial"

    if "sweep" in nombre:
        return "Barrido espacial"

    if "center" in nombre:
        return "Señal espacial central"

    if "left" in nombre:
        return "Señal espacial izquierda"

    if "right" in nombre:
        return "Señal espacial derecha"

    return "Grabación experimental"


def identificar_rol(nombre, banco):
    nombre = nombre.lower()

    if banco == "Banco experimental de cuatro micrófonos":
        if nombre.startswith("output_"):
            return "Salida previa de procesamiento"
        else:
            return "Entrada original"

    return "Señal de prueba"


# =========================================================
# INVENTARIAR
# =========================================================

extensiones = (
    ".wav",
    ".flac",
    ".aiff",
    ".aif"
)

inventario = []

for carpeta_actual, subcarpetas, archivos in os.walk(AUDIO_ROOT):

    for archivo in archivos:

        if not archivo.lower().endswith(extensiones):
            continue

        ruta_completa = os.path.join(
            carpeta_actual,
            archivo
        )

        ruta_relativa = os.path.relpath(
            ruta_completa,
            AUDIO_ROOT
        )

        banco = identificar_banco(ruta_completa)
        tipo = identificar_tipo(archivo)
        rol = identificar_rol(archivo, banco)

        try:

            info = sf.info(ruta_completa)

            canales = info.channels
            fs = info.samplerate
            muestras = info.frames
            duracion = info.duration
            formato = info.format
            subtipo = info.subtype

            tamano_mb = (
                os.path.getsize(ruta_completa)
                / (1024 ** 2)
            )

            subcarpeta = os.path.relpath(
                carpeta_actual,
                AUDIO_ROOT
            )

            inventario.append({
                "Banco": banco,
                "Subcarpeta": subcarpeta,
                "Archivo": archivo,
                "Tipo_señal": tipo,
                "Rol": rol,
                "Canales": canales,
                "Frecuencia_muestreo_Hz": fs,
                "Muestras": muestras,
                "Duracion_s": round(duracion, 3),
                "Formato": formato,
                "Subtipo": subtipo,
                "Tamaño_MB": round(tamano_mb, 3),
                "Ruta_relativa": ruta_relativa
            })

        except Exception as e:

            print(
                f"ERROR leyendo {ruta_relativa}: {e}"
            )


# =========================================================
# ORDENAR
# =========================================================

inventario.sort(
    key=lambda x: (
        x["Banco"],
        x["Subcarpeta"],
        x["Archivo"]
    )
)


# =========================================================
# GUARDAR CSV
# =========================================================

columnas = [
    "Banco",
    "Subcarpeta",
    "Archivo",
    "Tipo_señal",
    "Rol",
    "Canales",
    "Frecuencia_muestreo_Hz",
    "Muestras",
    "Duracion_s",
    "Formato",
    "Subtipo",
    "Tamaño_MB",
    "Ruta_relativa"
]


def guardar_csv(nombre, filas):

    ruta = os.path.join(
        RESULTS_DIR,
        nombre
    )

    with open(
        ruta,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columnas,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(filas)

    return ruta


# Inventario completo
ruta_general = guardar_csv(
    "inventario_audios.csv",
    inventario
)


# Inventarios individuales
bancos = {
    "Banco de señales estéreo":
        "inventario_stereo_tests.csv",

    "Banco experimental de cuatro micrófonos":
        "inventario_studio_4mic.csv",

    "Banco auxiliar de señales espaciales":
        "inventario_auxiliary_spatial_tests.csv"
}


rutas_generadas = [ruta_general]

for banco, nombre_csv in bancos.items():

    filas = [
        x for x in inventario
        if x["Banco"] == banco
    ]

    ruta = guardar_csv(
        nombre_csv,
        filas
    )

    rutas_generadas.append(ruta)


# =========================================================
# RESUMEN
# =========================================================

print()
print("=" * 70)
print("INVENTARIO DE AUDIOS GENERADO")
print("=" * 70)

print(f"\nTotal de archivos encontrados: {len(inventario)}")

for banco in bancos:

    cantidad = sum(
        1 for x in inventario
        if x["Banco"] == banco
    )

    print(
        f"- {banco}: {cantidad} archivos"
    )

print("\nArchivos generados:")

for ruta in rutas_generadas:
    print(f"- {ruta}")

print()
print("=" * 70)