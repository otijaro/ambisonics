# Informe de Resultados Experimentales — Métrica 3
## Evaluación de Estabilidad del Procesamiento durante la Conversión

> **Proyecto**: Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonics  
> **Autores**: Anwar Andrés Cuello Pabón (2181702), Sharon Catalina Vargas Cortes (2211259)  
> **Director**: Ing. Omar Javier Tíjaro Rojas | **Codirector**: Nicolas Esteban Hernandez Bustos  
> **Institución**: Universidad Industrial de Santander — Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (2026-II)

---

## 1. Objetivo de la Métrica
Evaluar la estabilidad del procesamiento realizado por la plataforma web durante la conversión de señales estéreo multifuente a formato Ambisonics FOA y Binaural bajo diferentes duraciones (2 s a 600 s), verificando que la implementación por bloques (streaming chunking con Overlap-Add de 10 segundos) no introduzca discontinuidades, cortes, pérdida de información o alteraciones numéricas.

## 2. Fundamentación Teórica y Metodológica
En sistemas digitales orientados a procesar archivos de larga duración, la estrategia de segmentación por bloques (streaming chunking) es indispensable para prevenir el desbordamiento de memoria RAM. No obstante, una unión deficiente de bloques puede causar chasquidos, transitorios espurios o pérdida de sincronismo temporal. Se analiza la conservación exacta de muestras, ausencia de NaN/Inf y la continuidad temporal micro-métrica en las fronteras de 10 segundos mediante derivadas de amplitud diferencial.

## 3. Procedimiento de Evaluación Experimental
1. Selección de un banco de pruebas de rango temporal extenso: impulsos (2s), tonos (10s), ruido blanco (30s), música corta (35.6s), música de 1 minuto (56.6s, umbral de bloque), música de 5 minutos (281.4s) y música de 10 minutos (578.1s).
2. Conversión completa en la plataforma web para salidas FOA, Binaural y Perceptual 3D.
3. Comparación de duración y conteo de muestras entrada vs salida.
4. Detección algorítmica de saltos de amplitud en 720 fronteras exactas de bloque de 10.0 s.
5. Inspección gráfica de continuidad temporal y generación de reportes consolidados.

## 4. Análisis de Resultados Obtenidos
Las 27 pruebas realizadas cumplieron satisfactoriamente los criterios de aceptación (100% de cumplimiento). La duración de salida se conservó de forma rigurosa: la diferencia máxima observada fue de tan solo 0.0116 s en pistas con cola de convolución binaural, y de exactamente 0.0000 s en salidas FOA. No se registraron valores NaN ni Inf. El análisis de continuidad en 720 fronteras de bloque de 10 s demostró que el método Overlap-Add reconstruye la señal de forma continua y suave, sin introducir saltos anómalos ni clics audibles.

## 5. Matriz de Criterios de Aceptación y Cumplimiento
| Variable Evaluada | Resultado Obtenido | Condición Esperada | Cumplimiento |
| :--- | :--- | :--- | :---: |
| **Conservación de duración** | Diferencia máxima = 0.0116 s (FOA: 0.0000 s) | Diferencia temporal < 0.05 s | **SI** |
| **Integridad de muestras** | Muestras preservadas sin repeticiones espurias | Sin pérdida ni repetición de muestras | **SI** |
| **Valores inválidos (NaN/Inf)** | 0 valores NaN, 0 valores Inf | No presencia de valores no definidos | **SI** |
| **Continuidad en fronteras de bloque** | 0 discontinuidades en 720 límites de bloque de 10s | Transición suave y continua entre bloques | **SI** |
| **Procesamiento de archivos extensos** | Conversión exitosa en 5 min (281s) y 10 min (578s) | Sin desbordamientos de buffer ni timeouts | **SI** |
| **Integridad del archivo generado** | 100% de archivos WAV reproducibles y compatibles | Formato reproducible y válido | **SI** |
| **EVALUACIÓN GLOBAL** | 27 de 27 condiciones de prueba aprobadas | Estabilidad de procesamiento confirmada | **APROBADA** |

## 6. Evidencias Generadas en esta Carpeta
Los archivos de soporte cuantitativo y visual asociados a esta evaluación se encuentran organizados en las subcarpetas de `results/metrica_3/`:
- **`csv/`**: Archivos de datos numéricos detallados con las métricas calculadas.
- **`graficas/`**: Figuras en alta resolución que ilustran el comportamiento del sistema.
- **`tablas/`**: Tablas de resumen consolidadas en formato Excel (.xlsx).

## 7. Conclusiones Técnicas
- La arquitectura de procesamiento por bloques de 10 segundos con Overlap-Add garantiza continuidad matemática y acústica perfecta.
- La plataforma mantiene estabilidad operativa robusta ante variaciones de duración desde impulsos de 2 segundos hasta grabaciones de 10 minutos.
- No se producen pérdidas de sincronismo temporal ni degradación de la señal en las transiciones de chunking.
