"""
====================================================================
MÉTRICA 1 - VERIFICACIÓN ESTRUCTURAL DEL FOA
====================================================================

Objetivo
--------
Validar directamente el conversor Ambisonics implementado en
core_dsp.py a partir de los audios ORIGINALES del banco de pruebas.

Flujo
-----
Audio original
      ↓
Funciones reales de core_dsp.py
      ↓
W, X, Y, Z
      ↓
Empaquetado FOA AmbiX / ACN
      ↓
Guardado del FOA generado
      ↓
Cálculo de métricas estructurales

Se verifica
-----------
- Número de canales de entrada.
- Número de canales FOA.
- Frecuencia de muestreo.
- Número de muestras.
- Duración.
- RMS de W, X, Y y Z.
- Relaciones RMS respecto a W.
- Coeficientes direccionales con signo respecto a W.
- Componente direccional dominante por RMS.
- Pico máximo.
- NaN.
- Inf.
- Muestras fuera del rango [-1, 1].
- Clipping.

Convención del archivo FOA guardado
-----------------------------------
AmbiX / ACN:

Canal 1 = W  (ACN 0)
Canal 2 = Y  (ACN 1)
Canal 3 = Z  (ACN 2)
Canal 4 = X  (ACN 3)

IMPORTANTE
----------
Este script NO utiliza:

- Notebook_output_foa.wav
- Notebook_output_binaural.wav
- Notebook_output_binaural_3D_perceptual.wav
- archivos descargados desde la página web

La entrada de esta prueba es siempre el AUDIO ORIGINAL y la
conversión se realiza llamando directamente las funciones del backend.

Para el banco experimental de cuatro micrófonos, este script calcula
los coeficientes utilizando la grabación completa como caracterización
estructural inicial. La comprobación espacial definitiva debe realizarse
posteriormente sobre los segmentos donde la fuente permanece fija
mediante analyze_tetra_valid_segments.py.
====================================================================
"""

import os
import sys
import re

import numpy as np
import pandas as pd
import soundfile as sf


# ====================================================================
# 1. RUTAS DEL PROYECTO
# ====================================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Script:
# validation/scripts/metrica_1/analyze_foa_structure.py
#
# CURRENT_DIR       -> validation/scripts/metrica_1
# dirname 1         -> validation/scripts
# dirname 2         -> validation

VALIDATION_DIR = os.path.dirname(
    os.path.dirname(CURRENT_DIR)
)

PROJECT_DIR = os.path.dirname(
    VALIDATION_DIR
)


# --------------------------------------------------------------------
# Banco de audios
# --------------------------------------------------------------------

AUDIO_ROOT = os.path.join(
    VALIDATION_DIR,
    "audios_tests"
)

STEREO_DIR = os.path.join(
    AUDIO_ROOT,
    "1. stereo_tests"
)

TETRA_DIR = os.path.join(
    AUDIO_ROOT,
    "2. studio_4mic"
)


# --------------------------------------------------------------------
# Carpeta raíz de resultados de la Métrica 1
# --------------------------------------------------------------------

RESULT_ROOT = os.path.join(
    VALIDATION_DIR,
    "results",
    "metrica_1"
)

CSV_DIR = os.path.join(
    RESULT_ROOT,
    "csv"
)

TABLE_DIR = os.path.join(
    RESULT_ROOT,
    "tablas"
)

GRAPH_DIR = os.path.join(
    RESULT_ROOT,
    "graficas"
)

FOA_OUTPUT_DIR = os.path.join(
    RESULT_ROOT,
    "foa_generados"
)


# Crear automáticamente toda la estructura

for folder in [
    RESULT_ROOT,
    CSV_DIR,
    TABLE_DIR,
    GRAPH_DIR,
    FOA_OUTPUT_DIR
]:
    os.makedirs(
        folder,
        exist_ok=True
    )


# ====================================================================
# 2. LOCALIZAR EL BACKEND
# ====================================================================

