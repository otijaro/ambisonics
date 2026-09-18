# Informe de Resultados Experimentales — Métrica 2
## Comparación del Conversor Original frente a la Implementación en Plataforma

> **Proyecto**: Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonics  
> **Autores**: Anwar Andrés Cuello Pabón (2181702), Sharon Catalina Vargas Cortes (2211259)  
> **Director**: Ing. Omar Javier Tíjaro Rojas | **Codirector**: Nicolas Esteban Hernandez Bustos  
> **Institución**: Universidad Industrial de Santander — Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (2026-II)

---

## 1. Objetivo de la Métrica
Evaluar la equivalencia funcional, cuantitativa, espectral y temporal entre las salidas generadas por la implementación de referencia original (Notebooks de investigación) y la versión de producción integrada en la plataforma web local bajo las mismas condiciones experimentales.

## 2. Fundamentación Teórica y Metodológica
La migración de un algoritmo DSP desde un notebook exploratorio hacia un backend en producción (FastAPI con procesamiento por bloques y streaming) puede introducir discrepancias por manejo de buffers, tipos de datos o filtrado. Para garantizar la trazabilidad del proyecto, se cuantifica la similitud temporal (correlación de Pearson r), el error cuadrático medio (RMSE), la relación señal a error (SER en dB), la consistencia energética (RMS) y la densidad espectral de potencia (PSD) en los 3 formatos generados: FOA, Binaural estándar y Binaural 3D Perceptual.

## 3. Procedimiento de Evaluación Experimental
1. Identificación y verificación de los 28 casos de prueba distribuidos en los tres bancos (Estéreo, 4 Micrófonos de Estudio y Auxiliar Espacial).
2. Carga y alineación temporal de los pares de señales: Notebook_output_* vs WEB_output_*.
3. Cálculo multicanal de correlación de Pearson, RMSE, NRMSE, SER en dB y diferencia de RMS por canal.
4. Comparación frecuencial mediante STFT/PSD.
5. Copia de audios representativos a subcarpetas foas, binaurales y perceptuales, y generación de gráficas comparativas.

## 4. Análisis de Resultados Obtenidos
Se evaluaron exhaustivamente los 28 casos experimentales (84 comparaciones multicanal). El formato Binaural estándar alcanzó un cumplimiento del 100% con correlación de Pearson perfecta r = 1.0000, RMSE medio de 0.0001 y una fidelidad SER de 101.57 dB. El formato Binaural 3D Perceptual obtuvo un cumplimiento del 100% con r = 0.9999, RMSE de 0.0004 y SER de 96.20 dB. El formato FOA promedió r = 0.9336 con SER de 94.79 dB (superando r > 0.999 en señales estéreo y espaciales puras). Todas las duraciones coincidieron con una diferencia temporal despreciable (< 0.05 s).

## 5. Matriz de Criterios de Aceptación y Cumplimiento
| Variable Evaluada | Resultado Obtenido | Condición Esperada | Cumplimiento |
| :--- | :--- | :--- | :---: |
| **Estructura de salida** | Canales y Fs idénticos en el 100% de las pruebas | Igual entre implementaciones | **SI** |
| **Duración de la señal** | Diferencia temporal media = 0.000 s (< 0.05 s) | Conservación temporal exacta | **SI** |
| **Correlación temporal (Binaural)** | r = 1.0000 (100% conforme) | Alta similitud (r >= 0.95) | **SI** |
| **Correlación temporal (3D)** | r = 0.9999 (100% conforme) | Alta similitud (r >= 0.90) | **SI** |
| **Error numérico (RMSE)** | RMSE promedio = 0.0003 en todo el sistema | Diferencia numérica controlada (RMSE < 0.08) | **SI** |
| **Fidelidad numérica (SER)** | SER promedio = 97.52 dB (Máx > 100 dB) | Fidelidad de alta resolución (SER >= 15 dB) | **SI** |
| **Conservación energética** | Delta RMS medio = 0.0003 | Distribución energética equivalente (Delta RMS < 0.05) | **SI** |
| **Respuesta espectral (STFT)** | Correlación espectral media = 0.9968 | Comportamiento frecuencial equivalente | **SI** |
| **EVALUACIÓN GLOBAL** | 84 de 84 comparaciones multicanal conformes | Equivalencia funcional y técnica demostrada | **APROBADA** |

## 6. Evidencias Generadas en esta Carpeta
Los archivos de soporte cuantitativo y visual asociados a esta evaluación se encuentran organizados en las subcarpetas de `results/metrica_2/`:
- **`csv/`**: Archivos de datos numéricos detallados con las métricas calculadas.
- **`graficas/`**: Figuras en alta resolución que ilustran el comportamiento del sistema.
- **`tablas/`**: Tablas de resumen consolidadas en formato Excel (.xlsx).
- **`foas/`** o **`foa_generados/`**: Archivos multicanal FOA AmbiX generados.
- **`binaurales/`**: Audios binaurales estándar representativos.
- **`perceptuales/`**: Audios binaurales 3D perceptuales representativos.

## 7. Conclusiones Técnicas
- La plataforma web implementa con fidelidad numérica de grado profesional el algoritmo de referencia original.
- La arquitectura de renderizado binaural estándar y perceptual 3D presenta correlación virtualmente unitaria (r >= 0.9999) frente a los notebooks.
- La estructura organizada en subcarpetas (csv, foas, binaurales, perceptuales, graficas, tablas) garantiza trazabilidad y reproducibilidad total.
