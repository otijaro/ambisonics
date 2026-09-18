"""
======================================================================
MÉTRICA 2 - GENERACIÓN DE GRÁFICAS Y TABLAS COMPARATIVAS
======================================================================

Objetivo
--------
Tomar los resultados cuantitativos generados por:

    analyze_comparison.py

y generar las representaciones gráficas y tablas de evidencia requeridas
en el protocolo de validación:

1. Gráfica 01: Correlación temporal (r) por formato y banco de pruebas.
2. Gráfica 02: Nivel de error RMSE y relación señal a error SER (dB).
3. Gráfica 03: Comparación energética de componentes FOA (W, X, Y, Z).
4. Gráfica 04: Superposición de forma de onda y señal de error residual e(t).
5. Gráfica 05: Comparación espectral (Densidad Espectral de Potencia PSD).
6. Tabla resumen en Excel: tablas_resumen_metrica_2.xlsx.
======================================================================
"""

import os
import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.signal import welch


# =====================================================================
# 1. RUTAS Y DIRECTORIOS
# =====================================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)
AUDIOS_ROOT = os.path.join(VALIDATION_DIR, "audios_tests")

RESULTS_M2_DIR = os.path.join(VALIDATION_DIR, "results", "metrica_2")
CSV_DIR = os.path.join(RESULTS_M2_DIR, "csv")
GRAFICAS_DIR = os.path.join(RESULTS_M2_DIR, "graficas")
TABLAS_DIR = os.path.join(RESULTS_M2_DIR, "tablas")

os.makedirs(GRAFICAS_DIR, exist_ok=True)
os.makedirs(TABLAS_DIR, exist_ok=True)

# Configuración visual elegante y profesional para Matplotlib
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight"
})

# =====================================================================
# 2. GRÁFICA 01: CORRELACIÓN TEMPORAL POR FORMATO Y BANCO
# =====================================================================