backend_candidates = [

    os.path.join(
        PROJECT_DIR,
        "ambisonics_backend"
    ),

    os.path.join(
        PROJECT_DIR,
        "Web Site",
        "backend"
    ),

    os.path.join(
        PROJECT_DIR,
        "backend"
    )
]


BACKEND_DIR = next(
    (
        path
        for path in backend_candidates
        if os.path.isdir(path)
    ),
    None
)


if BACKEND_DIR is None:

    raise FileNotFoundError(
        "No se encontró el backend del proyecto.\n"
        "Rutas revisadas:\n- "
        + "\n- ".join(backend_candidates)
    )


sys.path.insert(
    0,
    BACKEND_DIR
)


# ====================================================================
# 3. IMPORTAR FUNCIONES REALES DEL CONVERSOR
# ====================================================================

from core_dsp import (
    stereo_to_foa,
    tetra_aformat_to_foa
)


# ====================================================================
# 4. PRUEBAS SELECCIONADAS
# ====================================================================

# --------------------------------------------------------------------
# Banco estéreo
#
# Se utilizan las pruebas A01-A05.
# A02 contiene tres condiciones controladas.
# --------------------------------------------------------------------

STEREO_TESTS = [

    (
        "A01_impulso_center",
        "Impulso central"
    ),

    (
        "A02_tono_1kHz_center",
        "Tono 1 kHz - centro"
    ),

    (
        "A02_tono_1kHz_left",
        "Tono 1 kHz - izquierda"
    ),

    (
        "A02_tono_1kHz_right",
        "Tono 1 kHz - derecha"
    ),

    (
        "A03_ruido_blanco_30s",
        "Ruido blanco 30 s"
    ),

    (
        "A04_cancion_corta_30s",
        "Audio musical 30 s"
    ),

    (
        "A05_cancion_corta_1min",
        "Audio musical 1 min"
    )
]


# --------------------------------------------------------------------
# Banco experimental de cuatro micrófonos
#
# Solamente se analizan los seis ejes principales.
# Las ocho posiciones diagonales quedan excluidas de esta métrica.
# --------------------------------------------------------------------

TETRA_TESTS = [

    (
        "EJE +X",
        "Frente",
        "X",
        +1
    ),

    (
        "EJE -X",
        "Atrás",
        "X",
        -1
    ),

    (
        "EJE +Y",
        "Izquierda",
        "Y",
        +1
    ),

    (
        "EJE -Y",
        "Derecha",
        "Y",
        -1
    ),

    (
        "EJE +Z",
        "Arriba",
        "Z",
        +1
    ),

    (
        "EJE -Z",
        "Abajo",
        "Z",
        -1
    )
]


# ====================================================================
# 5. FUNCIONES AUXILIARES
# ====================================================================

def rms(signal):
    """
    Calcula el valor RMS de una señal.
    """

    signal = np.asarray(
        signal,
        dtype=np.float64
    )

    return float(
        np.sqrt(
            np.mean(
                np.square(signal)
            )
        )
    )


def relative_coefficient(reference, signal):
    """
    Calcula la proyección de una componente direccional sobre W.

    coef = (W^T · componente) / (W^T · W)

    A diferencia de RMS_X/RMS_W, esta operación conserva el signo.
    """

    reference = np.asarray(
        reference,
        dtype=np.float64
    )

    signal = np.asarray(
        signal,
        dtype=np.float64
    )

    denominator = (
        np.dot(
            reference,
            reference
        )
        + 1e-12
    )

    return float(
        np.dot(
            reference,
            signal
        )
        / denominator
    )


def sanitize_filename(text):
    """
    Convierte un texto en un nombre seguro para archivo.
    """

    text = (
        text
        .replace("+", "plus_")
        .replace("-", "minus_")
        .replace(" ", "_")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
    )

    return re.sub(
        r"[^A-Za-z0-9_.]",
        "_",
        text
    )


