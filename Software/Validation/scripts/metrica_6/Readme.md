# Métrica 6 - Evaluación Binaural mediante Diferencias ITD e ILD

## Descripción general
Esta carpeta contiene los scripts asociados a la evaluación de la **Métrica 6** del protocolo de validación experimental de la plataforma Ambisonics.

El objetivo de esta métrica es evaluar la coherencia de la información espacial transferida desde el formato First Order Ambisonics (FOA) hacia la salida binaural ($L, R$) sintetizada mediante filtros HRTF, analizando las dos claves psicoacústicas fundamentales de la audición espacial humana:
1. **ITD (Interaural Time Difference)**: Retraso temporal relativo entre las señales recibidas en ambos oídos.
2. **ILD (Interaural Level Difference)**: Diferencia de nivel de intensidad acústica en decibelios ($ILD = 20 \log_{10}(RMS_L / RMS_R)$) causada por el efecto de sombra acústica de la cabeza.

---

## Casos analizados
1. **Banco auxiliar espacial**:
   - `test_left`: Fuente lateral izquierda pura.
   - `test_center`: Fuente frontal centrada.
   - `test_right`: Fuente lateral derecha pura.
   - `test_sweep`: Barrido continuo espacial de izquierda a derecha.
2. **Banco estéreo controlado**:
   - `A02_tono_1kHz_left`, `A02_tono_1kHz_center`, `A02_tono_1kHz_right`.
3. **Banco experimental de cuatro micrófonos (Sonosfera)**:
   - `EJE +Y` (Izquierda), `EJE +X` (Frente), `EJE -Y` (Derecha).

---

## Resultados y observaciones técnicas
- **ILD**: Las fuentes posicionadas en el hemisferio izquierdo producen valores positivos marcados ($+3.66\text{ dB}$ a $+5.40\text{ dB}$), mientras que las fuentes en el hemisferio derecho generan valores negativos ($-3.81\text{ dB}$ a $-6.38\text{ dB}$), con el centro balanceado en torno a $0\text{ dB}$ ($\pm 0.4\text{ dB}$).
- **ITD**: En señales de banda ancha (`test_left`, `test_right`), el retardo temporal es de $\approx 0.32\text{ a } 0.36\text{ ms}$ ($\approx 15\text{ a } 17\text{ muestras}$ a $48\text{ kHz}$), perfectamente contenido dentro del rango fisiológico humano ($0\text{ a } 0.70\text{ ms}$). En tonos senoidales puros (1 kHz), la periodicidad de la onda induce ambigüedad de fase inherente a la teoría dúplex de Rayleigh.
- **Barrido dinámico**: La señal `test_sweep` demuestra una transición monótona y suave sin saltos abruptos de fase entre canales.

---

## Organización de resultados
```text
validation/results/metrica_6/
├── csv/
│   ├── resultados_itd_ild.csv
│   └── evolucion_temporal_sweep.csv
├── binaurales/
│   └── (Archivos binaurales analizados como evidencia)
├── graficas/
│   ├── 01_ild_por_posicion_espacial.png
│   ├── 02_itd_por_posicion_espacial.png
│   ├── 03_correlograma_cruzado.png
│   └── 04_trayectoria_sweep_itd_ild.png
└── tablas/
    └── tablas_resumen_metrica_6.xlsx
```

---

## Ejecución
```bash
python Software/Validation/scripts/metrica_6/analyze_binaural_itd_ild.py
python Software/Validation/scripts/metrica_6/plot_binaural_results.py
```
