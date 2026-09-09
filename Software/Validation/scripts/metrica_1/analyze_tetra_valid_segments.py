"""
======================================================================
MÉTRICA 1 - ANÁLISIS DE SEGMENTOS VÁLIDOS DEL BANCO DE 4 MICRÓFONOS
======================================================================

Objetivo
--------
Evaluar el comportamiento espacial del conversor FOA utilizando
únicamente los intervalos de las grabaciones experimentales donde
la fuente permanece fija en una dirección conocida.

Las grabaciones originales contienen, además de la fuente fija:

- voz de identificación,
- silencios,
- desplazamientos de la fuente,
- otros eventos acústicos.

Por esta razón, la evaluación direccional definitiva NO se realiza
sobre la grabación completa.

Flujo
-----
Grabación A-format original de 4 canales
                ↓
Selección del segmento válido
                ↓
tetra_aformat_to_foa() de core_dsp.py
                ↓
W, X, Y, Z
                ↓
RMS + coeficientes con signo
                ↓
Verificación de eje y signo esperado
                ↓
CSV + FOA de evidencia

Convención física utilizada
----------------------------
+X = Frente
-X = Atrás

+Y = Izquierda
-Y = Derecha

+Z = Arriba
-Z = Abajo

Convención FOA guardada
-----------------------
AmbiX / ACN:

Canal 1 = W  (ACN 0)
Canal 2 = Y  (ACN 1)
Canal 3 = Z  (ACN 2)
Canal 4 = X  (ACN 3)

Salida principal
----------------
results/metrica_1/csv/
    resultados_metrica_1_tetra_segmentos_validos.csv

Los FOA correspondientes a cada segmento válido se guardan en:

results/metrica_1/foa_generados/segmentos_validos_tetra/

Este CSV será utilizado posteriormente por:

    plot_foa_results.py

para generar las tablas y gráficas direccionales definitivas.
======================================================================
"""

import os
import sys
import re

import numpy as np
import pandas as pd
import soundfile as sf


# =====================================================================
# 1. RUTAS
# =====================================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Script:
# validation/scripts/metrica_1/analyze_tetra_valid_segments.py
#
# Subimos:
# metrica_1 -> scripts -> validation

VALIDATION_DIR = os.path.dirname(
    os.path.dirname(CURRENT_DIR)
)

PROJECT_DIR = os.path.dirname(
    VALIDATION_DIR
)


TETRA_DIR = os.path.join(
    VALIDATION_DIR,
    "audios_tests",
    "2. studio_4mic"
)


RESULT_ROOT = os.path.join(
    VALIDATION_DIR,
    "results",
    "metrica_1"
)


CSV_DIR = os.path.join(
    RESULT_ROOT,
    "csv"
)


FOA_ROOT = os.path.join(
    RESULT_ROOT,
    "foa_generados"
)


FOA_SEGMENT_DIR = os.path.join(
    FOA_ROOT,
    "segmentos_validos_tetra"
)


os.makedirs(
    CSV_DIR,
    exist_ok=True
)


os.makedirs(
    FOA_SEGMENT_DIR,
    exist_ok=True
)


OUTPUT_CSV = os.path.join(
    CSV_DIR,
    "resultados_metrica_1_tetra_segmentos_validos.csv"
)


# =====================================================================
# 2. LOCALIZAR BACKEND
# =====================================================================

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


# =====================================================================
# 3. IMPORTAR CONVERSOR REAL
# =====================================================================

from core_dsp import tetra_aformat_to_foa


# =====================================================================
# 4. SEGMENTOS VÁLIDOS DEFINIDOS MEDIANTE ESCUCHA
# =====================================================================

# Estructura:
#
# carpeta,
# interpretación,
# eje esperado,
# signo esperado,
# inicio [s],
# fin [s]