def find_original_wav(folder_path, expected_mode):
    """
    Busca automáticamente el WAV ORIGINAL de una carpeta.

    Se excluyen todas las salidas procesadas:
    - Notebook_output...
    - Web_output...
    - FOA
    - binaural
    - 3D perceptual
    - etc.

    expected_mode:
        "stereo"
        "tetra"
    """

    if not os.path.isdir(
        folder_path
    ):

        return None


    excluded_terms = [

        "notebook_output",
        "web_output",
        "pagina_output",
        "output_",
        "binaural",
        "perceptual",
        "foa",
        "speaker",
        "parlante",
        "render",
        "3d"
    ]


    candidates = []


    for filename in os.listdir(
        folder_path
    ):

        if not filename.lower().endswith(
            ".wav"
        ):

            continue


        name_lower = filename.lower()


        if any(
            term in name_lower
            for term in excluded_terms
        ):

            continue


        path = os.path.join(
            folder_path,
            filename
        )


        try:

            info = sf.info(
                path
            )

        except Exception:

            continue


        # Entrada estéreo: exactamente 2 canales

        if expected_mode == "stereo":

            if info.channels != 2:

                continue


        # Entrada tetra: al menos 4 canales

        elif expected_mode == "tetra":

            if info.channels < 4:

                continue


        candidates.append(
            path
        )


    if not candidates:

        return None


    # Si hubiera más de uno, preferir nombre más corto

    candidates.sort(
        key=lambda path: len(
            os.path.basename(path)
        )
    )


    return candidates[0]


def extract_foa_components(result):
    """
    Extrae W, X, Y, Z independientemente del formato de salida
    utilizado por las funciones del backend.

    Caso actual de stereo_to_foa:
        tuple/list con W, X, Y, Z, ...

    También admite una matriz N x 4.
    """

    # ---------------------------------------------------------------
    # Tuple/list
    # ---------------------------------------------------------------

    if isinstance(
        result,
        (tuple, list)
    ):

        if len(result) < 4:

            raise ValueError(
                "El conversor devolvió menos de cuatro componentes FOA."
            )


        W = np.asarray(
            result[0],
            dtype=np.float64
        )

        X = np.asarray(
            result[1],
            dtype=np.float64
        )

        Y = np.asarray(
            result[2],
            dtype=np.float64
        )

        Z = np.asarray(
            result[3],
            dtype=np.float64
        )


    # ---------------------------------------------------------------
    # Matriz
    # ---------------------------------------------------------------

    else:

        matrix = np.asarray(
            result
        )


        if (
            matrix.ndim != 2
            or matrix.shape[1] < 4
        ):

            raise ValueError(
                "El conversor no devolvió una estructura FOA válida."
            )


        W = np.asarray(
            matrix[:, 0],
            dtype=np.float64
        )

        X = np.asarray(
            matrix[:, 1],
            dtype=np.float64
        )

        Y = np.asarray(
            matrix[:, 2],
            dtype=np.float64
        )

        Z = np.asarray(
            matrix[:, 3],
            dtype=np.float64
        )


    # ---------------------------------------------------------------
    # Verificación de longitud
    # ---------------------------------------------------------------

    lengths = [
        len(W),
        len(X),
        len(Y),
        len(Z)
    ]


    if len(
        set(lengths)
    ) != 1:

        raise ValueError(
            "Las componentes W, X, Y y Z no tienen la misma longitud."
        )


    return (
        W,
        X,
        Y,
        Z
    )


# ====================================================================
# 6. ANÁLISIS DE UNA CONVERSIÓN
# ====================================================================

