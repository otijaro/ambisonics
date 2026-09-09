"""
======================================================================
MÉTRICA 1 - GENERACIÓN DE TABLAS Y GRÁFICAS FOA
======================================================================

Objetivo
--------
Tomar los resultados numéricos generados previamente por:

    analyze_foa_structure.py

y convertirlos en tablas y gráficas utilizadas como evidencia
de la Métrica 1.

Este script NO vuelve a procesar los audios ni llama a core_dsp.py.

Flujo
-----
Audio original
      ↓
analyze_foa_structure.py
      ↓
CSV de resultados
      ↓
plot_foa_results.py
      ↓
Tablas + gráficas

Para el banco experimental de cuatro micrófonos:

- Los resultados de la grabación completa se consideran una
  caracterización estructural preliminar.

- La conclusión direccional final (+X/-X, +Y/-Y, +Z/-Z)
  debe obtenerse a partir de los segmentos donde la fuente
  permanece fija.

Si existe:

    resultados_metrica_1_tetra_segmentos_validos.csv

el script lo utiliza automáticamente para generar las
gráficas direccionales definitivas del banco tetra.

======================================================================
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =====================================================================
# 1. RUTAS
# =====================================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# validation/scripts/metrica_1
#           ↓
# validation

VALIDATION_DIR = os.path.dirname(
    os.path.dirname(CURRENT_DIR)
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


TABLE_DIR = os.path.join(
    RESULT_ROOT,
    "tablas"
)


GRAPH_DIR = os.path.join(
    RESULT_ROOT,
    "graficas"
)


os.makedirs(
    TABLE_DIR,
    exist_ok=True
)


os.makedirs(
    GRAPH_DIR,
    exist_ok=True
)


# =====================================================================
# 2. ARCHIVOS DE ENTRADA
# =====================================================================

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


# Archivo que generaremos después con
# analyze_tetra_valid_segments.py

VALID_TETRA_CANDIDATES = [

    os.path.join(
        CSV_DIR,
        "resultados_metrica_1_tetra_segmentos_validos.csv"
    ),

    os.path.join(
        CSV_DIR,
        "resultados_prueba1_tetra_segmentos_validos.csv"
    ),

    # Compatibilidad con resultados antiguos
    os.path.join(
        VALIDATION_DIR,
        "results",
        "resultados_prueba1_tetra_segmentos_validos.csv"
    )
]


# =====================================================================
# 3. FUNCIONES AUXILIARES
# =====================================================================

def read_csv_file(path):
    """
    Lee los CSV de la Métrica 1.

    Primero intenta el separador ';', utilizado para que los
    archivos se abran correctamente en Excel en configuración
    regional española/latinoamericana.

    Si detecta una única columna, intenta nuevamente con ','.
    """

    if not os.path.isfile(path):

        raise FileNotFoundError(
            f"No se encontró el archivo:\n{path}"
        )


    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig"
    )


    if len(df.columns) == 1:

        df = pd.read_csv(
            path,
            sep=",",
            encoding="utf-8-sig"
        )


    return df


def find_valid_tetra_csv():
    """
    Busca el CSV generado por el análisis de segmentos válidos.
    """

    for candidate in VALID_TETRA_CANDIDATES:

        if os.path.isfile(candidate):

            return candidate


    return None


def clean_valid_tetra_columns(df):
    """
    Normaliza los nombres de columnas del script
    analyze_tetra_valid_segments.py.

    Permite compatibilidad con la versión anterior donde
    los encabezados estaban escritos en minúsculas.
    """

    rename_map = {

        "direccion":
            "Condicion",

        "interpretacion":
            "Interpretacion",

        "archivo_original":
            "Archivo_original",

        "inicio_segmento_s":
            "Inicio_segmento_s",

        "fin_segmento_s":
            "Fin_segmento_s",

        "duracion_segmento_s":
            "Duracion_segmento_s",

        "sample_rate_Hz":
            "Frecuencia_muestreo_Hz",

        "canales_entrada":
            "Canales_entrada",

        "canales_FOA":
            "Canales_FOA",

        "muestras_entrada_segmento":
            "Muestras_entrada",

        "muestras_FOA":
            "Muestras_FOA",

        "RMS_W":
            "RMS_W",

        "RMS_X":
            "RMS_X",

        "RMS_Y":
            "RMS_Y",

        "RMS_Z":
            "RMS_Z",

        "coef_X_W":
            "Coef_X_W",

        "coef_Y_W":
            "Coef_Y_W",

        "coef_Z_W":
            "Coef_Z_W",

        "componente_direccional_dominante_RMS":
            "Componente_direccional_dominante_RMS",

        "pico_maximo":
            "Pico_maximo",

        "NaN":
            "NaN_count",

        "Inf":
            "Inf_count",

        "clipping_samples":
            "Clipping_samples",

        "clipping":
            "Clipping"
    }


    return df.rename(
        columns=rename_map
    )


def order_tetra(df):
    """
    Orden estándar para las seis direcciones físicas.
    """

    order = [

        "EJE +X",
        "EJE -X",
        "EJE +Y",
        "EJE -Y",
        "EJE +Z",
        "EJE -Z",

        # Compatibilidad con scripts anteriores
        "+X",
        "-X",
        "+Y",
        "-Y",
        "+Z",
        "-Z"
    ]


    def get_order(value):

        text = str(value)


        normalized = (
            text
            .replace("EJE ", "")
            .strip()
        )


        preferred = [

            "+X",
            "-X",
            "+Y",
            "-Y",
            "+Z",
            "-Z"
        ]


        try:

            return preferred.index(
                normalized
            )

        except ValueError:

            return 999


    df = df.copy()


    df["_orden"] = (
        df["Condicion"]
        .apply(get_order)
    )


    df = (
        df
        .sort_values("_orden")
        .drop(columns="_orden")
    )


    return df


def tetra_short_label(value):
    """
    EJE +X -> +X
    """

    return (
        str(value)
        .replace("EJE ", "")
        .strip()
    )


def format_excel_workbook(path):
    """
    Mejora la presentación visual del Excel generado.
    """

    try:

        from openpyxl import load_workbook


        workbook = load_workbook(
            path
        )


        for worksheet in workbook.worksheets:


            worksheet.freeze_panes = "A2"


            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )


            for column_cells in worksheet.columns:


                max_length = 0


                column_letter = (
                    column_cells[0].column_letter
                )


                for cell in column_cells:


                    if cell.value is None:

                        continue


                    text = str(
                        cell.value
                    )


                    max_length = max(
                        max_length,
                        len(text)
                    )


                width = min(
                    max_length + 2,
                    38
                )


                worksheet.column_dimensions[
                    column_letter
                ].width = width


        workbook.save(
            path
        )


    except Exception as error:

        print(
            "ADVERTENCIA: no fue posible aplicar "
            "el formato adicional al Excel."
        )

        print(
            error
        )


# =====================================================================
# 4. CARGAR RESULTADOS ESTRUCTURALES
# =====================================================================

print()

print(
    "=" * 88
)

print(
    "MÉTRICA 1 - GENERACIÓN DE TABLAS Y GRÁFICAS"
)

print(
    "=" * 88
)


df_general = read_csv_file(
    GENERAL_CSV
)


df_stereo = read_csv_file(
    STEREO_CSV
)


df_tetra = read_csv_file(
    TETRA_CSV
)


df_tetra = order_tetra(
    df_tetra
)


print()

print(
    "Resultados estructurales cargados correctamente."
)

print(
    "Casos estéreo:",
    len(df_stereo)
)

print(
    "Casos tetra:",
    len(df_tetra)
)


# =====================================================================
# 5. TABLA DE CONTROL ESTRUCTURAL
# =====================================================================

control_columns = [

    "Banco",
    "Condicion",
    "Interpretacion",

    "Frecuencia_muestreo_Hz",

    "Canales_entrada",
    "Canales_FOA",

    "Muestras_entrada",
    "Muestras_FOA",

    "Duracion_entrada_s",
    "Duracion_FOA_s",

    "Pico_maximo",

    "NaN_count",
    "Inf_count",

    "Clipping_samples",
    "Clipping"
]


tabla_control = df_general[
    control_columns
].copy()


# =====================================================================
# 6. TABLA RMS - BANCO ESTÉREO
# =====================================================================

tabla_rms_stereo = df_stereo[

    [
        "Condicion",
        "Interpretacion",
        "RMS_W",
        "RMS_X",
        "RMS_Y",
        "RMS_Z"
    ]

].copy()


# =====================================================================
# 7. TABLA DIRECCIONAL - BANCO ESTÉREO CONTROLADO
# =====================================================================

# Para evaluar izquierda/centro/derecha se usan los tonos
# controlados A02.

stereo_controlled = df_stereo[

    df_stereo[
        "Condicion"
    ].isin(
        [
            "A02_tono_1kHz_left",
            "A02_tono_1kHz_center",
            "A02_tono_1kHz_right"
        ]
    )

].copy()


stereo_order = {

    "A02_tono_1kHz_left":
        0,

    "A02_tono_1kHz_center":
        1,

    "A02_tono_1kHz_right":
        2

}


stereo_controlled["_orden"] = (

    stereo_controlled[
        "Condicion"
    ]

    .map(
        stereo_order
    )

)


stereo_controlled = (

    stereo_controlled

    .sort_values(
        "_orden"
    )

    .drop(
        columns="_orden"
    )

)


tabla_direccion_stereo = stereo_controlled[

    [
        "Condicion",
        "Interpretacion",

        "Coef_X_W",
        "Coef_Y_W",
        "Coef_Z_W",

        "RMS_X_W",
        "RMS_Y_W",
        "RMS_Z_W"
    ]

].copy()


# =====================================================================
# 8. TABLAS DEL BANCO TETRA - GRABACIÓN COMPLETA
# =====================================================================

tabla_rms_tetra_completo = df_tetra[

    [
        "Condicion",
        "Interpretacion",

        "RMS_W",
        "RMS_X",
        "RMS_Y",
        "RMS_Z"
    ]

].copy()


tabla_direccion_tetra_completo = df_tetra[

    [
        "Condicion",
        "Interpretacion",

        "Eje_esperado",
        "Signo_esperado",

        "Coef_X_W",
        "Coef_Y_W",
        "Coef_Z_W",

        "Componente_direccional_dominante_RMS"
    ]

].copy()


# =====================================================================
# 9. BUSCAR RESULTADOS DE SEGMENTOS VÁLIDOS
# =====================================================================

valid_tetra_path = (
    find_valid_tetra_csv()
)


df_tetra_valid = None


if valid_tetra_path is not None:


    df_tetra_valid = read_csv_file(
        valid_tetra_path
    )


    df_tetra_valid = clean_valid_tetra_columns(
        df_tetra_valid
    )


    df_tetra_valid = order_tetra(
        df_tetra_valid
    )


    print()

    print(
        "Resultados de segmentos válidos encontrados:"
    )

    print(
        valid_tetra_path
    )


else:


    print()

    print(
        "AVISO:"
    )

    print(
        "Todavía no se encontró el CSV de segmentos válidos."
    )

    print(
        "Se generarán las tablas y gráficas estructurales,"
    )

    print(
        "pero la gráfica direccional FINAL del banco tetra "
        "se generará cuando se ejecute:"
    )

    print(
        "analyze_tetra_valid_segments.py"
    )


# =====================================================================
# 10. SI EXISTEN SEGMENTOS VÁLIDOS, GENERAR SUS TABLAS
# =====================================================================

if df_tetra_valid is not None:


    tabla_rms_tetra_valid = df_tetra_valid[

        [
            "Condicion",
            "Interpretacion",

            "RMS_W",
            "RMS_X",
            "RMS_Y",
            "RMS_Z"
        ]

    ].copy()


    tabla_direccion_tetra_valid = df_tetra_valid[

        [
            "Condicion",
            "Interpretacion",

            "Coef_X_W",
            "Coef_Y_W",
            "Coef_Z_W",

            "Componente_direccional_dominante_RMS"
        ]

    ].copy()


# =====================================================================
# 11. CREAR EXCEL DE TABLAS RESUMIDAS
# =====================================================================

TABLE_XLSX = os.path.join(
    TABLE_DIR,
    "tablas_resumen_metrica_1.xlsx"
)


with pd.ExcelWriter(
    TABLE_XLSX,
    engine="openpyxl"
) as writer:


    tabla_control.to_excel(
        writer,
        sheet_name="Control estructural",
        index=False
    )


    tabla_rms_stereo.to_excel(
        writer,
        sheet_name="RMS estereo",
        index=False
    )


    tabla_direccion_stereo.to_excel(
        writer,
        sheet_name="Direccion estereo",
        index=False
    )


    tabla_rms_tetra_completo.to_excel(
        writer,
        sheet_name="RMS tetra completo",
        index=False
    )


    tabla_direccion_tetra_completo.to_excel(
        writer,
        sheet_name="Dir tetra preliminar",
        index=False
    )


    if df_tetra_valid is not None:


        tabla_rms_tetra_valid.to_excel(
            writer,
            sheet_name="RMS tetra validos",
            index=False
        )


        tabla_direccion_tetra_valid.to_excel(
            writer,
            sheet_name="Dir tetra validos",
            index=False
        )


format_excel_workbook(
    TABLE_XLSX
)


# =====================================================================
# 12. GRÁFICA RMS - BANCO ESTÉREO
# =====================================================================

labels = (

    df_stereo[
        "Condicion"
    ]

    .str.replace(
        "A01_",
        "",
        regex=False
    )

    .str.replace(
        "A02_",
        "",
        regex=False
    )

    .str.replace(
        "A03_",
        "",
        regex=False
    )

    .str.replace(
        "A04_",
        "",
        regex=False
    )

    .str.replace(
        "A05_",
        "",
        regex=False
    )

)


x = np.arange(
    len(df_stereo)
)

width = 0.20


plt.figure(
    figsize=(13, 7)
)


plt.bar(
    x - 1.5 * width,
    df_stereo["RMS_W"],
    width,
    label="W"
)


plt.bar(
    x - 0.5 * width,
    df_stereo["RMS_X"],
    width,
    label="X"
)


plt.bar(
    x + 0.5 * width,
    df_stereo["RMS_Y"],
    width,
    label="Y"
)


plt.bar(
    x + 1.5 * width,
    df_stereo["RMS_Z"],
    width,
    label="Z"
)


plt.xticks(
    x,
    labels,
    rotation=25,
    ha="right"
)


plt.xlabel(
    "Señal de entrada"
)


plt.ylabel(
    "RMS"
)


plt.title(
    "RMS de las componentes FOA - banco de señales estéreo"
)


plt.legend()


plt.grid(
    axis="y",
    alpha=0.3
)


plt.tight_layout()


RMS_STEREO_GRAPH = os.path.join(
    GRAPH_DIR,
    "01_RMS_componentes_FOA_estereo.png"
)


plt.savefig(
    RMS_STEREO_GRAPH,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


# =====================================================================
# 13. GRÁFICA DIRECCIONAL - TONOS ESTÉREO CONTROLADOS
# =====================================================================

direction_labels = [

    "Izquierda",
    "Centro",
    "Derecha"
]


x = np.arange(
    len(stereo_controlled)
)

width = 0.25


plt.figure(
    figsize=(10, 6)
)


plt.bar(
    x - width,
    stereo_controlled["Coef_X_W"],
    width,
    label="X/W"
)


plt.bar(
    x,
    stereo_controlled["Coef_Y_W"],
    width,
    label="Y/W"
)


plt.bar(
    x + width,
    stereo_controlled["Coef_Z_W"],
    width,
    label="Z/W"
)


plt.axhline(
    0,
    linewidth=1
)


plt.xticks(
    x,
    direction_labels
)


plt.xlabel(
    "Condición de entrada"
)


plt.ylabel(
    "Coeficiente respecto a W"
)


plt.title(
    "Comportamiento direccional FOA - señales estéreo controladas"
)


plt.legend()


plt.grid(
    axis="y",
    alpha=0.3
)


plt.tight_layout()


DIR_STEREO_GRAPH = os.path.join(
    GRAPH_DIR,
    "02_direccionalidad_FOA_estereo_controlado.png"
)


plt.savefig(
    DIR_STEREO_GRAPH,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


# =====================================================================
# 14. GRÁFICA RMS - TETRA, GRABACIÓN COMPLETA
# =====================================================================

tetra_labels = [

    tetra_short_label(
        value
    )

    for value in df_tetra[
        "Condicion"
    ]

]


x = np.arange(
    len(df_tetra)
)

width = 0.20


plt.figure(
    figsize=(11, 6)
)


plt.bar(
    x - 1.5 * width,
    df_tetra["RMS_W"],
    width,
    label="W"
)


plt.bar(
    x - 0.5 * width,
    df_tetra["RMS_X"],
    width,
    label="X"
)


plt.bar(
    x + 0.5 * width,
    df_tetra["RMS_Y"],
    width,
    label="Y"
)


plt.bar(
    x + 1.5 * width,
    df_tetra["RMS_Z"],
    width,
    label="Z"
)


plt.xticks(
    x,
    tetra_labels
)


plt.xlabel(
    "Dirección física"
)


plt.ylabel(
    "RMS"
)


plt.title(
    "RMS FOA - grabaciones completas del banco experimental"
)


plt.legend()


plt.grid(
    axis="y",
    alpha=0.3
)


plt.tight_layout()


RMS_TETRA_FULL_GRAPH = os.path.join(
    GRAPH_DIR,
    "03_RMS_FOA_tetra_grabacion_completa.png"
)


plt.savefig(
    RMS_TETRA_FULL_GRAPH,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


# =====================================================================
# 15. GRÁFICAS TETRA DEFINITIVAS - SEGMENTOS VÁLIDOS
# =====================================================================

RMS_TETRA_VALID_GRAPH = None

DIR_TETRA_VALID_GRAPH = None


if df_tetra_valid is not None:


    valid_labels = [

        tetra_short_label(
            value
        )

        for value in df_tetra_valid[
            "Condicion"
        ]

    ]


    x = np.arange(
        len(df_tetra_valid)
    )

    width = 0.20


    # -----------------------------------------------------------------
    # RMS segmentos válidos
    # -----------------------------------------------------------------

    plt.figure(
        figsize=(11, 6)
    )


    plt.bar(
        x - 1.5 * width,
        df_tetra_valid["RMS_W"],
        width,
        label="W"
    )


    plt.bar(
        x - 0.5 * width,
        df_tetra_valid["RMS_X"],
        width,
        label="X"
    )


    plt.bar(
        x + 0.5 * width,
        df_tetra_valid["RMS_Y"],
        width,
        label="Y"
    )


    plt.bar(
        x + 1.5 * width,
        df_tetra_valid["RMS_Z"],
        width,
        label="Z"
    )


    plt.xticks(
        x,
        valid_labels
    )


    plt.xlabel(
        "Dirección física"
    )


    plt.ylabel(
        "RMS"
    )


    plt.title(
        "RMS FOA - segmentos válidos del banco experimental"
    )


    plt.legend()


    plt.grid(
        axis="y",
        alpha=0.3
    )


    plt.tight_layout()


    RMS_TETRA_VALID_GRAPH = os.path.join(
        GRAPH_DIR,
        "04_RMS_FOA_tetra_segmentos_validos.png"
    )


    plt.savefig(
        RMS_TETRA_VALID_GRAPH,
        dpi=300,
        bbox_inches="tight"
    )


    plt.close()


    # -----------------------------------------------------------------
    # Coeficientes direccionales con signo
    # -----------------------------------------------------------------

    width = 0.25


    plt.figure(
        figsize=(11, 6)
    )


    plt.bar(
        x - width,
        df_tetra_valid["Coef_X_W"],
        width,
        label="X/W"
    )


    plt.bar(
        x,
        df_tetra_valid["Coef_Y_W"],
        width,
        label="Y/W"
    )


    plt.bar(
        x + width,
        df_tetra_valid["Coef_Z_W"],
        width,
        label="Z/W"
    )


    plt.axhline(
        0,
        linewidth=1
    )


    plt.xticks(
        x,
        valid_labels
    )


    plt.xlabel(
        "Dirección física"
    )


    plt.ylabel(
        "Coeficiente respecto a W"
    )


    plt.title(
        "Comportamiento direccional FOA - segmentos válidos"
    )


    plt.legend()


    plt.grid(
        axis="y",
        alpha=0.3
    )


    plt.tight_layout()


    DIR_TETRA_VALID_GRAPH = os.path.join(
        GRAPH_DIR,
        "05_direccionalidad_FOA_tetra_segmentos_validos.png"
    )


    plt.savefig(
        DIR_TETRA_VALID_GRAPH,
        dpi=300,
        bbox_inches="tight"
    )


    plt.close()


# =====================================================================
# 16. RESUMEN
# =====================================================================

print()

print(
    "=" * 88
)

print(
    "TABLAS Y GRÁFICAS GENERADAS"
)

print(
    "=" * 88
)


print()

print(
    "Tabla resumen:"
)

print(
    "-",
    TABLE_XLSX
)


print()

print(
    "Gráficas generadas:"
)


print(
    "-",
    RMS_STEREO_GRAPH
)


print(
    "-",
    DIR_STEREO_GRAPH
)


print(
    "-",
    RMS_TETRA_FULL_GRAPH
)


if RMS_TETRA_VALID_GRAPH is not None:

    print(
        "-",
        RMS_TETRA_VALID_GRAPH
    )


if DIR_TETRA_VALID_GRAPH is not None:

    print(
        "-",
        DIR_TETRA_VALID_GRAPH
    )


print()

print(
    "IMPORTANTE:"
)


if df_tetra_valid is None:

    print(
        "La caracterización estructural está disponible,"
    )

    print(
        "pero falta ejecutar analyze_tetra_valid_segments.py "
        "para cerrar la comprobación direccional tetra."
    )


else:

    print(
        "Se utilizaron los segmentos válidos para la "
        "comprobación direccional definitiva del banco tetra."
    )


print()

print(
    "=" * 88
)