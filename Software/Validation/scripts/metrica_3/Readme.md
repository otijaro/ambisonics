# Métrica 3 - Evaluación de Estabilidad del Procesamiento durante la Conversión

## Descripción general
Esta carpeta contiene los scripts asociados a la evaluación de la **Métrica 3** del protocolo de validación experimental de la plataforma Ambisonics.

El objetivo de esta métrica es evaluar la estabilidad del procesamiento realizado por la plataforma web durante la conversión de señales estéreo multifuente a formato Ambisonics FOA y Binaural bajo diferentes duraciones (2 s a 600 s), verificando que la implementación por bloques (*streaming chunking* con Overlap-Add de 10 segundos) no introduzca discontinuidades, cortes, pérdida de información o alteraciones numéricas.

---

## Pruebas y banco evaluado
El análisis cubre señales de prueba desde impulsos ultracortos hasta pistas musicales extensas:
- `A01_impulso_center` (2 s)
- `A02_tono_1kHz_center`, `A02_tono_1kHz_left`, `A02_tono_1kHz_right` (10 s)
- `A03_ruido_blanco_30s` (30 s)
- `A04_cancion_corta_30s` (35.6 s)
- `A05_cancion_corta_1min` (56.6 s, inicio de procesamiento por bloques)
- `A06_cancion_larga_5mins` (281.4 s)
- `A07_cancion_larga_10mins` (578.1 s)

---

## Variables evaluadas
1. **Conservación temporal**: Coincidencia de duración entre audio original y salida ($\Delta T < 0.05$ s).
2. **Integridad de datos**: Conteo de valores inválidos (NaN, Inf) y saturación (clipping).
3. **Continuidad temporal en fronteras de bloque**: Detección de saltos diferenciales en límites exactos de 10.0 s.
4. **Respuesta ante sobrecarga**: Comprobación de ausencia de excepciones o timeouts en audios de larga duración.

---

## Organización de resultados
```text
validation/results/metrica_3/
├── csv/
│   ├── estabilidad_duraciones.csv
│   └── continuidad_fronteras_bloque.csv
├── graficas/
│   ├── 01_conservacion_duracion.png
│   ├── 02_zoom_frontera_bloques.png
│   └── 03_saltos_amplitud_limites.png
└── tablas/
    └── tablas_resumen_metrica_3.xlsx
```

---

## Ejecución
```bash
python Software/Validation/scripts/metrica_3/analyze_stability.py
python Software/Validation/scripts/metrica_3/plot_stability_results.py
```
