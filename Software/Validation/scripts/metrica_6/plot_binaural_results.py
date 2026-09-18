"""
======================================================================
MÉTRICA 6 - GENERACIÓN DE GRÁFICAS DE EVALUACIÓN BINAURAL (ITD E ILD)
======================================================================

Genera:
1. Gráfica 01: ILD (dB) por posición espacial y banco de pruebas.
2. Gráfica 02: ITD (ms) por posición espacial y banco de pruebas.
3. Gráfica 03: Funciones de correlación cruzada interaural demostrando el desplazamiento temporal del pico.
4. Gráfica 04: Trayectoria continua de ITD e ILD durante el barrido espacial (test_sweep).
======================================================================
"""

import os
import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import correlate, correlation_lags


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)
AUDIOS_ROOT = os.path.join(VALIDATION_DIR, "audios_tests")

RESULTS_M6_DIR = os.path.join(VALIDATION_DIR, "results", "metrica_6")
CSV_DIR = os.path.join(RESULTS_M6_DIR, "csv")
GRAFICAS_DIR = os.path.join(RESULTS_M6_DIR, "graficas")

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


def plot_ild_by_position(df_bin):
    print("  -> Generando Gráfica 01: ILD por posición espacial...")
    fig, ax = plt.subplots(figsize=(9.5, 5))
    
    bancos = df_bin["Banco_tag"].unique()
    x = np.arange(len(bancos))
    width = 0.26
    
    posiciones = ["Izquierda", "Centro", "Derecha"]
    colors = ["#2563EB", "#10B981", "#EF4444"]
    
    for i, pos in enumerate(posiciones):
        vals = []
        for b in bancos:
            sub = df_bin[(df_bin["Banco_tag"] == b) & (df_bin["Direccion"].str.lower().str.contains(pos.lower()[:3]))]
            if len(sub) > 0:
                vals.append(sub["ILD_dB"].values[0])
            else:
                vals.append(np.nan)
                
        bars = ax.bar(x + (i - 1) * width, vals, width, label=f"Posición: {pos}", color=colors[i], alpha=0.85, edgecolor="black", linewidth=0.6)
        
        for bar in bars:
            h = bar.get_height()
            if not np.isnan(h):
                va_pos = "bottom" if h >= 0 else "top"
                y_offset = 0.4 if h >= 0 else -0.4
                ax.annotate(f"{h:+.1f} dB",
                            xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, y_offset * 6),
                            textcoords="offset points",
                            ha="center", va=va_pos, fontsize=8, fontweight="bold")
                            
    ax.set_ylabel("Diferencia de Nivel Interaural ILD (dB) [L - R]")
    ax.set_title("Métrica 6 — Diferencia de Nivel Interaural (ILD) según Posición Espacial")
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", " ") for b in bancos], fontweight="medium")
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(-12, 12)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "01_ild_por_posicion_espacial.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_itd_by_position(df_bin):
    print("  -> Generando Gráfica 02: ITD por posición espacial...")
    fig, ax = plt.subplots(figsize=(9.5, 5))
    
    bancos = df_bin["Banco_tag"].unique()
    x = np.arange(len(bancos))
    width = 0.26
    
    posiciones = ["Izquierda", "Centro", "Derecha"]
    colors = ["#2563EB", "#10B981", "#EF4444"]
    
    for i, pos in enumerate(posiciones):
        vals = []
        for b in bancos:
            sub = df_bin[(df_bin["Banco_tag"] == b) & (df_bin["Direccion"].str.lower().str.contains(pos.lower()[:3]))]
            if len(sub) > 0:
                vals.append(sub["ITD_ms"].values[0])
            else:
                vals.append(np.nan)
                
        bars = ax.bar(x + (i - 1) * width, vals, width, label=f"Posición: {pos}", color=colors[i], alpha=0.85, edgecolor="black", linewidth=0.6)
        
        for bar in bars:
            h = bar.get_height()
            if not np.isnan(h):
                va_pos = "bottom" if h >= 0 else "top"
                y_offset = 0.03 if h >= 0 else -0.03
                ax.annotate(f"{h:+.2f} ms",
                            xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, y_offset * 100),
                            textcoords="offset points",
                            ha="center", va=va_pos, fontsize=8, fontweight="bold")
                            
    ax.set_ylabel("Diferencia Temporal Interaural ITD (ms) [Adelanto Canal L]")
    ax.set_title("Métrica 6 — Diferencia Temporal Interaural (ITD) en Rango Fisiológico")
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", " ") for b in bancos], fontweight="medium")
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax.axhline(0.70, color="gray", linestyle=":", label="Límite anatómico humano (~0.70 ms)")
    ax.axhline(-0.70, color="gray", linestyle=":")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(-0.95, 0.95)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "02_itd_por_posicion_espacial.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_cross_correlation_curves():
    print("  -> Generando Gráfica 03: Correlograma cruzado interaural...")
    # Usar casos del banco auxiliar: test_left, test_center, test_right
    cases = [
        ("test_left", "Fuente Izquierda (Adelanto L)", "#2563EB"),
        ("test_center", "Fuente Centro (Simetría bilateral)", "#10B981"),
        ("test_right", "Fuente Derecha (Adelanto R)", "#DC2626")
    ]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    for folder, label, col in cases:
        p = os.path.join(AUDIOS_ROOT, "3. auxiliary_spatial_tests", folder, "WEB_output_binaural.wav")
        if not os.path.exists(p):
            continue
            
        data, sr = sf.read(p)
        L = data[:int(2.0*sr), 0]
        R = data[:int(2.0*sr), 1]
        
        corr = correlate(R - np.mean(R), L - np.mean(L), mode='full')
        lags = correlation_lags(len(R), len(L), mode='full')
        
        max_lag = int(0.0015 * sr)
        mask = (np.abs(lags) <= max_lag)
        
        t_ms = (lags[mask] / sr) * 1000.0
        c_norm = corr[mask] / (np.max(np.abs(corr[mask])) + 1e-9)
        
        ax.plot(t_ms, c_norm, label=label, color=col, linewidth=1.6)
        
        # Marcar pico
        pk_idx = np.argmax(c_norm)
        ax.scatter([t_ms[pk_idx]], [c_norm[pk_idx]], color=col, s=50, zorder=5)
        ax.annotate(f"Pico: {t_ms[pk_idx]:+.2f} ms",
                    xy=(t_ms[pk_idx], c_norm[pk_idx]),
                    xytext=(0, 6), textcoords="offset points",
                    ha="center", fontsize=8, fontweight="bold", color=col)
                    
    ax.axvline(0, color="black", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Desfase temporal relativo (ms) [Lag]")
    ax.set_ylabel("Correlación cruzada normalizada")
    ax.set_title("Métrica 6 — Función de Correlación Cruzada Interaural R_LR(τ) y Localización del Pico ITD")
    ax.set_xlim(-1.2, 1.2)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "03_correlograma_cruzado.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def plot_sweep_trajectory():
    print("  -> Generando Gráfica 04: Trayectoria continua de barrido espacial...")
    csv_sweep = os.path.join(CSV_DIR, "evolucion_temporal_sweep.csv")
    if not os.path.exists(csv_sweep):
        print("  [!] Archivo de barrido no encontrado.")
        return
        
    df_sw = pd.read_csv(csv_sweep, sep=";")
    if len(df_sw) == 0:
        return
        
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    
    t = df_sw["tiempo_s"].values
    ild = df_sw["ild_db"].values
    itd = df_sw["itd_ms"].values
    
    # ILD
    ax1.plot(t, ild, color="#2563EB", linewidth=1.8, label="Diferencia de Nivel Interaural ILD(t)")
    ax1.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax1.set_ylabel("ILD (dB)")
    ax1.set_title("Métrica 6 — Evolución Continua de ILD e ITD durante Barrido Espacial (test_sweep)")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper right")
    
    # ITD
    ax2.plot(t, itd, color="#10B981", linewidth=1.8, label="Diferencia Temporal Interaural ITD(t)")
    ax2.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax2.set_xlabel("Tiempo transcurrido en el barrido (s)")
    ax2.set_ylabel("ITD (ms)")
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="upper right")
    
    plt.tight_layout()
    out_path = os.path.join(GRAFICAS_DIR, "04_trayectoria_sweep_itd_ild.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


def main():
    csv_path = os.path.join(CSV_DIR, "resultados_itd_ild.csv")
    if not os.path.exists(csv_path):
        print(f"[!] Archivo {csv_path} no encontrado. Ejecuta analyze_binaural_itd_ild.py primero.")
        return
        
    df_bin = pd.read_csv(csv_path, sep=";")
    plot_ild_by_position(df_bin)
    plot_itd_by_position(df_bin)
    plot_cross_correlation_curves()
    plot_sweep_trajectory()
    print("[OK] Gráficas de Métrica 6 generadas exitosamente.")


if __name__ == "__main__":
    main()
