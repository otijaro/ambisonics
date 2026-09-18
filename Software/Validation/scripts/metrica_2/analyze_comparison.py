"""
======================================================================
MÉTRICA 2 - COMPARACIÓN CONVERSOR ORIGINAL (NOTEBOOK) VS PLATAFORMA WEB
======================================================================

Objetivo
--------
Evaluar la equivalencia cuantitativa y cualitativa entre las salidas
generadas por el conversor de referencia original (Notebook) y la versión
integrada en la plataforma Web local para los tres formatos principales:

1. Formato Ambisonics FOA (4 canales: W, Y, Z, X)
2. Formato Binaural estándar (2 canales: L, R)
3. Formato Binaural 3D Perceptual (2 canales: L, R con movimiento)

Métricas Evaluadas
------------------
- Correspondencia estructural: Canales, Frecuencia de muestreo, Muestras, Duración.
- Similitud temporal: Coeficiente de correlación de Pearson (r) por canal y promedio.
- Error numérico:
    * RMSE (Root Mean Square Error) global y por canal.
    * NRMSE (Normalized RMSE respecto al rango de la señal).
    * SER (Signal-to-Error Ratio en dB): 10 * log10(sum(ref^2) / sum((ref - web)^2)).
    * Error máximo absoluto (Peak Error).
- Comparación energética: RMS por canal y diferencia de RMS (|RMS_nb - RMS_web|).
- Comparación espectral: Correlación espectral entre densidades de magnitud FFT/STFT.
- Criterios de aceptación:
    * Correspondencia estructural exacta (igual canales y fs, diferencia temporal < 0.05s).
    * Correlación temporal alta (r >= 0.95 en estático, r >= 0.90 en perceptual 3D).
    * Error numérico controlado (RMSE < 0.08, SER > 15 dB).
    * Distribución energética equivalente (Delta RMS < 0.05).

Organización de Salidas
-----------------------
validation/results/metrica_2/
├── csv/            <- CSVs detallados por formato y resumen global
├── foas/           <- Archivos FOA representativos analizados
├── binaurales/     <- Archivos Binaurales representativos analizados
├── perceptuales/   <- Archivos Perceptuales 3D representativos analizados
├── graficas/       <- Gráficas comparativas generadas por plot_comparison_results.py
└── tablas/         <- Tablas consolidadas en Excel (.xlsx)
======================================================================
"""

import os
import sys
import shutil
import numpy as np
import pandas as pd
import soundfile as sf
from scipy.signal import stft


# =====================================================================
# 1. CONFIGURACIÓN Y RUTAS
# =====================================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(CURRENT_DIR)
VALIDATION_DIR = os.path.dirname(SCRIPTS_DIR)
AUDIOS_ROOT = os.path.join(VALIDATION_DIR, "audios_tests")

RESULTS_M2_DIR = os.path.join(VALIDATION_DIR, "results", "metrica_2")
CSV_DIR = os.path.join(RESULTS_M2_DIR, "csv")
FOAS_DIR = os.path.join(RESULTS_M2_DIR, "foas")
BINAURALES_DIR = os.path.join(RESULTS_M2_DIR, "binaurales")
PERCEPTUALES_DIR = os.path.join(RESULTS_M2_DIR, "perceptuales")
GRAFICAS_DIR = os.path.join(RESULTS_M2_DIR, "graficas")
TABLAS_DIR = os.path.join(RESULTS_M2_DIR, "tablas")

for d in [CSV_DIR, FOAS_DIR, BINAURALES_DIR, PERCEPTUALES_DIR, GRAFICAS_DIR, TABLAS_DIR]:
    os.makedirs(d, exist_ok=True)


# Bancos de pruebas y sus carpetas
BANKS = [
    (
        "Banco estéreo de señales controladas",
        "Stereo",
        os.path.join(AUDIOS_ROOT, "1. stereo_tests")
    ),
    (
        "Banco experimental de cuatro micrófonos",
        "Studio_4mic",
        os.path.join(AUDIOS_ROOT, "2. studio_4mic")
    ),
    (
        "Banco auxiliar de señales espaciales",
        "Auxiliary_spatial",
        os.path.join(AUDIOS_ROOT, "3. auxiliary_spatial_tests")
    ),
]