def analyze_conversion(
    input_path,
    bank,
    condition,
    interpretation,
    mode,
    expected_axis=None,
    expected_sign=None
):

    # ----------------------------------------------------------------
    # Leer audio ORIGINAL
    # ----------------------------------------------------------------

    audio, sr = sf.read(
        input_path,
        dtype="float32",
        always_2d=True
    )


    input_samples = int(
        audio.shape[0]
    )

    input_channels = int(
        audio.shape[1]
    )

    input_duration = (
        input_samples
        / sr
    )


    # ----------------------------------------------------------------
    # Ejecutar el conversor REAL
    # ----------------------------------------------------------------

    if mode == "stereo":

        conversion_result = stereo_to_foa(
            audio,
            sr
        )


    elif mode == "tetra":

        if input_channels < 4:

            raise ValueError(
                f"{input_path} tiene "
                f"{input_channels} canales. "
                "El procesamiento tetra requiere 4."
            )


        conversion_result = tetra_aformat_to_foa(
            audio[:, :4]
        )


    else:

        raise ValueError(
            f"Modo de procesamiento desconocido: {mode}"
        )


    # ----------------------------------------------------------------
    # Obtener componentes WXYZ
    # ----------------------------------------------------------------

    W, X, Y, Z = extract_foa_components(
        conversion_result
    )


    output_samples = int(
        len(W)
    )

    output_channels = 4

    output_duration = (
        output_samples
        / sr
    )


    # ----------------------------------------------------------------
    # RMS
    # ----------------------------------------------------------------

    rms_W = rms(W)
    rms_X = rms(X)
    rms_Y = rms(Y)
    rms_Z = rms(Z)


    # ----------------------------------------------------------------
    # Relaciones RMS respecto a W
    #
    # Sirven para comparar magnitud de energía.
    # NO conservan signo.
    # ----------------------------------------------------------------

    epsilon = 1e-12


    RMS_X_W = (
        rms_X
        / (rms_W + epsilon)
    )

    RMS_Y_W = (
        rms_Y
        / (rms_W + epsilon)
    )

    RMS_Z_W = (
        rms_Z
        / (rms_W + epsilon)
    )


    # ----------------------------------------------------------------
    # Coeficientes direccionales con SIGNO
    # ----------------------------------------------------------------

    coef_X_W = relative_coefficient(
        W,
        X
    )

    coef_Y_W = relative_coefficient(
        W,
        Y
    )

    coef_Z_W = relative_coefficient(
        W,
        Z
    )


    # ----------------------------------------------------------------
    # Componente direccional dominante
    # ----------------------------------------------------------------

    directional_rms = {

        "X": rms_X,
        "Y": rms_Y,
        "Z": rms_Z

    }


    dominant_component = max(
        directional_rms,
        key=directional_rms.get
    )


    # ----------------------------------------------------------------
    # NaN / Inf
    # ----------------------------------------------------------------

    nan_count = int(

        np.isnan(W).sum()
        + np.isnan(X).sum()
        + np.isnan(Y).sum()
        + np.isnan(Z).sum()

    )


    inf_count = int(

        np.isinf(W).sum()
        + np.isinf(X).sum()
        + np.isinf(Y).sum()
        + np.isinf(Z).sum()

    )


    # ----------------------------------------------------------------
    # Pico
    # ----------------------------------------------------------------

    peak_W = float(
        np.max(
            np.abs(W)
        )
    )

    peak_X = float(
        np.max(
            np.abs(X)
        )
    )

    peak_Y = float(
        np.max(
            np.abs(Y)
        )
    )

    peak_Z = float(
        np.max(
            np.abs(Z)
        )
    )


    peak_max = max(
        peak_W,
        peak_X,
        peak_Y,
        peak_Z
    )


    # ----------------------------------------------------------------
    # Clipping
    # ----------------------------------------------------------------

    clipping_samples = int(

        np.sum(
            np.abs(W) > 1.0
        )

        + np.sum(
            np.abs(X) > 1.0
        )

        + np.sum(
            np.abs(Y) > 1.0
        )

        + np.sum(
            np.abs(Z) > 1.0
        )

    )


    clipping = (
        clipping_samples > 0
    )


    # ----------------------------------------------------------------
    # Información de dirección esperada
    #
    # Para tetra esto se conserva como información descriptiva.
    # La conclusión espacial definitiva se realizará utilizando
    # los segmentos válidos de cada grabación.
    # ----------------------------------------------------------------

    if expected_axis is None:

        expected_axis_value = ""

    else:

        expected_axis_value = (
            expected_axis
        )


    if expected_sign is None:

        expected_sign_value = ""

    else:

        expected_sign_value = (
            expected_sign
        )


    # ----------------------------------------------------------------
    # Guardar FOA generado
    #
    # Convención AmbiX / ACN:
    #
    # Canal 1 -> W
    # Canal 2 -> Y
    # Canal 3 -> Z
    # Canal 4 -> X
    # ----------------------------------------------------------------

    foa_acn = np.column_stack(
        [
            W,
            Y,
            Z,
            X
        ]
    )


    output_filename = sanitize_filename(

        f"{bank}_{condition}_FOA_AmbiX.wav"

    )


    output_path = os.path.join(
        FOA_OUTPUT_DIR,
        output_filename
    )


    sf.write(
        output_path,
        foa_acn,
        sr,
        subtype="FLOAT"
    )


    # ----------------------------------------------------------------
    # Resultado de la prueba
    # ----------------------------------------------------------------

    resultado = {

        "Banco":
            bank,

        "Condicion":
            condition,

        "Interpretacion":
            interpretation,

        "Archivo_original":
            os.path.basename(
                input_path
            ),

        "Ruta_original":
            os.path.relpath(
                input_path,
                VALIDATION_DIR
            ),

        "Frecuencia_muestreo_Hz":
            sr,

        "Canales_entrada":
            input_channels,

        "Canales_FOA":
            output_channels,

        "Orden_FOA_guardado":
            "W,Y,Z,X (ACN 0,1,2,3)",

        "Muestras_entrada":
            input_samples,

        "Muestras_FOA":
            output_samples,

        "Duracion_entrada_s":
            input_duration,

        "Duracion_FOA_s":
            output_duration,

        "RMS_W":
            rms_W,

        "RMS_X":
            rms_X,

        "RMS_Y":
            rms_Y,

        "RMS_Z":
            rms_Z,

        "RMS_X_W":
            RMS_X_W,

        "RMS_Y_W":
            RMS_Y_W,

        "RMS_Z_W":
            RMS_Z_W,

        "Coef_X_W":
            coef_X_W,

        "Coef_Y_W":
            coef_Y_W,

        "Coef_Z_W":
            coef_Z_W,

        "Componente_direccional_dominante_RMS":
            dominant_component,

        "Eje_esperado":
            expected_axis_value,

        "Signo_esperado":
            expected_sign_value,

        "Pico_W":
            peak_W,

        "Pico_X":
            peak_X,

        "Pico_Y":
            peak_Y,

        "Pico_Z":
            peak_Z,

        "Pico_maximo":
            peak_max,

        "NaN_count":
            nan_count,

        "Inf_count":
            inf_count,

        "Clipping_samples":
            clipping_samples,

        "Clipping":
            clipping,

        "FOA_guardado":
            os.path.relpath(
                output_path,
                VALIDATION_DIR
            )

    }


    return resultado


