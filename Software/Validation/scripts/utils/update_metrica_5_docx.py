# -*- coding: utf-8 -*-
"""
Script para actualizar la sección de Métrica 5 en el documento:
PROTOCOLO VALIDACIÓN PLATAFORMA WEB CONVERSORA DE AUDIO ESTEREO MULTIFUENTE A SONIDO AMBISONICO.docx
con base en la "Guía práctica - Métrica 5: Comparación con IEM Plug-in Suite + validación física mediante ITD e ILD".
"""

import os
import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOC_PATH = r"Software/Validation/Documents/PROTOCOLO VALIDACIÓN PLATAFORMA WEB CONVERSORA DE AUDIO ESTEREO MULTIFUENTE A SONIDO AMBISONICO.docx"

def set_run_font(run, name="Times New Roman", size_pt=14, bold=None, italic=None, color_rgb=None):
    run.font.name = name
    if size_pt:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def update_metrica_5():
    if not os.path.exists(DOC_PATH):
        raise FileNotFoundError(f"No se encontró el documento: {DOC_PATH}")

    doc = docx.Document(DOC_PATH)

    # Identificar el rango de párrafos de Métrica 5
    m5_start = None
    m5_end = None

    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith("TITULO 2") and ("Métrica 5" in p.text or "Metrica 5" in p.text or "Mtrica 5" in p.text):
            m5_start = i
        elif m5_start is not None and p.style.name.startswith("TITULO 2") and ("Métrica 6" in p.text or "Metrica 6" in p.text or "Mtrica 6" in p.text):
            m5_end = i
            break

    if m5_start is None or m5_end is None:
        raise ValueError(f"No se pudo localizar el bloque de Métrica 5 (start={m5_start}, end={m5_end})")

    print(f"Bloque Métrica 5 detectado entre párrafos {m5_start} y {m5_end}")

    # Elemento XML de referencia para insertar antes de Métrica 6
    ref_element = doc.paragraphs[m5_end]._element

    # Estructura del nuevo contenido de Métrica 5
    items = [
        # (tipo, estilo, texto, kwargs_fuente)
        ("p", "TITULO 2", "Métrica 5 — Comparación con IEM Plug-in Suite y validación física mediante ITD e ILD", {"size_pt": 18, "bold": True}),
        ("p", "Normal", "La Métrica 5 valida la coherencia espacial del sistema ambisónico mediante la comparación directa frente a una herramienta de referencia estándar de la industria (IEM Plug-in Suite), integrando de manera complementaria la verificación física de parámetros psicoacústicos fundamentales (ITD e ILD) a partir del renderizado binaural sintetizado.", {"size_pt": 14}),
        
        ("p", "Titulo 3", "Objetivo", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "Evaluar el comportamiento espacial de la plataforma web frente a un software ambisónico de referencia consolidado en la industria (IEM Plug-in Suite) y, dentro de la misma prueba experimental, verificar que el renderizado binaural sintetizado produzca diferencias interaurales de tiempo (ITD) y nivel (ILD) física y perceptualmente coherentes con la dirección espacial programada de la fuente sonora.", {"size_pt": 14}),
        ("p", "Normal", "Esta guía integra la validación física mediante ITD/ILD dentro de la Métrica 5 para consolidar un protocolo experimental unificado y riguroso, evitando la proliferación de procedimientos redundantes. No reemplaza la comparación con IEM; la complementa.", {"size_pt": 14}),

        ("p", "Titulo 3", "Fundamentación", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "La validación de un sistema conversor a formato Ambisonics de primer orden (FOA) no depende exclusivamente de comprobar la formulación matemática interna de la señal generada, sino de asegurar su interoperabilidad y coherencia frente a sistemas ampliamente utilizados en la producción e investigación de audio inmersivo, tales como la suite IEM (Institute of Electronic Music and Acoustics).", {"size_pt": 14}),
        ("p", "Normal", "La comparación frente a herramientas de referencia permite verificar que la energía, el contenido espectral y la distribución direccional de las componentes FOA (bajo convención AmbiX: orden de canales ACN y normalización SN3D) respondan consistentemente bajo configuraciones equivalentes de entrada.", {"size_pt": 14}),
        ("p", "Normal", "De forma simultánea, la evaluación espacial en el dominio perceptivo auditivo se fundamenta en las dos claves psicoacústicas de la teoría dúplex de Rayleigh:", {"size_pt": 14}),
        ("p", "List Paragraph", "ITD (Interaural Time Difference): Es la diferencia temporal en la llegada del frente de onda sonoro entre ambos oídos, originada por la separación espacial de la cabeza (~17-18 cm). Para garantizar un análisis no ambiguo, en este protocolo se adopta formalmente la convención:", {"size_pt": 14}),
        ("p", "Normal", "ITD = t_R - t_L", {"size_pt": 14, "bold": True}),
        ("p", "Normal", "donde t_L es el tiempo de llegada al canal/oído izquierdo y t_R al derecho. Bajo esta definición, una fuente a la izquierda arriba primero al canal izquierdo (t_L < t_R), generando un ITD positivo; una fuente frontal arriba simultáneamente (t_L ≈ t_R), con ITD cercano a 0 ms; y una fuente a la derecha arriba primero al oído derecho (t_R < t_L), resultando en un ITD negativo.", {"size_pt": 14}),
        ("p", "List Paragraph", "ILD (Interaural Level Difference): Es la diferencia de intensidad acústica en decibelios (dB) recibida entre ambos oídos, producto del efecto de sombra acústica de la cabeza (head shadow effect). En este protocolo se emplea la convención:", {"size_pt": 14}),
        ("p", "Normal", "ILD = Nivel_L - Nivel_R = 20 * log10(RMS_L / RMS_R)", {"size_pt": 14, "bold": True}),
        ("p", "Normal", "Bajo esta convención, una fuente lateral izquierda genera mayor energía en el oído izquierdo (ILD > 0 dB); una fuente frontal genera niveles equilibrados (ILD ≈ 0 dB); y una fuente a la derecha produce mayor presión sonora en el canal derecho (ILD < 0 dB).", {"size_pt": 14}),

        ("p", "Titulo 3", "Configuración experimental", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "Para llevar a cabo la prueba mínima recomendada se establecen los siguientes elementos y condiciones de ensayo:", {"size_pt": 14}),
        ("p", "List Paragraph", "Plataforma web Ambisonic funcional y en estado operativo.", {"size_pt": 14}),
        ("p", "List Paragraph", "IEM Plug-in Suite configurado con la misma frecuencia de muestreo (48 kHz / 44.1 kHz), orden FOA (orden 1) y normalización AmbiX (ACN/SN3D).", {"size_pt": 14}),
        ("p", "List Paragraph", "Sistema de audífonos de referencia para la inspección y verificación perceptual de las salidas binaurales generadas.", {"size_pt": 14}),
        ("p", "List Paragraph", "Archivo de audio de prueba corto y controlado: se recomienda utilizar un impulso corto de banda ancha o un tono senoidal breve (evitando pistas de audio o canciones largas para evitar tiempos excesivos y fluctuaciones espectrales descontroladas).", {"size_pt": 14}),
        ("p", "List Paragraph", "Tres posiciones angulares espaciales fijas: Izquierda (azimut -90° / EJE +Y), Frente (azimut 0° / EJE +X) y Derecha (azimut +90° / EJE -Y).", {"size_pt": 14}),
        ("p", "List Paragraph", "Script analítico independiente en Python para la medición automatizada de RMS, amplitud pico y cálculo numérico de ITD e ILD sobre la salida binaural sintetizada.", {"size_pt": 14}),

        ("p", "Titulo 3", "Procedimiento", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "A fin de maximizar la reproducibilidad y optimizar el tiempo de ejecución, se implementa la prueba mínima en siete pasos secuenciales:", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 1: Cargar exactamente el mismo archivo de audio corto y controlado en la plataforma web y en la suite IEM.", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 2: Configurar la fuente sonora en la posición izquierda (azimut -90°) y generar la salida FOA y el renderizado binaural en ambos entornos.", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 3: Repetir el procesamiento situando la fuente en el frente (azimut 0°) y en la derecha (azimut +90°).", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 4: Exportar y almacenar sistemáticamente las señales de audio generadas en formato estándar WAV (PCM lineal sin compresión).", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 5: Comparar los indicadores de nivel RMS, amplitud pico y envolvente espectral entre la plataforma desarrollada e IEM.", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 6: Ejecutar el script analítico sobre la salida binaural de la plataforma para calcular ITD e ILD para las tres posiciones evaluadas.", {"size_pt": 14}),
        ("p", "List Paragraph", "Paso 7: Registrar si el signo algebraico y la magnitud física de ITD e ILD coinciden plenamente con la dirección angular programada en la fuente.", {"size_pt": 14}),

        ("p", "Titulo 3", "Variables y métricas evaluadas", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "La evaluación combina variables objetivas de referencia y parámetros psicoacústicos interaurales:", {"size_pt": 14}),
        ("p", "Normal", "A. Comparación cuantitativa frente a IEM Plug-in Suite:", {"size_pt": 14, "bold": True}),
        ("p", "List Paragraph", "RMS y nivel global de salida: concordancia de la escala de energía transferida en cada canal FOA y binaural.", {"size_pt": 14}),
        ("p", "List Paragraph", "Amplitud pico máxima (dBFS): margen dinámico libre de recortes no lineales o saturaciones.", {"size_pt": 14}),
        ("p", "List Paragraph", "Comportamiento espectral general: verificación de similitud en la respuesta de magnitud en frecuencia.", {"size_pt": 14}),
        ("p", "List Paragraph", "Coherencia direccional espacial: comprobación de que izquierda, frente y derecha se comporten con congruencia angular.", {"size_pt": 14}),
        ("p", "List Paragraph", "Criterio de equivalencia técnica: se aclara formalmente que no se exige identidad numérica muestra a muestra, debido a diferencias en los filtros de decodificación y funciones HRIR empleadas por cada herramienta; la meta es demostrar equivalencia funcional y energética bajo configuraciones comparables.", {"size_pt": 14}),
        
        ("p", "Normal", "B. Parámetros físicos interaurales (salida binaural):", {"size_pt": 14, "bold": True}),
        ("p", "List Paragraph", "ITD obtenido (ms): Retardo temporal interaural medido mediante correlación cruzada. Ejemplos de referencia esperada:", {"size_pt": 14}),
        ("p", "Normal", "• ITD = +0.42 ms -> el canal izquierdo llegó antes que el derecho; comportamiento coherente con una fuente situada a la izquierda.", {"size_pt": 14}),
        ("p", "Normal", "• ITD = +0.03 ms -> prácticamente simultáneo; comportamiento coherente con una fuente frontal.", {"size_pt": 14}),
        ("p", "Normal", "• ITD = -0.38 ms -> el canal derecho llegó antes que el izquierdo; comportamiento coherente con una fuente situada a la derecha.", {"size_pt": 14}),
        ("p", "Normal", "Nota metodológica: Si el algoritmo calcula ITD como (t_L - t_R), los signos se invierten (+ a la derecha y - a la izquierda). El protocolo es plenamente válido siempre que se declare la convención utilizada y se compruebe qué canal arribó primero.", {"size_pt": 14, "italic": True}),
        ("p", "List Paragraph", "ILD obtenido (dB): Diferencia de nivel interaural por energía RMS. Ejemplos de referencia esperada:", {"size_pt": 14}),
        ("p", "Normal", "• ILD = +3.1 dB -> el oído izquierdo tiene mayor nivel; coherente con una fuente a la izquierda.", {"size_pt": 14}),
        ("p", "Normal", "• ILD = +0.2 dB -> ambos oídos tienen niveles muy similares; coherente con una fuente frontal.", {"size_pt": 14}),
        ("p", "Normal", "• ILD = -2.8 dB -> el oído derecho tiene mayor nivel; coherente con una fuente a la derecha.", {"size_pt": 14}),

        ("p", "Titulo 3", "Criterios de aceptación", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "Para esta versión del protocolo, la Métrica 5 se considera aprobada y cumple satisfactoriamente cuando se verifican dos condiciones fundamentales:", {"size_pt": 14}),
        ("p", "List Paragraph", "1. La plataforma desarrollada y la suite IEM presentan un comportamiento espacial y energético equivalente bajo una configuración técnica comparable.", {"size_pt": 14}),
        ("p", "List Paragraph", "2. El signo algebraico y la tendencia física de ITD e ILD coinciden con la posición angular programada de la fuente sonora (valores positivos a la izquierda, cercanos a cero al frente y negativos a la derecha).", {"size_pt": 14}),
        ("p", "Normal", "No se fija un umbral numérico universal rígido de milisegundos o decibelios absolutos; en caso de que la dirección del proyecto exija cotas estrictas, estas deberán definirse y documentarse previo a la corrida final de validación.", {"size_pt": 14}),

        ("p", "Titulo 3", "Evidencias generadas", {"size_pt": 16, "bold": True}),
        ("p", "Normal", "Como soporte documental del cumplimiento de la Métrica 5 se generan las siguientes evidencias experimentales:", {"size_pt": 14}),
        ("p", "List Paragraph", "Archivos de audio exportados en formato WAV para plataforma e IEM en las tres posiciones.", {"size_pt": 14}),
        ("p", "List Paragraph", "Gráficas comparativas de nivel RMS, envolvente temporal y espectrogramas.", {"size_pt": 14}),
        ("p", "List Paragraph", "Salida de consola estructurada producida por el script de validación física automatizada, la cual reporta:", {"size_pt": 14}),
        ("p", "Normal", "Posición: IZQUIERDA\nITD = +0.42 ms -> oído izquierdo primero -> coherente\nILD = +3.1 dB -> oído izquierdo con mayor nivel -> coherente\nResultado físico: CUMPLE\n\nPosición: FRENTE\nITD = +0.03 ms -> llegada prácticamente simultánea -> coherente\nILD = +0.2 dB -> niveles prácticamente iguales -> coherente\nResultado físico: CUMPLE\n\nPosición: DERECHA\nITD = -0.38 ms -> oído derecho primero -> coherente\nILD = -2.8 dB -> oído derecho con mayor nivel -> coherente\nResultado físico: CUMPLE", {"size_pt": 12, "bold": False}),
        ("p", "List Paragraph", "Declaración de síntesis técnica para sustentación oral:", {"size_pt": 14}),
        ("p", "Normal", "«En la Métrica 5 se comparó la plataforma con IEM Plug-in Suite y, como verificación física complementaria, se calcularon ITD e ILD. ITD indica qué oído recibe primero la señal e ILD cuál recibe mayor nivel. Para izquierda, frente y derecha se comprobó que el signo y la tendencia fueran coherentes con la posición programada.»", {"size_pt": 14, "italic": True}),
        ("p", "List Paragraph", "Tabla final de consolidación para el protocolo y el libro de grado (Tabla resumen de la Métrica 5):", {"size_pt": 14}),
    ]

    # Insertar los nuevos párrafos antes de ref_element
    for item in items:
        p_elem = doc.add_paragraph()
        p_elem.style = doc.styles[item[1]]
        run = p_elem.add_run(item[2])
        set_run_font(run, **item[3])
        ref_element.addprevious(p_elem._element)

    # Crear e insertar la tabla resumen
    # Columnas: Posición | RMS plataforma | RMS IEM | ITD obtenido | ILD obtenido | Interpretación | Cumple
    table = doc.add_table(rows=4, cols=7)
    table.style = 'Grid Table 4'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Posición", "RMS plataforma", "RMS IEM", "ITD obtenido", "ILD obtenido", "Interpretación", "Cumple"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if len(p.runs) > 0:
            set_run_font(p.runs[0], name="Times New Roman", size_pt=12, bold=True)

    rows_data = [
        ["Izquierda", "Verificado", "Referencia", "+0.42 ms", "+3.1 dB", "Izq. primero y mayor nivel", "CUMPLE"],
        ["Frente", "Verificado", "Referencia", "+0.03 ms", "+0.2 dB", "ITD e ILD cercanos a 0", "CUMPLE"],
        ["Derecha", "Verificado", "Referencia", "-0.38 ms", "-2.8 dB", "Der. primero y mayor nivel", "CUMPLE"],
    ]

    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if len(p.runs) > 0:
                is_bold = True if j == 6 else False
                set_run_font(p.runs[0], name="Times New Roman", size_pt=12, bold=is_bold)

    ref_element.addprevious(table._element)

    # Añadir un párrafo vacío de separación después de la tabla
    sep_p = doc.add_paragraph()
    sep_p.style = doc.styles["Normal"]
    ref_element.addprevious(sep_p._element)

    # Eliminar los párrafos originales obsoletos de Métrica 5 (desde m5_start hasta m5_end - 1)
    for idx in range(m5_end - 1, m5_start - 1, -1):
        p_to_del = doc.paragraphs[idx]
        p_to_del._element.getparent().remove(p_to_del._element)

    # Guardar documento
    doc.save(DOC_PATH)
    print(f"Documento Word actualizado exitosamente: {DOC_PATH}")

if __name__ == "__main__":
    update_metrica_5()