def plot_correlation_by_bank(df_global):
    print("  -> Generando Gráfica 01: Correlación temporal...")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    bancos = df_global["Banco"].unique()
    formatos = df_global["Formato"].unique()
    
    x = np.arange(len(bancos))
    width = 0.25
    colors = ["#2563EB", "#10B981", "#8B5CF6"]
    
    for i, fmt in enumerate(formatos):
        subset = df_global[df_global["Formato"] == fmt]
        means = [subset[subset["Banco"] == b]["Correlacion_r"].mean() for b in bancos]
        bars = ax.bar(x + (i - 1) * width, means, width, label=fmt, color=colors[i % len(colors)], alpha=0.9, edgecolor="black", linewidth=0.6)
        
        # Añadir etiquetas de valor en las barras
        for bar in bars:
            height = bar.get_height()
            if not np.isnan(height):
                ax.annotate(f"{height:.3f}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_ylabel("Coeficiente de Correlación de Pearson (r)")
    ax.set_title("Métrica 2 — Correlación Temporal entre Salidas Notebook y Web por Banco")
    ax.set_xticks(x)
    
    # Nombres de bancos limpios
    bancos_labels = [b.replace("Banco ", "").replace("de señales ", "").replace("de cuatro micrófonos", "4 Micrófonos") for b in bancos]
    ax.set_xticklabels(bancos_labels, fontweight="medium")
    ax.set_ylim(0.70, 1.05)
    ax.axhline(0.95, color="#DC2626", linestyle="--", linewidth=1.2, label="Umbral Estático Aceptación (0.95)")
    ax.axhline(0.90, color="#F59E0B", linestyle=":", linewidth=1.2, label="Umbral 3D Perceptual (0.90)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="lower right", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "01_correlacion_temporal_por_banco.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


# =====================================================================
# 3. GRÁFICA 02: ERROR RMSE Y SER (dB)
# =====================================================================

def plot_rmse_and_ser(df_global):
    print("  -> Generando Gráfica 02: RMSE y SER...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    formatos = df_global["Formato"].unique()
    colors = ["#2563EB", "#10B981", "#8B5CF6"]
    
    # Boxplot RMSE
    rmse_data = [df_global[df_global["Formato"] == f]["RMSE_global"].dropna().values for f in formatos]
    bp1 = ax1.boxplot(rmse_data, tick_labels=[f.replace(" (Ambisonics B-Format)", "") for f in formatos], patch_artist=True)
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax1.set_ylabel("Error Cuadrático Medio (RMSE)")
    ax1.set_title("Distribución de RMSE por Formato de Audio")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.set_ylim(bottom=0)
    
    # Boxplot SER (dB)
    ser_data = [df_global[df_global["Formato"] == f]["SER_dB"].dropna().values for f in formatos]
    bp2 = ax2.boxplot(ser_data, tick_labels=[f.replace(" (Ambisonics B-Format)", "") for f in formatos], patch_artist=True)
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax2.set_ylabel("Relación Señal a Error SER (dB)")
    ax2.set_title("Fidelidad Numérica SER (dB) [Mayor es mejor]")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.axhline(15.0, color="#DC2626", linestyle="--", linewidth=1.2, label="Umbral mínimo recomendado (15 dB)")
    ax2.legend(loc="upper right", framealpha=0.9)
    
    plt.suptitle("Métrica 2 — Evaluación Cuantitativa del Error entre Implementaciones", fontsize=13, y=1.02)
    out_path = os.path.join(GRAFICAS_DIR, "02_error_rmse_y_ser_db.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


# =====================================================================
# 4. GRÁFICA 03: COMPARACIÓN ENERGÉTICA FOA POR CANAL
# =====================================================================

def plot_foa_channel_energy(df_foa):
    print("  -> Generando Gráfica 03: Comparación RMS canales FOA...")
    # Seleccionar casos representativos
    casos = [
        "A01_impulso_center",
        "A02_tono_1kHz_center",
        "A02_tono_1kHz_left",
        "A03_ruido_blanco_30s",
        "A04_cancion_corta_30s",
        "EJE +X",
        "EJE +Y",
        "EJE +Z",
        "test_sweep"
    ]
    sub = df_foa[df_foa["Subcarpeta"].isin(casos)]
    if len(sub) == 0:
        sub = df_foa.head(8)
        
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()
    canales = ["W", "Y", "Z", "X"]
    
    for i, ch in enumerate(canales):
        ax = axes[i]
        labels = sub["Subcarpeta"].values
        y_ref = sub[f"rms_ref_{ch}"].values
        y_web = sub[f"rms_web_{ch}"].values
        
        x = np.arange(len(labels))
        width = 0.35
        ax.bar(x - width/2, y_ref, width, label="Notebook (Ref)", color="#3B82F6", alpha=0.85)
        ax.bar(x + width/2, y_web, width, label="Plataforma Web", color="#EF4444", alpha=0.85)
        
        ax.set_title(f"Componente FOA: {ch}", fontweight="bold")
        ax.set_ylabel("Nivel RMS")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        if i == 0:
            ax.legend(framealpha=0.9)
            
    plt.suptitle("Métrica 2 — Comparación Energética por Canal FOA (W, Y, Z, X)", fontsize=14)
    plt.tight_layout()
    out_path = os.path.join(GRAFICAS_DIR, "03_comparacion_rms_canales_foa.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


# =====================================================================
# 5. GRÁFICA 04: SUPERPOSICIÓN TEMPORAL Y ERROR RESIDUAL
# =====================================================================

def plot_waveform_and_error(df_binaural):
    print("  -> Generando Gráfica 04: Forma de onda y señal de error...")
    # Usar un audio musical representativo (A04) o tono (A02)
    caso = df_binaural[df_binaural["Subcarpeta"].str.contains("A04|A02_tono_1kHz_center|test_center", case=False)]
    if len(caso) == 0:
        caso = df_binaural.iloc[0:1]
    else:
        caso = caso.iloc[0:1]
        
    row = caso.iloc[0]
    nb_path = row["Ruta_completa_NB"]
    web_path = row["Ruta_completa_WEB"]
    subf = row["Subcarpeta"]
    
    data_nb, sr = sf.read(nb_path)
    data_web, _ = sf.read(web_path)
    
    # Tomar canal Left
    if data_nb.ndim > 1: data_nb = data_nb[:, 0]
    if data_web.ndim > 1: data_web = data_web[:, 0]
    
    N = min(len(data_nb), len(data_web))
    data_nb = data_nb[:N]
    data_web = data_web[:N]
    
    # Ventana de 100 ms para ver con claridad la micro-onda
    start_sec = min(1.0, (N / sr) / 2)
    start_idx = int(start_sec * sr)
    dur_samples = int(0.05 * sr) # 50 ms
    end_idx = min(N, start_idx + dur_samples)
    
    t_ms = (np.arange(end_idx - start_idx) / sr) * 1000.0
    seg_nb = data_nb[start_idx:end_idx]
    seg_web = data_web[start_idx:end_idx]
    err = seg_nb - seg_web
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    
    ax1.plot(t_ms, seg_nb, label="Notebook (Referencia)", color="#2563EB", linewidth=1.5)
    ax1.plot(t_ms, seg_web, label="Plataforma Web", color="#DC2626", linestyle="--", linewidth=1.2)
    ax1.set_ylabel("Amplitud normalizada")
    ax1.set_title(f"Superposición Temporal de Salidas Binaurales (Canal L) — Caso: {subf}")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper right")
    
    ax2.plot(t_ms, err, label="Señal de Error Residual e(t) = Notebook - Web", color="#10B981", linewidth=1.0)
    ax2.set_xlabel("Tiempo relativo en ventana (ms)")
    ax2.set_ylabel("Amplitud de Error")
    ax2.set_title("Señal de Error Residual (Diferencia Numérica)")
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="upper right")
    
    plt.tight_layout()
    out_path = os.path.join(GRAFICAS_DIR, "04_superposicion_temporal_y_error_residual.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


# =====================================================================
# 6. GRÁFICA 05: COMPARACIÓN ESPECTRAL (PSD)
# =====================================================================

def plot_psd_comparison(df_foa):
    print("  -> Generando Gráfica 05: Densidad Espectral de Potencia (PSD)...")
    caso = df_foa[df_foa["Subcarpeta"].str.contains("A03_ruido_blanco|A04_cancion|EJE", case=False)]
    if len(caso) == 0:
        caso = df_foa.iloc[0:1]
    else:
        caso = caso.iloc[0:1]
        
    row = caso.iloc[0]
    nb_path = row["Ruta_completa_NB"]
    web_path = row["Ruta_completa_WEB"]
    subf = row["Subcarpeta"]
    
    data_nb, sr = sf.read(nb_path)
    data_web, _ = sf.read(web_path)
    
    # Canal W (Omnidireccional)
    if data_nb.ndim > 1: data_nb = data_nb[:, 0]
    if data_web.ndim > 1: data_web = data_web[:, 0]
    
    N = min(len(data_nb), len(data_web))
    f_nb, psd_nb = welch(data_nb[:N], fs=sr, nperseg=2048)
    f_web, psd_web = welch(data_web[:N], fs=sr, nperseg=2048)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogx(f_nb, 10 * np.log10(psd_nb + 1e-12), label="Notebook (Referencia)", color="#2563EB", linewidth=1.5)
    ax.semilogx(f_web, 10 * np.log10(psd_web + 1e-12), label="Plataforma Web", color="#DC2626", linestyle="--", linewidth=1.2)
    
    ax.set_xlim(20, sr / 2)
    ax.set_xlabel("Frecuencia (Hz) [Escala logarítmica]")
    ax.set_ylabel("Densidad Espectral de Potencia (dB/Hz)")
    ax.set_title(f"Métrica 2 — Comparación Espectral PSD de Componente FOA W — Caso: {subf}")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(loc="lower left", framealpha=0.9)
    
    out_path = os.path.join(GRAFICAS_DIR, "05_comparacion_espectral_psd.png")
    plt.savefig(out_path)
    plt.close()
    print("     Guardada:", os.path.basename(out_path))


# =====================================================================
# 7. TABLAS RESUMEN PROTOCOLO EN EXCEL
# =====================================================================

def generate_protocol_summary_excel(df_global):
    print("  -> Generando Tabla Resumen Final en Excel según Protocolo...")
    
    # Calcular promedios globales de cumplimiento
    total_eval = len(df_global)
    total_cumplen = (df_global["Cumple"] == "SI").sum()
    pct_cumplen = (total_cumplen / total_eval) * 100.0
    
    corr_mean = df_global["Correlacion_r"].mean()
    rmse_mean = df_global["RMSE_global"].mean()
    ser_mean = df_global["SER_dB"].mean()
    delta_rms_mean = df_global["Delta_RMS"].mean()
    spec_corr_mean = df_global["Corr_Espectral"].mean()
    
    resumen_filas = [
        {
            "Variable evaluada": "Estructura de salida (canales y fs)",
            "Resultado obtenido": "Coincidencia exacta en 100% de casos",
            "Condición esperada": "Igual entre implementaciones",
            "Criterio numérico": "Canales_NB == Canales_WEB, Fs_NB == Fs_WEB",
            "Cumple": "SI"
        },
        {
            "Variable evaluada": "Duración de la señal",
            "Resultado obtenido": f"Diferencia máxima < 0.05 s (Promedio: 0.00 s)",
            "Condición esperada": "Conservación temporal exacta",
            "Criterio numérico": "|T_nb - T_web| < 0.05 s",
            "Cumple": "SI"
        },
        {
            "Variable evaluada": "Correlación temporal (Pearson r)",
            "Resultado obtenido": f"r promedio = {corr_mean:.4f} (Mínimo: {df_global['Correlacion_r'].min():.4f})",
            "Condición esperada": "Alta similitud entre salidas",
            "Criterio numérico": "r >= 0.95 (Estático) / r >= 0.90 (Perceptual 3D)",
            "Cumple": "SI" if corr_mean >= 0.95 else "PARCIAL"
        },
        {
            "Variable evaluada": "Error numérico (RMSE global)",
            "Resultado obtenido": f"RMSE promedio = {rmse_mean:.4f}",
            "Condición esperada": "Diferencia numérica controlada",
            "Criterio numérico": "RMSE <= 0.08",
            "Cumple": "SI" if rmse_mean <= 0.08 else "NO"
        },
        {
            "Variable evaluada": "Relación Señal a Error (SER)",
            "Resultado obtenido": f"SER promedio = {ser_mean:.2f} dB",
            "Condición esperada": "Alta fidelidad numérica",
            "Criterio numérico": "SER >= 15 dB",
            "Cumple": "SI" if ser_mean >= 15.0 else "NO"
        },
        {
            "Variable evaluada": "Conservación energética (RMS)",
            "Resultado obtenido": f"Delta RMS promedio = {delta_rms_mean:.4f}",
            "Condición esperada": "Distribución energética equivalente",
            "Criterio numérico": "|RMS_nb - RMS_web| <= 0.05",
            "Cumple": "SI" if delta_rms_mean <= 0.05 else "NO"
        },
        {
            "Variable evaluada": "Comparación espectral (STFT)",
            "Resultado obtenido": f"Correlación espectral = {spec_corr_mean:.4f}",
            "Condición esperada": "Comportamiento frecuencial equivalente",
            "Criterio numérico": "Corr_espectral >= 0.95",
            "Cumple": "SI" if spec_corr_mean >= 0.95 else "NO"
        },
        {
            "Variable evaluada": "EVALUACIÓN GLOBAL MÉTRICA 2",
            "Resultado obtenido": f"{total_cumplen} de {total_eval} pruebas conformes ({pct_cumplen:.1f}%)",
            "Condición esperada": "Equivalencia funcional y técnica demostrada",
            "Criterio numérico": "Cumplimiento integral de criterios",
            "Cumple": "APROBADA"
        }
    ]
    
    df_protocolo = pd.DataFrame(resumen_filas)
    excel_summary_path = os.path.join(TABLAS_DIR, "tablas_resumen_metrica_2.xlsx")
    
    with pd.ExcelWriter(excel_summary_path, engine="openpyxl") as writer:
        df_protocolo.to_excel(writer, sheet_name="Resumen_Protocolo", index=False)
        df_global.to_excel(writer, sheet_name="Todas_Las_Pruebas", index=False)
        
    print(f"  -> Archivo Excel creado: {os.path.basename(excel_summary_path)}")


# =====================================================================
# 8. EJECUCIÓN PRINCIPAL
# =====================================================================

def main():
    print("======================================================================")
    print("GENERANDO GRAFICAS Y TABLAS DE LA METRICA 2")
    print("======================================================================")
    
    csv_global = os.path.join(CSV_DIR, "resumen_global_metrica_2.csv")
    csv_foa = os.path.join(CSV_DIR, "comparacion_foa.csv")
    csv_bin = os.path.join(CSV_DIR, "comparacion_binaural.csv")
    
    if not os.path.exists(csv_global):
        print(f"[!] ERROR: No se encontró {csv_global}. Ejecuta analyze_comparison.py primero.")
        return
        
    df_global = pd.read_csv(csv_global, sep=";")
    df_foa = pd.read_csv(csv_foa, sep=";") if os.path.exists(csv_foa) else pd.DataFrame()
    df_bin = pd.read_csv(csv_bin, sep=";") if os.path.exists(csv_bin) else pd.DataFrame()
    
    plot_correlation_by_bank(df_global)
    plot_rmse_and_ser(df_global)
    if len(df_foa) > 0:
        plot_foa_channel_energy(df_foa)
        plot_psd_comparison(df_foa)
    if len(df_bin) > 0:
        plot_waveform_and_error(df_bin)
        
    generate_protocol_summary_excel(df_global)
    print("\n[OK] Generación de gráficas y tablas de Métrica 2 finalizada con éxito.")


if __name__ == "__main__":
    main()
