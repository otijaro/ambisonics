"""
======================================================================
MÉTRICA 3 - GENERACIÓN DE GRÁFICAS DE ESTABILIDAD Y CONTINUIDAD
======================================================================

Genera:
1. Gráfica 01: Conservación de duración (Entrada vs Salida) con regresión identidad.
2. Gráfica 02: Zoom micro-temporal a la frontera de bloque (10.0 s) demostrando continuidad de forma de onda.
3. Gráfica 03: Distribución de saltos de amplitud en límites de bloque vs salto intra-bloque.
======================================================================
"""

import os
import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)
AUDIOS_ROOT = os.path.join(VALIDATION_DIR, "audios_tests")

RESULTS_M3_DIR = os.path.join(VALIDATION_DIR, "results", "metrica_3")
CSV_DIR = os.path.join(RESULTS_M3_DIR, "csv")
GRAFICAS_DIR = os.path.join(RESULTS_M3_DIR, "graficas")

os.makedirs(GRAFICAS_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight"
})


def plot_duration_conservation(df_stab):
    print("  -> Generando Gráfica 01: Conservación temporal...")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    formatos = df_stab["Formato"].unique()
    colors = {"FOA": "#2563EB", "Binaural": "#10B981", "Perceptual_3D": "#8B5CF6"}
    
    for fmt in formatos:
        sub = df_stab[df_stab["Formato"] == fmt]
        ax.scatter(sub["Duracion_entrada_s"], sub["Duracion_salida_s"], label=f"Salida {fmt}",
                   color=colors.get(fmt, "#000000"), s=55, alpha=0.85, edgecolors="black", linewidth=0.5)
        
    max_val = max(df_stab["Duracion_entrada_s"].max(), df_stab["Duracion_salida_s"].max()) * 1.05
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=1.2, label="Línea de Identidad Exacta (y = x)")
    
    ax.set_xlabel("Duración de Entrada Original (s)")
    ax.set_ylabel("Duración de Salida Ambisonics / Binaural (s)")
    ax.set_title("Métrica 3 — Conservación Temporal de Duración ante Variaciones de Carga")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "01_conservacion_duracion.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_boundary_continuity_zoom():
    print("  -> Generando Gráfica 02: Zoom a frontera de bloque (10.0 s)...")
    # Usar A05 (cancion_corta_1min) o A06 (5min)
    case_dir = os.path.join(AUDIOS_ROOT, "1. stereo_tests", "A05_cancion_corta_1min")
    audio_path = os.path.join(case_dir, "WEB_output_binaural.wav")
    if not os.path.exists(audio_path):
        case_dir = os.path.join(AUDIOS_ROOT, "1. stereo_tests", "A04_cancion_corta_30s")
        audio_path = os.path.join(case_dir, "WEB_output_binaural.wav")
        
    if not os.path.exists(audio_path):
        print("  [!] Audio no encontrado para zoom de frontera.")
        return
        
    data, sr = sf.read(audio_path)
    if data.ndim > 1:
        sig = data[:, 0] # Canal L
    else:
        sig = data
        
    # Ventana de 40 ms centrada en t = 10.0 s (frontera del primer bloque streaming)
    t_center = 10.0
    win_ms = 40.0
    half_samples = int((win_ms / 2000.0) * sr)
    idx_center = int(t_center * sr)
    
    idx_start = max(0, idx_center - half_samples)
    idx_end = min(len(sig), idx_center + half_samples)
    
    t_axis = (np.arange(idx_start, idx_end) / sr - t_center) * 1000.0 # ms relativos a la frontera
    segment = sig[idx_start:idx_end]
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(t_axis, segment, color="#2563EB", linewidth=1.5, label="Forma de onda reconstruida (Streaming OLA)")
    ax.axvline(0, color="#DC2626", linestyle="--", linewidth=1.5, label="Frontera teórica de Bloque (t = 10.00 s)")
    
    ax.set_xlabel("Tiempo relativo a la frontera de bloque (ms)")
    ax.set_ylabel("Amplitud normalizada")
    ax.set_title("Métrica 3 — Continuidad Temporal en la Unión de Bloques (Sin Discontinuidades ni Clics)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "02_zoom_frontera_bloques.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_boundary_jump_distribution(df_cont):
    print("  -> Generando Gráfica 03: Distribución de saltos en límites...")
    if len(df_cont) == 0:
        return
        
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    saltos_frontera = df_cont["salto_frontera"].values
    saltos_medios = df_cont["salto_medio_local"].values
    
    ax.hist(saltos_medios, bins=15, alpha=0.6, color="#10B981", label="Salto diferencial intra-bloque (dinámica natural)", edgecolor="black")
    ax.hist(saltos_frontera, bins=15, alpha=0.7, color="#3B82F6", label="Salto en frontera exacta (límite de bloque)", edgecolor="black")
    
    ax.set_xlabel("Magnitud del salto absoluto entre muestras sucesivas (|x[i] - x[i-1]|)")
    ax.set_ylabel("Frecuencia de ocurrencia")
    ax.set_title("Métrica 3 — Comparación de Saltos en Límites de Bloque vs Variación Natural de la Señal")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "03_saltos_amplitud_limites.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def main():
    csv_stab = os.path.join(CSV_DIR, "estabilidad_duraciones.csv")
    csv_cont = os.path.join(CSV_DIR, "continuidad_fronteras_bloque.csv")
    
    if not os.path.exists(csv_stab):
        print(f"[!] No se encontró {csv_stab}. Ejecuta analyze_stability.py primero.")
        return
        
    df_stab = pd.read_csv(csv_stab, sep=";")
    df_cont = pd.read_csv(csv_cont, sep=";") if os.path.exists(csv_cont) else pd.DataFrame()
    
    plot_duration_conservation(df_stab)
    plot_boundary_continuity_zoom()
    if len(df_cont) > 0:
        plot_boundary_jump_distribution(df_cont)
        
    print("[OK] Gráficas de Métrica 3 generadas exitosamente.")


if __name__ == "__main__":
    main()
