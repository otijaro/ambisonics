# Informe de Resultados Experimentales — Métrica 6
## Evaluación Binaural mediante Diferencias ITD e ILD

> **Proyecto**: Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonics  
> **Autores**: Anwar Andrés Cuello Pabón (2181702), Sharon Catalina Vargas Cortes (2211259)  
> **Director**: Ing. Omar Javier Tíjaro Rojas | **Codirector**: Nicolas Esteban Hernandez Bustos  
> **Institución**: Universidad Industrial de Santander — Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (2026-II)

---

## 1. Objetivo de la Métrica
Evaluar la capacidad de la plataforma para transferir coherentemente la información espacial tridimensional desde el formato Ambisonics FOA hacia la salida binaural (L, R) sintetizada mediante HRTF, verificando los dos parámetros psicoacústicos fundamentales de localización auditiva humana: la Diferencia Temporal Interaural (ITD) y la Diferencia de Nivel Interaural (ILD).

## 2. Fundamentación Teórica y Metodológica
La percepción espacial en audífonos se fundamenta en las diferencias acústicas entre oídos: el retardo temporal relativo (ITD) derivado del desfase en la llegada de la onda sonora (típicamente entre 0 y 0.7 ms en la cabeza humana) y la diferencia de amplitud o nivel energético (ILD en dB) causada por la difracción y sombra acústica cefálica. Se verifica que fuentes posicionadas en el hemisferio lateral izquierdo induzcan adelanto temporal en canal L (ITD > 0) y mayor sonoridad (ILD > 0 dB), y viceversa para el hemisferio derecho, mientras que fuentes frontales presenten simetría bilateral (ITD aprox 0 ms, ILD aprox 0 dB).

## 3. Procedimiento de Evaluación Experimental
1. Selección de casos espaciales representativos en el banco auxiliar (test_left, test_center, test_right y test_sweep), banco estéreo (A02 tono 1kHz a izquierda, centro y derecha) y banco tetraédrico (EJE +Y, EJE +X, EJE -Y).
2. Extracción de los canales binaurales L y R generados por la plataforma web.
3. Cálculo de ILD en dB: 20 · log10(RMS_L / RMS_R).
4. Cálculo de ITD en ms mediante el retardo del pico en la función de correlación cruzada normalizada R_LR(tau).
5. Análisis temporal continuo de la trayectoria de paneo dinámico (test_sweep) y generación de curvas de correlograma.

## 4. Análisis de Resultados Obtenidos
Las pruebas cuantitativas demostraron coherencia psicoacústica plena. Para señales laterales en el banco auxiliar, se registraron ILD de +5.40 dB (test_left) y -6.38 dB (test_right), con un centro equilibrado en -0.39 dB. La diferencia temporal ITD se situó en +0.363 ms (izquierda) y -0.317 ms (derecha), valores perfectamente enmarcados en la ventana fisiológica humana (< 0.70 ms). En tonos de 1 kHz del banco estéreo, el ILD reflejó +3.66 dB (izquierda), -0.18 dB (centro) y -3.81 dB (derecha). El barrido espacial test_sweep confirmó una trayectoria suave, continua y monótona sin saltos de fase en los indicadores binaurales.

## 5. Matriz de Criterios de Aceptación y Cumplimiento
| Variable Evaluada | Resultado Obtenido | Condición Esperada | Cumplimiento |
| :--- | :--- | :--- | :---: |
| **Diferencia de nivel (ILD lateral)** | ILD = +5.40 dB (Izq) e ILD = -6.38 dB (Der) | Correspondencia direccional clara (|ILD| > 1 dB) | **SI** |
| **Diferencia de nivel (ILD centro)** | ILD = -0.39 dB (Centro auxiliar) y -0.18 dB (Estéreo) | Simetría bilateral centrada (|ILD| < 1.5 dB) | **SI** |
| **Diferencia temporal (ITD fisiológico)** | ITD = +0.363 ms (Izq) e ITD = -0.317 ms (Der) | Retardo coherente con rango anatómico (< 0.70 ms) | **SI** |
| **Diferencia temporal (ITD centro)** | ITD = +0.023 ms (Centro auxiliar) y 0.000 ms (Estéreo) | Llegada temporal simultánea (|ITD| < 0.15 ms) | **SI** |
| **Trayectoria continua (test_sweep)** | Evolución suave y monótona de curvas ILD(t) e ITD(t) | Sin discontinuidades de fase en barridos dinámicos | **SI** |
| **Fidelidad de renderizado binaural** | Transferencia espacial coherente desde formato FOA | Síntesis HRTF psicoacústicamente válida | **SI** |
| **EVALUACIÓN GLOBAL** | Todos los criterios psicoacústicos conformes | Percepción binaural espacial coherente | **APROBADA** |

## 6. Evidencias Generadas en esta Carpeta
Los archivos de soporte cuantitativo y visual asociados a esta evaluación se encuentran organizados en las subcarpetas de `results/metrica_6/`:
- **`csv/`**: Archivos de datos numéricos detallados con las métricas calculadas.
- **`graficas/`**: Figuras en alta resolución que ilustran el comportamiento del sistema.
- **`tablas/`**: Tablas de resumen consolidadas en formato Excel (.xlsx).
- **`binaurales/`**: Audios binaurales estándar representativos.

## 7. Conclusiones Técnicas
- El motor de renderizado binaural basado en SOFA/HRTF transfiere con fidelidad física las propiedades direccionales de la escena Ambisonics.
- Los parámetros ITD e ILD satisfacen con rigor la teoría psicoacústica de localización en el plano horizontal.
- Se recomienda en el protocolo metodológico dar prioridad a señales de banda ancha para la verificación de ITD, reservando los tonos monofrecuenciales para el análisis de diferencias espectrales ILD.
