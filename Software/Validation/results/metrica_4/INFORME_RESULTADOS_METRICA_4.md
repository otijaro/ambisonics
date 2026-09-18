# Informe de Resultados Experimentales — Métrica 4
## Evaluación del Desempeño Computacional de la Plataforma

> **Proyecto**: Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonics  
> **Autores**: Anwar Andrés Cuello Pabón (2181702), Sharon Catalina Vargas Cortes (2211259)  
> **Director**: Ing. Omar Javier Tíjaro Rojas | **Codirector**: Nicolas Esteban Hernandez Bustos  
> **Institución**: Universidad Industrial de Santander — Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (2026-II)

---

## 1. Objetivo de la Métrica
Evaluar el desempeño computacional de la plataforma web durante la conversión Ambisonics, determinando el tiempo de procesamiento, el Factor de Tiempo Real (RTF = T_proc / T_audio), el consumo de recursos de hardware (CPU y RAM) y la escalabilidad del sistema ante variaciones en la duración del contenido.

## 2. Fundamentación Teórica y Metodológica
La conversión Ambisonics y la síntesis binaural por convolución directa con filtros HRTF de alta resolución demandan un volumen apreciable de operaciones matemáticas. Un sistema eficiente debe garantizar un Factor de Tiempo Real RTF < 1.0 (procesamiento más rápido que tiempo real) y un crecimiento temporal lineal sin explosión de memoria RAM al aumentar la duración de la pista de entrada.

## 3. Procedimiento de Evaluación Experimental
1. Recopilación de las 19 ejecuciones empíricas de repetibilidad y carga registradas en la interfaz gráfica web (METRICA 3.docx) para audios de 2s, 10s, 30s, 35.6s, 56.6s, 281.4s (5 min) y 578.1s (10 min).
2. Cálculo de métricas: Factor de Tiempo Real (RTF), porcentaje RTF y factor de velocidad respecto a tiempo real.
3. Análisis de regresión lineal para evaluar la escalabilidad computacional (coeficiente R^2, pendiente m y ordenada al origen c).
4. Evaluación de memoria RAM y CPU en la arquitectura streaming.
5. Generación de curvas comparativas y tablas de desempeño.

## 4. Análisis de Resultados Obtenidos
El sistema procesó con éxito el 100% de las solicitudes. El Factor de Tiempo Real promedio se situó en RTF = 0.273 (27.3%), lo que certifica que la plataforma convierte el audio aproximadamente 3.88 veces más rápido que el tiempo real. Para la pista musical de 10 minutos (578.1 s), la conversión demandó tan solo 148.97 s (RTF = 25.8%). La regresión lineal arrojó T_proc = 0.2574 · T_audio + 0.7577 s con un coeficiente de determinación sobresaliente R^2 = 0.99904, confirmando un comportamiento estrictamente lineal. El consumo de memoria RAM se mantuvo acotado (< 250 MB) y el uso de CPU controlado en 42.5% multinúcleo.

## 5. Matriz de Criterios de Aceptación y Cumplimiento
| Variable Evaluada | Resultado Obtenido | Condición Esperada | Cumplimiento |
| :--- | :--- | :--- | :---: |
| **Tiempo de procesamiento** | Completado sin bloqueos (Máx: 148.97s para 10 min) | Conversión completada dentro de rangos operativos | **SI** |
| **Factor de Tiempo Real (RTF)** | RTF promedio = 27.3% (Velocidad: 3.88x tiempo real) | RTF < 1.0 (procesamiento más rápido que tiempo real) | **SI** |
| **Linealidad y escalabilidad** | Ajuste lineal con R^2 = 0.99904 y pendiente m = 0.257 | Escalabilidad proporcional directa (R^2 >= 0.95) | **SI** |
| **Consumo de Memoria RAM** | Pico constante < 250 MB (gracias a streaming OLA) | Sin saturación ni fugas de memoria (RAM < 500 MB) | **SI** |
| **Utilización de CPU** | Uso multinúcleo controlado en 42.5% | Sin bloqueo de la interfaz web (CPU < 85%) | **SI** |
| **Capacidad de respuesta** | 19 de 19 ejecuciones de prueba conformes (100%) | Operatividad confiable en toda condición | **SI** |
| **EVALUACIÓN GLOBAL** | Alta eficiencia y viabilidad práctica demostrada | Desempeño computacional satisfactorio | **APROBADA** |

## 6. Evidencias Generadas en esta Carpeta
Los archivos de soporte cuantitativo y visual asociados a esta evaluación se encuentran organizados en las subcarpetas de `results/metrica_4/`:
- **`csv/`**: Archivos de datos numéricos detallados con las métricas calculadas.
- **`graficas/`**: Figuras en alta resolución que ilustran el comportamiento del sistema.
- **`tablas/`**: Tablas de resumen consolidadas en formato Excel (.xlsx).

## 7. Conclusiones Técnicas
- La plataforma opera con un Factor de Tiempo Real sobresaliente (RTF aprox 0.25), logrando procesar 4 minutos de audio en apenas 1 minuto de reloj.
- La arquitectura streaming OLA garantiza una escalabilidad lineal estricta (R^2 = 0.9990) y mantiene un consumo de RAM plano e independiente de la longitud del archivo.
- El sistema es completamente viable y eficiente para despliegues prácticos y entornos de producción web.
