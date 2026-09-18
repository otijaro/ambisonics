# Métrica 2 - Comparación del conversor original frente a la implementación en plataforma

## Descripción general
Esta carpeta contiene los scripts asociados a la evaluación de la **Métrica 2** del protocolo de validación experimental de la plataforma Ambisonics.

El objetivo de esta métrica es determinar el grado de equivalencia funcional, temporal, energética y espectral entre las salidas generadas por la implementación de referencia original desarrollada en los notebooks de investigación (`Notebook_output_*`) y las salidas generadas por el motor de procesamiento integrado en la plataforma web local (`WEB_output_*`).

---

## Formatos evaluados
La comparación se realiza para los tres formatos principales generados por el sistema:
1. **FOA (First Order Ambisonics B-format)**: 4 canales ($W, Y, Z, X$ en convención ACN/SN3D).
2. **Binaural estándar**: 2 canales ($L, R$) con convolución de HRTF basada en SOFA.
3. **Binaural 3D Perceptual**: 2 canales ($L, R$) con renderizado orbital tridimensional y estabilización de sonoridad (*loudness*).

---

## Banco de pruebas evaluado
El análisis cubre la totalidad de los 28 casos experimentales disponibles en `audios_tests/`:
- **Banco estéreo de señales controladas (9 subcarpetas)**: Impulsos, tonos sinusoidales de 1 kHz (centro, izquierda, derecha), ruido blanco (30s) y fragmentos musicales (30s, 1m, 5m, 10m).
- **Banco experimental de cuatro micrófonos (14 subcarpetas)**: Grabaciones en el laboratorio Sonosfera de ejes cartesianos ($+X, -X, +Y, -Y, +Z, -Z$) y direcciones diagonales en formato tetraédrico.
- **Banco auxiliar de señales espaciales (5 subcarpetas)**: Señales espaciales de alternancia, centro, izquierda, derecha y barrido (*sweep*).

---

## Métricas cuantitativas calculadas
- **Correspondencia estructural**: Coincidencia de canales ($N_{ch}$), frecuencia de muestreo ($f_s$), duración total y número de muestras.
- **Similitud temporal**: Coeficiente de correlación de Pearson ($r$) por canal y promedio multicanal.
- **Error numérico**: Error cuadrático medio ($RMSE$), $NRMSE$, error pico absoluto y relación señal a error ($SER$ en dB).
- **Consistencia energética**: Niveles $RMS$ por canal y diferencia de energía ($\Delta RMS = |RMS_{nb} - RMS_{web}|$).
- **Similitud espectral**: Correlación espectral basada en densidades de magnitud STFT.

---

## Organización de resultados
Los resultados generados se almacenan estructurados en:
```text
validation/results/metrica_2/
├── csv/
│   ├── comparacion_foa.csv
│   ├── comparacion_binaural.csv
│   ├── comparacion_perceptual.csv
│   └── resumen_global_metrica_2.csv
├── foas/
│   └── (Archivos FOA representativos de validación)
├── binaurales/
│   └── (Archivos Binaurales representativos de validación)
├── perceptuales/
│   └── (Archivos Perceptuales 3D representativos de validación)
├── graficas/
│   ├── 01_correlacion_temporal_por_banco.png
│   ├── 02_error_rmse_y_ser_db.png
│   ├── 03_comparacion_rms_canales_foa.png
│   ├── 04_superposicion_temporal_y_error_residual.png
│   └── 05_comparacion_espectral_psd.png
└── tablas/
    ├── resultados_metrica_2_comparacion.xlsx
    └── tablas_resumen_metrica_2.xlsx
```

---

## Ejecución
Para ejecutar el análisis completo de la Métrica 2:
```bash
python Software/Validation/scripts/metrica_2/analyze_comparison.py
python Software/Validation/scripts/metrica_2/plot_comparison_results.py
```