# ====================================================================
# 7. EJECUTAR BANCO ESTÉREO
# ====================================================================

stereo_results = []


print()

print(
    "=" * 90
)

print(
    "MÉTRICA 1 - VERIFICACIÓN ESTRUCTURAL DEL FOA"
)

print(
    "=" * 90
)


print()

print(
    "[A] BANCO DE SEÑALES ESTÉREO"
)


for (
    folder_name,
    description
) in STEREO_TESTS:


    folder_path = os.path.join(
        STEREO_DIR,
        folder_name
    )


    original_file = find_original_wav(
        folder_path,
        "stereo"
    )


    if original_file is None:

        print()

        print(
            "ADVERTENCIA:"
        )

        print(
            f"No se encontró audio original en:\n"
            f"{folder_path}"
        )

        continue


    print()

    print(
        f"Procesando: {folder_name}"
    )

    print(
        "Original:",
        os.path.basename(
            original_file
        )
    )


    result = analyze_conversion(

        input_path=
            original_file,

        bank=
            "Stereo",

        condition=
            folder_name,

        interpretation=
            description,

        mode=
            "stereo"

    )


    stereo_results.append(
        result
    )


    print(
        "RMS W/X/Y/Z:",
        f"{result['RMS_W']:.6f}",
        f"{result['RMS_X']:.6f}",
        f"{result['RMS_Y']:.6f}",
        f"{result['RMS_Z']:.6f}"
    )


    print(
        "Coef. X/W Y/W Z/W:",
        f"{result['Coef_X_W']:+.6f}",
        f"{result['Coef_Y_W']:+.6f}",
        f"{result['Coef_Z_W']:+.6f}"
    )


    print(
        "NaN:",
        result["NaN_count"],
        "| Inf:",
        result["Inf_count"],
        "| Clipping:",
        result["Clipping"]
    )


