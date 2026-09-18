# Métrica 4 - Evaluación del Desempeño Computacional de la Plataforma

## Descripción general
Esta carpeta contiene los scripts asociados a la evaluación de la **Métrica 4** del protocolo de validación experimental de la plataforma Ambisonics.

El objetivo de esta métrica es cuantificar la eficiencia computacional, el tiempo de procesamiento, el Factor de Tiempo Real ($RTF = T_{proc} / T_{audio}$) y la escalabilidad de recursos de hardware (CPU y RAM) bajo diferentes condiciones de carga operativa (desde 2 segundos hasta 10 minutos de audio continuo).

---

## Metodología y mediciones
Se integran las 19 mediciones empíricas de repetibilidad y carga registradas en la interfaz gráfica web durante la ejecución experimental (`METRICA 3.docx`):
- Impulsos controlados (2 s, 5 corridas de repetibilidad).
- Tonos senoidales a 1 kHz (10 s: centro, izquierda, derecha).
- Ruido blanco sintético (30 s, 3 corridas).
- Fragmentos musicales breves (35.6 s, 3 corridas).
- Música de media duración (56.6 s, 3 corridas).
- Audio musical de 5 minutos (281.4 s).
- Audio musical de 10 minutos (578.1 s).

---

## Resultados clave de desempeño
- **Factor de Tiempo Real promedio (RTF)**: $27.3\%$ ($0.273$). El sistema procesa el contenido a una velocidad promedio de **$3.88\times$ más rápido que el tiempo real**.
- **Linealidad y escalabilidad**: Coeficiente de correlación $R^2 = 0.99904$, demostrando un crecimiento perfectamente predecible y lineal sin saturación de recursos.
- **Memoria RAM**: Consumo constante inferior a $250\text{ MB}$ gracias a la técnica de streaming por bloques con Overlap-Add de 10 segundos.
- **Uso de CPU**: Distribución multinúcleo con ocupación media del $42.5\%$, garantizando estabilidad sin bloqueos de la interfaz web.

---

## Organización de resultados
```text
validation/results/metrica_4/
├── csv/
│   ├── rendimiento_computacional_detallado.csv
│   └── escalabilidad_duracion.csv
├── graficas/
│   ├── 01_tiempo_proc_vs_duracion.png
│   ├── 02_factor_tiempo_real_rtf.png
│   └── 03_escalabilidad_recursos.png
└── tablas/
    └── tablas_resumen_metrica_4.xlsx
```

---

## Ejecución
```bash
python Software/Validation/scripts/metrica_4/analyze_performance.py
python Software/Validation/scripts/metrica_4/plot_performance_results.py
```
