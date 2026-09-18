"""
======================================================================
MÉTRICA 4 - GENERACIÓN DE GRÁFICAS DE DESEMPEÑO COMPUTACIONAL
======================================================================

Genera:
1. Gráfica 01: Tiempo de procesamiento vs Duración del audio con regresión lineal y R^2.
2. Gráfica 02: Factor de Tiempo Real (RTF %) en función de la duración de audio.
3. Gráfica 03: Escalabilidad de recursos (Consumo de RAM constante y uso de CPU).
======================================================================
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)

RESULTS_M4_DIR = os.path.join(VALIDATION_DIR, "results", "metrica_4")
CSV_DIR = os.path.join(RESULTS_M4_DIR, "csv")
GRAFICAS_DIR = os.path.join(RESULTS_M4_DIR, "graficas")

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


def plot_proc_time_vs_duration(df_bench):
    print("  -> Generando Gráfica 01: Tiempo de procesamiento vs duración...")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    
    x = df_bench["Duracion_audio_s"].values
    y = df_bench["Tiempo_procesamiento_s"].values
    
    # Regresión
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r2 = r_value ** 2
    
    x_line = np.linspace(0, max(x) * 1.05, 100)
    y_line = slope * x_line + intercept
    
    # Línea tiempo real (y = x)
    ax.plot(x_line, x_line, 'k--', alpha=0.5, label="Límite Tiempo Real (y = x, RTF = 100%)")
    
    # Regresión lineal
    ax.plot(x_line, y_line, color="#DC2626", linewidth=1.8,
            label=f"Ajuste Lineal: T = {slope:.3f}·D + {intercept:.2f} (R² = {r2:.4f}, Velocidad: {1/slope:.1f}x)")
    
    # Datos experimentales
    ax.scatter(x, y, color="#2563EB", s=60, alpha=0.85, edgecolors="black", linewidth=0.6,
               label=f"Mediciones Empíricas UI Web (N = {len(df_bench)})", zorder=5)
    
    ax.set_xlabel("Duración del Audio de Entrada (s)")
    ax.set_ylabel("Tiempo de Procesamiento Requerido (s)")
    ax.set_title("Métrica 4 — Escalabilidad Computacional y Tiempo de Procesamiento vs Duración")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "01_tiempo_proc_vs_duracion.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_rtf_factor(df_bench):
    print("  -> Generando Gráfica 02: Factor de Tiempo Real (RTF %)...")
    fig, ax = plt.subplots(figsize=(9, 5))
    
    x = df_bench["Duracion_audio_s"].values
    y = df_bench["RTF_Porcentaje"].values
    
    ax.scatter(x, y, color="#10B981", s=65, alpha=0.85, edgecolors="black", linewidth=0.6, label="RTF (%) Medido", zorder=5)
    
    # Media global
    mean_rtf = np.mean(y)
    ax.axhline(mean_rtf, color="#2563EB", linestyle="-", linewidth=1.5,
               label=f"RTF Promedio = {mean_rtf:.1f}% (~{100/mean_rtf:.1f}x más rápido que tiempo real)")
    
    # Umbral de tiempo real
    ax.axhline(100.0, color="#DC2626", linestyle="--", linewidth=1.2, label="Límite Crítico Tiempo Real (100%)")
    
    ax.set_xlabel("Duración del Audio de Entrada (s)")
    ax.set_ylabel("Factor de Tiempo Real RTF (%)")
    ax.set_title("Métrica 4 — Factor de Tiempo Real (RTF) ante Variaciones de Duración")
    ax.set_ylim(10, 110)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "02_factor_tiempo_real_rtf.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_resource_scalability(df_bench):
    print("  -> Generando Gráfica 03: Escalabilidad de Recursos (RAM y CPU)...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    x = df_bench["Duracion_audio_s"].values
    ram = df_bench["RAM_consumo_MB"].values
    cpu = df_bench["CPU_uso_pct"].values
    
    # RAM
    ax1.plot(x, ram, 'o-', color="#8B5CF6", linewidth=1.5, markersize=6, label="RAM Consumida (MB)")
    ax1.axhline(500.0, color="#DC2626", linestyle="--", label="Límite Aceptación RAM (500 MB)")
    ax1.set_xlabel("Duración del Audio (s)")
    ax1.set_ylabel("Memoria RAM (MB)")
    ax1.set_title("Consumo de Memoria RAM (Estabilidad por Bloques OLA)")
    ax1.set_ylim(100, 600)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="lower right", framealpha=0.9)
    
    # CPU
    ax2.scatter(x, cpu, color="#F59E0B", s=55, edgecolors="black", linewidth=0.5, label="Uso CPU (%)")
    ax2.axhline(np.mean(cpu), color="#B45309", linestyle="-", linewidth=1.5, label=f"Uso Medio CPU = {np.mean(cpu):.1f}%")
    ax2.axhline(85.0, color="#DC2626", linestyle="--", label="Límite Saturación CPU (85%)")
    ax2.set_xlabel("Duración del Audio (s)")
    ax2.set_ylabel("Uso de CPU (%)")
    ax2.set_title("Utilización de Procesador durante la Conversión")
    ax2.set_ylim(20, 100)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="lower right", framealpha=0.9)
    
    plt.suptitle("Métrica 4 — Demostración de Eficiencia Computacional en Recursos de Hardware", fontsize=13, y=1.02)
    out_path = os.path.join(GRAFICAS_DIR, "03_escalabilidad_recursos.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def main():
    csv_path = os.path.join(CSV_DIR, "rendimiento_computacional_detallado.csv")
    if not os.path.exists(csv_path):
        print(f"[!] Archivo {csv_path} no encontrado. Ejecuta analyze_performance.py primero.")
        return
        
    df_bench = pd.read_csv(csv_path, sep=";")
    plot_proc_time_vs_duration(df_bench)
    plot_rtf_factor(df_bench)
    plot_resource_scalability(df_bench)
    print("[OK] Gráficas de Métrica 4 generadas exitosamente.")


if __name__ == "__main__":
    main()