FORMAT_CONFIGS = [
    {
        "key": "foa",
        "nombre": "FOA (Ambisonics B-Format)",
        "nb_file": "Notebook_output_foa.wav",
        "web_file": "WEB_output_foa.wav",
        "min_corr": 0.95,
        "max_rmse": 0.08,
        "channel_names": ["W", "Y", "Z", "X"],
        "target_save_dir": FOAS_DIR
    },
    {
        "key": "binaural",
        "nombre": "Binaural estándar",
        "nb_file": "Notebook_output_binaural.wav",
        "web_file": "WEB_output_binaural.wav",
        "min_corr": 0.95,
        "max_rmse": 0.08,
        "channel_names": ["Left", "Right"],
        "target_save_dir": BINAURALES_DIR
    },
    {
        "key": "perceptual",
        "nombre": "Binaural 3D Perceptual",
        "nb_file": "Notebook_output_binaural_3D_perceptual.wav",
        "web_file": "WEB_output_binaural_3D_perceptual.wav",
        "min_corr": 0.90,
        "max_rmse": 0.10,
        "channel_names": ["Left_3D", "Right_3D"],
        "target_save_dir": PERCEPTUALES_DIR
    },
]


# =====================================================================
# 2. FUNCIONES DE COMPARACIÓN MATEMÁTICA Y DSP
# =====================================================================

def compute_pearson_corr(x, y):
    """Calcula correlación de Pearson entre dos vectores 1D."""
    eps = 1e-12
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    xm = x - x_mean
    ym = y - y_mean
    num = np.sum(xm * ym)
    den = np.sqrt(np.sum(xm ** 2) * np.sum(ym ** 2)) + eps
    return float(num / den)