# ====================================================================
# 8. EJECUTAR BANCO EXPERIMENTAL DE CUATRO MICRÓFONOS
# ====================================================================

tetra_results = []


print()

print(
    "[B] BANCO EXPERIMENTAL DE CUATRO MICRÓFONOS"
)


for (
    folder_name,
    interpretation,
    expected_axis,
    expected_sign
) in TETRA_TESTS:


    folder_path = os.path.join(
        TETRA_DIR,
        folder_name
    )


    original_file = find_original_wav(
        folder_path,
        "tetra"
    )


    if original_file is None:

        print()

        print(
            "ADVERTENCIA:"
        )

        print(
            f"No se encontró audio original en:\n"
            f"{folder_path}"
        )

        continue


    print()

    print(
        f"Procesando: "
        f"{folder_name} ({interpretation})"
    )

    print(
        "Original:",
        os.path.basename(
            original_file
        )
    )


    result = analyze_conversion(

        input_path=
            original_file,

        bank=
            "4_microfonos",

        condition=
            folder_name,

        interpretation=
            interpretation,

        mode=
            "tetra",

        expected_axis=
            expected_axis,

        expected_sign=
            expected_sign

    )


    tetra_results.append(
        result
    )


    print(
        "RMS W/X/Y/Z:",
        f"{result['RMS_W']:.6f}",
        f"{result['RMS_X']:.6f}",
        f"{result['RMS_Y']:.6f}",
        f"{result['RMS_Z']:.6f}"
    )


    print(
        "Coef. X/W Y/W Z/W:",
        f"{result['Coef_X_W']:+.6f}",
        f"{result['Coef_Y_W']:+.6f}",
        f"{result['Coef_Z_W']:+.6f}"
    )


    print(
        "NaN:",
        result["NaN_count"],
        "| Inf:",
        result["Inf_count"],
        "| Clipping:",
        result["Clipping"]
    )


# ====================================================================
# 9. CONSTRUIR DATAFRAMES
# ====================================================================

all_results = (
    stereo_results
    + tetra_results
)


df_general = pd.DataFrame(
    all_results
)

df_stereo = pd.DataFrame(
    stereo_results
)

df_tetra = pd.DataFrame(
    tetra_results
)


# ====================================================================
# 10. GUARDAR CSV
# ====================================================================

# Se usa ";" para que Excel en configuración regional española/
# latinoamericana separe correctamente cada dato en su columna.

GENERAL_CSV = os.path.join(
    CSV_DIR,
    "resultados_metrica_1_FOA.csv"
)

STEREO_CSV = os.path.join(
    CSV_DIR,
    "resultados_metrica_1_stereo.csv"
)

TETRA_CSV = os.path.join(
    CSV_DIR,
    "resultados_metrica_1_tetra.csv"
)