SEGMENTS = [

    (
        "EJE +X",
        "Frente",
        "X",
        +1,
        5.1,
        14.0
    ),

    (
        "EJE -X",
        "Atrás",
        "X",
        -1,
        5.6,
        12.0
    ),

    (
        "EJE +Y",
        "Izquierda",
        "Y",
        +1,
        7.0,
        13.0
    ),

    (
        "EJE -Y",
        "Derecha",
        "Y",
        -1,
        5.0,
        9.0
    ),

    (
        "EJE +Z",
        "Arriba",
        "Z",
        +1,
        7.0,
        12.0
    ),

    (
        "EJE -Z",
        "Abajo",
        "Z",
        -1,
        5.0,
        12.0
    )
]


# =====================================================================
# 5. FUNCIONES AUXILIARES
# =====================================================================

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
    Calcula la proyección de una componente sobre W:

        coef = (W^T · componente) / (W^T · W)

    Conserva el signo y permite distinguir, por ejemplo:

        +Y -> coeficiente Y/W positivo
        -Y -> coeficiente Y/W negativo
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
    Convierte texto en un nombre válido de archivo.
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


def find_original_tetra(folder_path):
    """
    Busca el WAV ORIGINAL de cuatro canales dentro de la carpeta.

    Excluye todas las salidas de procesamiento:
    - FOA
    - binaural
    - 3D perceptual
    - Notebook_output...
    - Web_output...
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
        "foa",
        "binaural",
        "perceptual",
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


        if info.channels < 4:

            continue


        candidates.append(
            path
        )


    if not candidates:

        return None


    candidates.sort(
        key=lambda path: len(
            os.path.basename(path)
        )
    )


    return candidates[0]


def extract_foa_components(result):
    """
    Extrae W, X, Y y Z de la salida de tetra_aformat_to_foa().
    """

    if isinstance(
        result,
        (tuple, list)
    ):


        if len(result) < 4:

            raise ValueError(
                "El conversor devolvió menos de cuatro componentes."
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


    else:


        matrix = np.asarray(
            result
        )


        if (
            matrix.ndim != 2
            or matrix.shape[1] < 4
        ):

            raise ValueError(
                "La salida del conversor no tiene estructura FOA válida."
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
            "W, X, Y y Z no tienen el mismo número de muestras."
        )


    return (
        W,
        X,
        Y,
        Z
    )


# =====================================================================
# 6. ANALIZAR CADA SEGMENTO
# =====================================================================

results = []


print()

print(
    "=" * 92
)

print(
    "MÉTRICA 1 - ANÁLISIS DIRECCIONAL DE SEGMENTOS VÁLIDOS"
)

print(
    "=" * 92
)


for (
    folder_name,
    interpretation,
    expected_axis,
    expected_sign,
    t_start,
    t_end
) in SEGMENTS:


    # -----------------------------------------------------------------
    # Buscar grabación original
    # -----------------------------------------------------------------

    folder_path = os.path.join(
        TETRA_DIR,
        folder_name
    )


    original_file = find_original_tetra(
        folder_path
    )


    if original_file is None:


        print()

        print(
            "ADVERTENCIA:"
        )

        print(
            f"No se encontró el WAV original para {folder_name}"
        )

        continue


    # -----------------------------------------------------------------
    # Leer grabación
    # -----------------------------------------------------------------

    audio, sr = sf.read(
        original_file,
        dtype="float32",
        always_2d=True
    )


    if audio.shape[1] < 4:

        print()

        print(
            f"ERROR: {os.path.basename(original_file)} "
            f"tiene solamente {audio.shape[1]} canales."
        )

        continue


    audio = audio[:, :4]


    total_samples = int(
        len(audio)
    )


    total_duration = (
        total_samples
        / sr
    )


    # -----------------------------------------------------------------
    # Asegurar que el intervalo esté dentro del archivo
    # -----------------------------------------------------------------

    t_start_use = max(
        0.0,
        t_start
    )


    t_end_use = min(
        total_duration,
        t_end
    )


    if t_end_use <= t_start_use:

        print()

        print(
            f"ERROR: intervalo inválido para {folder_name}"
        )

        continue


    # -----------------------------------------------------------------
    # Convertir tiempos a índices
    # -----------------------------------------------------------------

    sample_start = int(
        round(
            t_start_use
            * sr
        )
    )


    sample_end = int(
        round(
            t_end_use
            * sr
        )
    )


    segment = audio[
        sample_start:sample_end,
        :
    ]


    if len(segment) == 0:

        print()

        print(
            f"ERROR: segmento vacío para {folder_name}"
        )

        continue


    # -----------------------------------------------------------------
    # Procesar el SEGMENTO con la función REAL del backend
    # -----------------------------------------------------------------

    conversion_result = tetra_aformat_to_foa(
        segment
    )


    W, X, Y, Z = extract_foa_components(
        conversion_result
    )


    # -----------------------------------------------------------------
    # RMS
    # -----------------------------------------------------------------

    rms_W = rms(W)
    rms_X = rms(X)
    rms_Y = rms(Y)
    rms_Z = rms(Z)


    # -----------------------------------------------------------------
    # Relaciones RMS respecto a W
    #
    # Magnitud, sin información de signo.
    # -----------------------------------------------------------------

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


    # -----------------------------------------------------------------
    # Coeficientes con signo
    # -----------------------------------------------------------------

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


    coefficient_map = {

        "X": coef_X_W,
        "Y": coef_Y_W,
        "Z": coef_Z_W

    }


    # -----------------------------------------------------------------
    # Componente dominante por RMS
    # -----------------------------------------------------------------

    directional_rms = {

        "X": rms_X,
        "Y": rms_Y,
        "Z": rms_Z

    }


    dominant_component = max(
        directional_rms,
        key=directional_rms.get
    )


    # -----------------------------------------------------------------
    # Componente con mayor coeficiente absoluto
    # -----------------------------------------------------------------

    dominant_coefficient_component = max(

        coefficient_map,

        key=lambda axis: abs(
            coefficient_map[axis]
        )

    )


    # -----------------------------------------------------------------
    # Evaluar eje esperado
    # -----------------------------------------------------------------

    expected_coefficient = (
        coefficient_map[
            expected_axis
        ]
    )


    sign_coherent = (

        expected_sign
        * expected_coefficient

    ) > 0


    rms_dominance_coherent = (

        dominant_component
        == expected_axis

    )


    coefficient_dominance_coherent = (

        dominant_coefficient_component
        == expected_axis

    )


    # -----------------------------------------------------------------
    # NaN / Inf
    # -----------------------------------------------------------------

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


    # -----------------------------------------------------------------
    # Picos
    # -----------------------------------------------------------------

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


    # -----------------------------------------------------------------
    # Clipping
    # -----------------------------------------------------------------

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


    # -----------------------------------------------------------------
    # Guardar FOA del segmento
    #
    # AmbiX / ACN:
    #
    # W, Y, Z, X
    # -----------------------------------------------------------------

    foa_acn = np.column_stack(
        [
            W,
            Y,
            Z,
            X
        ]
    )


    output_filename = sanitize_filename(

        f"{folder_name}_{interpretation}_"
        f"segmento_valido_FOA_AmbiX.wav"

    )


    output_path = os.path.join(
        FOA_SEGMENT_DIR,
        output_filename
    )


    sf.write(
        output_path,
        foa_acn,
        sr,
        subtype="FLOAT"
    )


    # -----------------------------------------------------------------
    # Guardar fila de resultados
    # -----------------------------------------------------------------

    result = {

        "Banco":
            "4_microfonos_segmento_valido",

        "Condicion":
            folder_name,

        "Interpretacion":
            interpretation,

        "Archivo_original":
            os.path.basename(
                original_file
            ),

        "Inicio_segmento_s":
            t_start_use,

        "Fin_segmento_s":
            t_end_use,

        "Duracion_segmento_s":
            t_end_use
            - t_start_use,

        "Frecuencia_muestreo_Hz":
            sr,

        "Canales_entrada":
            4,

        "Canales_FOA":
            4,

        "Orden_FOA_guardado":
            "W,Y,Z,X (ACN 0,1,2,3)",

        "Muestras_entrada":
            len(segment),

        "Muestras_FOA":
            len(W),

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

        "Eje_esperado":
            expected_axis,

        "Signo_esperado":
            expected_sign,

        "Coeficiente_eje_esperado":
            expected_coefficient,

        "Signo_coherente":
            sign_coherent,

        "Componente_direccional_dominante_RMS":
            dominant_component,

        "Predominio_RMS_coherente":
            rms_dominance_coherent,

        "Componente_coeficiente_dominante":
            dominant_coefficient_component,

        "Predominio_coeficiente_coherente":
            coefficient_dominance_coherent,

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


    results.append(
        result
    )


    # -----------------------------------------------------------------
    # Mostrar resultado en consola
    # -----------------------------------------------------------------

    print()

    print(
        "-" * 92
    )


    print(
        f"{folder_name} | {interpretation}"
    )


    print(
        "-" * 92
    )


    print(
        "Archivo original:",
        os.path.basename(
            original_file
        )
    )


    print(
        f"Segmento válido: "
        f"{t_start_use:.2f} - {t_end_use:.2f} s "
        f"({t_end_use - t_start_use:.2f} s)"
    )


    print(
        "RMS W/X/Y/Z:",
        f"{rms_W:.6f}",
        f"{rms_X:.6f}",
        f"{rms_Y:.6f}",
        f"{rms_Z:.6f}"
    )


    print(
        "Coef. X/W Y/W Z/W:",
        f"{coef_X_W:+.6f}",
        f"{coef_Y_W:+.6f}",
        f"{coef_Z_W:+.6f}"
    )


    print(
        "Eje esperado:",
        expected_axis
    )


    print(
        "Signo esperado:",
        f"{expected_sign:+d}"
    )


    print(
        "Coeficiente del eje esperado:",
        f"{expected_coefficient:+.6f}"
    )


    print(
        "Signo coherente:",
        sign_coherent
    )


    print(
        "Dominante RMS:",
        dominant_component,
        "| coherente:",
        rms_dominance_coherent
    )


    print(
        "Dominante por coeficiente:",
        dominant_coefficient_component,
        "| coherente:",
        coefficient_dominance_coherent
    )


    print(
        "NaN:",
        nan_count,
        "| Inf:",
        inf_count,
        "| Clipping:",
        clipping
    )


# =====================================================================
# 7. GUARDAR CSV
# =====================================================================

df_results = pd.DataFrame(
    results
)


df_results.to_csv(
    OUTPUT_CSV,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)


# =====================================================================
# 8. RESUMEN FINAL
# =====================================================================

print()

print(
    "=" * 92
)

print(
    "ANÁLISIS DE SEGMENTOS VÁLIDOS COMPLETADO"
)

print(
    "=" * 92
)


print()

print(
    "Direcciones analizadas:",
    len(
        df_results
    )
)


print()

print(
    "CSV generado:"
)

print(
    OUTPUT_CSV
)


print()

print(
    "FOA de los segmentos válidos:"
)

print(
    FOA_SEGMENT_DIR
)


if len(df_results) > 0:


    sign_pass = int(

        df_results[
            "Signo_coherente"
        ].sum()

    )


    rms_pass = int(

        df_results[
            "Predominio_RMS_coherente"
        ].sum()

    )


    coef_pass = int(

        df_results[
            "Predominio_coeficiente_coherente"
        ].sum()

    )


    print()

    print(
        "Resumen espacial:"
    )


    print(
        f"- Signo esperado correcto: "
        f"{sign_pass}/{len(df_results)}"
    )


    print(
        f"- Predominio RMS correcto: "
        f"{rms_pass}/{len(df_results)}"
    )


    print(
        f"- Predominio por coeficiente correcto: "
        f"{coef_pass}/{len(df_results)}"
    )


    print()

    print(
        "Validación numérica:"
    )


    print(
        "- NaN totales:",
        int(
            df_results[
                "NaN_count"
            ].sum()
        )
    )


    print(
        "- Inf totales:",
        int(
            df_results[
                "Inf_count"
            ].sum()
        )
    )


    print(
        "- Casos con clipping:",
        int(
            df_results[
                "Clipping"
            ].sum()
        )
    )


print()

print(
    "SIGUIENTE PASO:"
)

print(
    "Ejecutar plot_foa_results.py para generar las tablas y "
    "gráficas definitivas de la Métrica 1."
)


print()

print(
    "=" * 92
)