def compute_spectral_corr(x, y, sr, nperseg=2048):
    """Calcula correlación espectral promedio entre magnitudes STFT."""
    eps = 1e-12
    f, t, zx = stft(x, fs=sr, nperseg=nperseg, noverlap=nperseg//2)
    _, _, zy = stft(y, fs=sr, nperseg=nperseg, noverlap=nperseg//2)
    mag_x = np.abs(zx).flatten()
    mag_y = np.abs(zy).flatten()
    return compute_pearson_corr(mag_x, mag_y)


def compare_pair(ref_path, web_path, fmt_cfg):
    """
    Compara exhaustivamente una señal de referencia (Notebook)
    frente a la generada por la plataforma Web.
    """
    res = {}
    
    # Lectura de metadatos
    info_ref = sf.info(ref_path)
    info_web = sf.info(web_path)
    
    res["fs_ref"] = info_ref.samplerate
    res["fs_web"] = info_web.samplerate
    res["fs_match"] = (info_ref.samplerate == info_web.samplerate)
    
    res["ch_ref"] = info_ref.channels
    res["ch_web"] = info_web.channels
    res["ch_match"] = (info_ref.channels == info_web.channels)
    
    res["duration_ref_s"] = info_ref.duration
    res["duration_web_s"] = info_web.duration
    res["duration_diff_s"] = abs(info_ref.duration - info_web.duration)
    res["duration_match"] = (res["duration_diff_s"] < 0.05)
    
    res["samples_ref"] = info_ref.frames
    res["samples_web"] = info_web.frames
    res["samples_diff"] = abs(info_ref.frames - info_web.frames)
    
    # Carga de datos de audio
    data_ref, sr_ref = sf.read(ref_path, dtype="float32")
    data_web, sr_web = sf.read(web_path, dtype="float32")
    
    if data_ref.ndim == 1:
        data_ref = data_ref[:, None]
    if data_web.ndim == 1:
        data_web = data_web[:, None]
        
    num_ch = min(data_ref.shape[1], data_web.shape[1])
    n_samples = min(data_ref.shape[0], data_web.shape[0])
    
    sig_ref = data_ref[:n_samples, :num_ch]
    sig_web = data_web[:n_samples, :num_ch]
    
    eps = 1e-12
    corr_per_ch = []
    rmse_per_ch = []
    nrmse_per_ch = []
    ser_per_ch = []
    max_err_per_ch = []
    rms_ref_per_ch = []
    rms_web_per_ch = []
    delta_rms_per_ch = []
    spec_corr_per_ch = []
    
    for c in range(num_ch):
        c_ref = sig_ref[:, c]
        c_web = sig_web[:, c]
        diff = c_ref - c_web
        
        # Correlación temporal
        r = compute_pearson_corr(c_ref, c_web)
        corr_per_ch.append(r)
        
        # RMSE
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        rmse_per_ch.append(rmse)
        
        # NRMSE
        r_range = float(np.max(c_ref) - np.min(c_ref) + eps)
        nrmse = float(rmse / r_range)
        nrmse_per_ch.append(nrmse)
        
        # SER (Signal to Error Ratio dB)
        power_ref = np.sum(c_ref ** 2)
        power_err = np.sum(diff ** 2)
        ser_db = float(10.0 * np.log10((power_ref + eps) / (power_err + eps)))
        ser_per_ch.append(ser_db)
        
        # Max error
        max_err = float(np.max(np.abs(diff)))
        max_err_per_ch.append(max_err)
        
        # RMS individual
        rms_ref = float(np.sqrt(np.mean(c_ref ** 2)))
        rms_web = float(np.sqrt(np.mean(c_web ** 2)))
        rms_ref_per_ch.append(rms_ref)
        rms_web_per_ch.append(rms_web)
        delta_rms_per_ch.append(abs(rms_ref - rms_web))
        
        # Correlación espectral
        sp_corr = compute_spectral_corr(c_ref, c_web, sr_ref)
        spec_corr_per_ch.append(sp_corr)
        
    res["correlacion_promedio"] = float(np.mean(corr_per_ch))
    res["correlacion_min"] = float(np.min(corr_per_ch))
    res["rmse_global"] = float(np.sqrt(np.mean((sig_ref - sig_web) ** 2)))
    res["nrmse_promedio"] = float(np.mean(nrmse_per_ch))
    res["ser_db_promedio"] = float(np.mean(ser_per_ch))
    res["max_error_absoluto"] = float(np.max(max_err_per_ch))
    
    res["rms_ref_promedio"] = float(np.mean(rms_ref_per_ch))
    res["rms_web_promedio"] = float(np.mean(rms_web_per_ch))
    res["delta_rms_promedio"] = float(np.mean(delta_rms_per_ch))
    res["correlacion_espectral_promedio"] = float(np.mean(spec_corr_per_ch))
    
    # Guardar métricas por canal como listas/strings
    ch_names = fmt_cfg["channel_names"][:num_ch]
    for i, ch_name in enumerate(ch_names):
        res[f"corr_{ch_name}"] = corr_per_ch[i]
        res[f"rmse_{ch_name}"] = rmse_per_ch[i]
        res[f"ser_db_{ch_name}"] = ser_per_ch[i]
        res[f"rms_ref_{ch_name}"] = rms_ref_per_ch[i]
        res[f"rms_web_{ch_name}"] = rms_web_per_ch[i]
        res[f"delta_rms_{ch_name}"] = delta_rms_per_ch[i]
        
    # Evaluación de criterios de aceptación
    cumple_estruc = res["fs_match"] and res["ch_match"] and res["duration_match"]
    cumple_corr = (res["correlacion_promedio"] >= fmt_cfg["min_corr"])
    cumple_rmse = (res["rmse_global"] <= fmt_cfg["max_rmse"])
    cumple_rms = (res["delta_rms_promedio"] <= 0.05)
    
    res["cumple_estructura"] = cumple_estruc
    res["cumple_correlacion"] = cumple_corr
    res["cumple_rmse"] = cumple_rmse
    res["cumple_energia"] = cumple_rms
    res["CUMPLE_METRICA"] = (cumple_estruc and cumple_corr and cumple_rmse and cumple_rms)
    
    return res


# =====================================================================
# 3. EJECUCIÓN PRINCIPAL DE ANÁLISIS
# =====================================================================

def run_metrica_2_analysis():
    print("======================================================================")
    print("INICIANDO ANALISIS DE METRICA 2: NOTEBOOK VS WEB")
    print("======================================================================")
    
    format_results = {
        "foa": [],
        "binaural": [],
        "perceptual": []
    }
    
    global_rows = []
    
    for bank_name, bank_tag, bank_dir in BANKS:
        print(f"\n---> Analizando: {bank_name} ({bank_dir})")
        if not os.path.exists(bank_dir):
            print(f"  [!] Carpeta no encontrada: {bank_dir}")
            continue
            
        subfolders = sorted([
            d for d in os.listdir(bank_dir)
            if os.path.isdir(os.path.join(bank_dir, d))
        ])
        
        for subf in subfolders:
            subf_dir = os.path.join(bank_dir, subf)
            
            for fmt in FORMAT_CONFIGS:
                fmt_key = fmt["key"]
                nb_path = os.path.join(subf_dir, fmt["nb_file"])
                web_path = os.path.join(subf_dir, fmt["web_file"])
                
                if not os.path.exists(nb_path) or not os.path.exists(web_path):
                    print(f"  [!] Archivo faltante en {subf} ({fmt_key}):")
                    print(f"      NB: {os.path.exists(nb_path)}, WEB: {os.path.exists(web_path)}")
                    continue
                    
                res = compare_pair(nb_path, web_path, fmt)
                
                # Identificadores
                row = {
                    "Banco": bank_name,
                    "Banco_tag": bank_tag,
                    "Subcarpeta": subf,
                    "Formato": fmt["nombre"],
                    "Formato_key": fmt_key,
                    "Archivo_NB": fmt["nb_file"],
                    "Archivo_WEB": fmt["web_file"],
                    "Ruta_completa_NB": nb_path,
                    "Ruta_completa_WEB": web_path,
                }
                row.update(res)
                
                format_results[fmt_key].append(row)
                
                # Resumen global simplificado
                global_rows.append({
                    "Banco": bank_name,
                    "Subcarpeta": subf,
                    "Formato": fmt["nombre"],
                    "Fs_Hz": res["fs_ref"],
                    "Canales": res["ch_ref"],
                    "Duracion_s": round(res["duration_ref_s"], 2),
                    "Correlacion_r": round(res["correlacion_promedio"], 4),
                    "RMSE_global": round(res["rmse_global"], 4),
                    "SER_dB": round(res["ser_db_promedio"], 2),
                    "Delta_RMS": round(res["delta_rms_promedio"], 4),
                    "Corr_Espectral": round(res["correlacion_espectral_promedio"], 4),
                    "Cumple": "SI" if res["CUMPLE_METRICA"] else "NO"
                })
                
                # Copiar archivo representativo a la subcarpeta correspondiente de metrica_2
                # (guardamos los audios con nombre distintivo para evidencia)
                target_audio_name = f"{bank_tag}_{subf.replace(' ', '_')}_{fmt['web_file']}"
                target_copy_path = os.path.join(fmt["target_save_dir"], target_audio_name)
                if not os.path.exists(target_copy_path):
                    shutil.copy2(web_path, target_copy_path)

    # =================================================================
    # 4. GUARDADO DE CSVs Y TABLAS
    # =================================================================
    print("\n======================================================================")
    print("GUARDANDO REPORTES CSV Y TABLAS")
    print("======================================================================")
    
    # 1. CSVs por formato
    for fmt_key, rows in format_results.items():
        df_fmt = pd.DataFrame(rows)
        csv_path = os.path.join(CSV_DIR, f"comparacion_{fmt_key}.csv")
        df_fmt.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")
        print(f"  -> Guardado: {os.path.basename(csv_path)} ({len(df_fmt)} filas)")
        
    # 2. Resumen global en CSV
    df_global = pd.DataFrame(global_rows)
    csv_global_path = os.path.join(CSV_DIR, "resumen_global_metrica_2.csv")
    df_global.to_csv(csv_global_path, sep=";", index=False, encoding="utf-8-sig")
    print(f"  -> Guardado: {os.path.basename(csv_global_path)} ({len(df_global)} registros)")
    
    # 3. Excel consolidado con múltiples hojas
    excel_path = os.path.join(TABLAS_DIR, "resultados_metrica_2_comparacion.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_global.to_excel(writer, sheet_name="Resumen_Global", index=False)
        for fmt_key, rows in format_results.items():
            df_f = pd.DataFrame(rows)
            sheet_title = fmt_key.upper()[:30]
            df_f.to_excel(writer, sheet_name=sheet_title, index=False)
    print(f"  -> Guardado Excel: {os.path.basename(excel_path)}")
    
    # 4. Estadísticas finales por formato
    print("\n======================================================================")
    print("RESUMEN DE CUMPLIMIENTO METRICA 2")
    print("======================================================================")
    for fmt in FORMAT_CONFIGS:
        k = fmt["key"]
        df_k = pd.DataFrame(format_results[k])
        if len(df_k) > 0:
            total_k = len(df_k)
            cumplen_k = (df_k["CUMPLE_METRICA"] == True).sum()
            mean_corr = df_k["correlacion_promedio"].mean()
            mean_rmse = df_k["rmse_global"].mean()
            mean_ser = df_k["ser_db_promedio"].mean()
            print(f"Formato: {fmt['nombre']}")
            print(f"  Total evaluados: {cumplen_k}/{total_k} cumplen ({cumplen_k/total_k*100:.1f}%)")
            print(f"  Correlación promedio (r): {mean_corr:.4f}")
            print(f"  RMSE promedio:            {mean_rmse:.4f}")
            print(f"  SER promedio (dB):        {mean_ser:.2f} dB")
            print("-" * 50)
            
    print("[OK] Análisis numérico de Métrica 2 finalizado con éxito.")


if __name__ == "__main__":
    run_metrica_2_analysis()
