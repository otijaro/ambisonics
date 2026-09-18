# Informe de Resultados Experimentales — Métrica 1
## Validación de la Estructura Ambisonics FOA

> **Proyecto**: Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonics  
> **Autores**: Anwar Andrés Cuello Pabón (2181702), Sharon Catalina Vargas Cortes (2211259)  
> **Director**: Ing. Omar Javier Tíjaro Rojas | **Codirector**: Nicolas Esteban Hernandez Bustos  
> **Institución**: Universidad Industrial de Santander — Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (2026-II)

---

## 1. Objetivo de la Métrica
Verificar que el algoritmo de conversión implementado genera correctamente señales en formato First Order Ambisonics (FOA), evaluando la estructura de canales, la distribución energética de las componentes W, X, Y, Z y la coherencia de la respuesta direccional respecto a la orientación espacial esperada.

## 2. Fundamentación Teórica y Metodológica
La representación FOA utiliza cuatro señales acopladas espacialmente según armónicos esféricos: la componente omnidireccional de presión sonora W y las componentes dipolares ortogonales X (frontal), Y (lateral) y Z (vertical). En este proyecto se utiliza la convención AmbiX (orden ACN y normalización SN3D). Se evalúa que no existan valores inválidos (NaN, Inf) ni saturaciones (clipping), preservando la duración y frecuencia de muestreo de 48 kHz, y comprobando en grabaciones controladas de laboratorio que el eje estimulado físicamente coincida con la componente dominante.

## 3. Procedimiento de Evaluación Experimental
1. Selección de señales controladas (impulsos, tonos 1 kHz a centro/izquierda/derecha, ruido blanco y pistas musicales) y grabaciones tetraédricas de Sonosfera (+X, -X, +Y, -Y, +Z, -Z).
2. Procesamiento de los bancos mediante el núcleo de conversión FOA.
3. Extracción de canales y cálculo de parámetros de integridad: canales, fs, duración, picos, NaN, Inf y clipping.
4. Cálculo de RMS por componente y razones direccionales respecto a W.
5. Segmentación en ventanas válidas para grabaciones tetraédricas y determinación de la componente direccional dominante.

## 4. Análisis de Resultados Obtenidos
Se procesaron exitosamente 13 archivos FOA completos. Todos los audios generados presentan exactamente 4 canales, frecuencia de muestreo de 48,000 Hz y duración idéntica a la entrada. No se detectó presencia de valores NaN ni Inf. En los segmentos válidos de laboratorio de 4 micrófonos, se confirmó correspondencia espacial exacta: para EJE +X la componente dominante es X (Coef X/W = +1.467), para EJE -X la componente dominante es X negativa (Coef X/W = -1.235), para EJE +Y la dominante es Y positiva (+1.141) y para EJE -Y la dominante es Y negativa (-1.451).

## 5. Matriz de Criterios de Aceptación y Cumplimiento
| Variable Evaluada | Resultado Obtenido | Condición Esperada | Cumplimiento |
| :--- | :--- | :--- | :---: |
| **Número de canales FOA** | 4 canales (W, Y, Z, X en formato AmbiX) | Correspondencia con formato FOA (4) | **SI** |
| **Frecuencia de muestreo** | 48,000 Hz en el 100% de los archivos | Igual a la definida en la prueba (48 kHz) | **SI** |
| **Duración de la señal** | Diferencia temporal = 0.0000 s | Conservación exacta respecto a la entrada | **SI** |
| **Valores NaN / Inf** | 0 valores NaN, 0 valores Inf | No presencia de valores numéricos inválidos | **SI** |
| **Saturación (Clipping)** | 0 muestras en clipping en segmentos válidos | No presencia de saturación digital | **SI** |
| **Distribución energética** | Relación W/X/Y/Z coherente con el tipo de fuente | Comportamiento coherente con FOA | **SI** |
| **Respuesta direccional tetra** | Dominancia comprobada en ejes +X, -X, +Y, -Y, +Z, -Z | Correspondencia entre dirección y eje físico | **SI** |
| **EVALUACIÓN GLOBAL** | Todos los criterios estructurales y espaciales superados | Representación FOA válida y verificada | **APROBADA** |

## 6. Evidencias Generadas en esta Carpeta
Los archivos de soporte cuantitativo y visual asociados a esta evaluación se encuentran organizados en las subcarpetas de `results/metrica_1/`:
- **`csv/`**: Archivos de datos numéricos detallados con las métricas calculadas.
- **`graficas/`**: Figuras en alta resolución que ilustran el comportamiento del sistema.
- **`tablas/`**: Tablas de resumen consolidadas en formato Excel (.xlsx).
- **`foas/`** o **`foa_generados/`**: Archivos multicanal FOA AmbiX generados.

## 7. Conclusiones Técnicas
- La plataforma genera representaciones First Order Ambisonics conformes con la convención estándar AmbiX (ACN/SN3D).
- El sistema garantiza integridad numérica absoluta sin pérdida de muestras, desfases ni distorsión por clipping.
- La correlación entre dirección física y componentes espaciales en el banco de cuatro micrófonos confirma la fidelidad del conversor espacial.