df_general.to_csv(
    GENERAL_CSV,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


df_stereo.to_csv(
    STEREO_CSV,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


df_tetra.to_csv(
    TETRA_CSV,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


# ====================================================================
# 11. CREAR EXCEL ORGANIZADO
# ====================================================================

EXCEL_PATH = os.path.join(
    TABLE_DIR,
    "resultados_metrica_1_FOA.xlsx"
)


excel_generated = False


try:

    import openpyxl

    from openpyxl import load_workbook


    # ---------------------------------------------------------------
    # Escribir las tres hojas
    # ---------------------------------------------------------------

    with pd.ExcelWriter(
        EXCEL_PATH,
        engine="openpyxl"
    ) as writer:


        df_general.to_excel(
            writer,
            sheet_name="Resultados generales",
            index=False
        )


        df_stereo.to_excel(
            writer,
            sheet_name="Banco estereo",
            index=False
        )


        df_tetra.to_excel(
            writer,
            sheet_name="Banco 4 microfonos",
            index=False
        )


    # ---------------------------------------------------------------
    # Mejorar presentación del Excel
    # ---------------------------------------------------------------

    workbook = load_workbook(
        EXCEL_PATH
    )


    for worksheet in workbook.worksheets:


        # Congelar encabezado

        worksheet.freeze_panes = "A2"


        # Activar filtro

        worksheet.auto_filter.ref = (
            worksheet.dimensions
        )


        # Ajustar automáticamente anchos

        for column_cells in worksheet.columns:


            max_length = 0


            column_letter = (
                column_cells[0].column_letter
            )


            for cell in column_cells:


                try:

                    value = (
                        ""
                        if cell.value is None
                        else str(cell.value)
                    )


                    if len(value) > max_length:

                        max_length = len(
                            value
                        )


                except Exception:

                    pass


            adjusted_width = min(
                max_length + 2,
                45
            )


            worksheet.column_dimensions[
                column_letter
            ].width = adjusted_width


    workbook.save(
        EXCEL_PATH
    )


    excel_generated = True


except ImportError:

    print()

    print(
        "ADVERTENCIA:"
    )

    print(
        "No se encontró openpyxl."
    )

    print(
        "Los CSV sí fueron generados correctamente."
    )

    print(
        "Para crear también el archivo Excel ejecuta:"
    )

    print(
        "python -m pip install openpyxl"
    )


# ====================================================================
# 12. RESUMEN FINAL
# ====================================================================

print()

print(
    "=" * 90
)

print(
    "MÉTRICA 1 - ANÁLISIS ESTRUCTURAL COMPLETADO"
)

print(
    "=" * 90
)


print()

print(
    "Casos estéreo analizados:",
    len(
        stereo_results
    )
)


print(
    "Casos 4 micrófonos analizados:",
    len(
        tetra_results
    )
)


print(
    "Total:",
    len(
        all_results
    )
)


print()

print(
    "CSV:"
)

print(
    "-",
    GENERAL_CSV
)

print(
    "-",
    STEREO_CSV
)

print(
    "-",
    TETRA_CSV
)


if excel_generated:

    print()

    print(
        "Excel organizado:"
    )

    print(
        "-",
        EXCEL_PATH
    )


print()

print(
    "FOA generados:"
)

print(
    "-",
    FOA_OUTPUT_DIR
)


print()

print(
    "Carpeta reservada para gráficas:"
)

print(
    "-",
    GRAPH_DIR
)


print()

print(
    "Orden de los WAV FOA guardados:"
)

print(
    "Canal 1 -> W (ACN 0)"
)

print(
    "Canal 2 -> Y (ACN 1)"
)

print(
    "Canal 3 -> Z (ACN 2)"
)

print(
    "Canal 4 -> X (ACN 3)"
)


print()

print(
    "NOTA:"
)

print(
    "La direccionalidad definitiva del banco de 4 micrófonos "
    "debe calcularse sobre los segmentos válidos de fuente fija."
)

print(
    "Ese análisis corresponde al script "
    "analyze_tetra_valid_segments.py."
)


print()

print(
    "=" * 90
)