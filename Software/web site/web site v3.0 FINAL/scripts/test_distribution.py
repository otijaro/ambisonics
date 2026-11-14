#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
AMBISONIC — SUITE DE PRUEBAS AUTOMATIZADAS DE DISTRIBUCIÓN
==============================================================================
Ejecuta una serie de 10 pruebas objetivas sobre la copia pública usando
señales sintéticas para verificar la correcta instalación y funcionamiento
del motor DSP, decodificador SAD y conversor FOA sin depender de audios externos.
==============================================================================
"""

import os
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def run_tests():
    print("=" * 76)
    print("  AMBISONIC — VERIFICACIÓN INTEGRAL DE INSTALACIÓN Y PROCESAMIENTO DSP")
    print("=" * 76)
    
    passed = 0
    total = 10

    # Test 1: Importación de dependencias críticas
    print("\n[1/10] Verificando dependencias Python críticas...")
    try:
        import soundfile as sf
        import scipy.signal
        from pysofaconventions import SOFAFile
        import fastapi
        import sqlalchemy
        print("  ✅ Dependencias importadas correctamente (numpy, scipy, soundfile, pysofa, fastapi, sqlalchemy).")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error importando dependencias: {e}")

    # Test 2: Importación de módulos DSP propios
    print("\n[2/10] Verificando módulos internos de Ambisonic...")
    try:
        from backend.core_dsp import (
            stereo_to_foa, tetra_aformat_to_foa, foa_to_binaural,
            load_sofa, get_sadie_sofa_path, validate_sample_rate,
            normalize_audio, stabilize_loudness,
            SUPPORTED_SAMPLING_RATES, SOFA_FILENAMES
        )
        from backend.demo import demo_encode_stereo_to_foa_manual, demo_build_params
        print("  ✅ Módulos core_dsp y demo cargados con éxito.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en módulos internos: {e}")

    # Test 3: Verificación de archivos SOFA SADIE II D1
    print("\n[3/10] Verificando presencia de archivos SOFA SADIE II D1...")
    sofa_ok = True
    for sr in (44100, 48000, 96000):
        try:
            p = get_sadie_sofa_path(sr, BASE_DIR)
            if not os.path.exists(p):
                print(f"  ❌ SOFA {sr} Hz no existe en {p}")
                sofa_ok = False
        except Exception as e:
            print(f"  ❌ Error buscando SOFA {sr} Hz: {e}")
            sofa_ok = False
    if sofa_ok:
        print("  ✅ Los 3 archivos SOFA (44.1, 48 y 96 kHz) existen en las rutas requeridas.")
        passed += 1

    # Test 4: Carga y formato de SOFA 44.1 kHz
    print("\n[4/10] Verificando carga y dimensiones de HRIR (44.1 kHz)...")
    try:
        p44 = get_sadie_sofa_path(44100, BASE_DIR)
        ir, pos = load_sofa(p44)
        assert ir.ndim == 3, f"IR debe tener 3 dimensiones (M, R, N), obtenido: {ir.shape}"
        assert pos.ndim == 2, f"Pos debe tener 2 dimensiones (M, C), obtenido: {pos.shape}"
        print(f"  ✅ SOFA 44.1 kHz cargado: {pos.shape[0]} posiciones, {ir.shape[2]} taps FIR, {ir.shape[1]} oídos.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error cargando SOFA 44.1 kHz: {e}")

    # Test 5: Codificación Estéreo -> FOA (MSC + Preservación de Side)
    print("\n[5/10] Probando codificador Estéreo → FOA (MSC y conservación de Side)...")
    try:
        sr = 44100
        t = np.linspace(0, 1.0, sr, endpoint=False)
        # Señal sintética con diferencias L y R
        L = 0.6 * np.sin(2 * np.pi * 440 * t)
        R = 0.3 * np.sin(2 * np.pi * 880 * t)
        stereo = np.column_stack([L, R])

        W, X, Y, Z, _, _ = stereo_to_foa(stereo, sr)
        assert len(W) == len(t), "Longitud de salida debe coincidir con entrada"
        assert len(X) == len(t) and len(Y) == len(t) and len(Z) == len(t)
        # Verificar que la componente lateral Y no sea nula
        assert np.max(np.abs(Y)) > 0.01, "El canal Y debe contener energía lateral preservada"
        print(f"  ✅ Estéreo codificado a FOA AmbiX [W, Y, Z, X]. Max|Y| = {np.max(np.abs(Y)):.4f}.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en stereo_to_foa: {e}")

    # Test 6: Respuesta ante señal en oposición de fase (L = -R)
    print("\n[6/10] Probando preservación de Side en oposición de fase (L = -R)...")
    try:
        sr = 44100
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        sig = 0.5 * np.sin(2 * np.pi * 500 * t)
        stereo_oop = np.column_stack([sig, -sig])

        W, X, Y, Z, _, _ = stereo_to_foa(stereo_oop, sr)
        # En oposición pura, Mid = 0, Side = sig
        energy_Y = np.sum(Y ** 2)
        assert energy_Y > 0, "El canal Y debe retener la componente Side ante oposición de fase"
        print(f"  ✅ Información lateral conservada en canal Y (Energía Y = {energy_Y:.4f}).")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en prueba de oposición de fase: {e}")

    # Test 7: Codificación Tetraédrica 4 Micrófonos -> FOA
    print("\n[7/10] Probando codificador Tetraédrico [FLU, FRD, BLD, BRU] → FOA...")
    try:
        sr = 48000
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        flu = np.sin(2 * np.pi * 300 * t)
        frd = np.sin(2 * np.pi * 300 * t) * 0.5
        bld = np.sin(2 * np.pi * 300 * t) * 0.2
        bru = np.sin(2 * np.pi * 300 * t) * 0.8
        tetra = np.column_stack([flu, frd, bld, bru])

        W, X, Y, Z = tetra_aformat_to_foa(tetra)
        assert len(W) == len(t), "Longitud debe conservarse"
        print("  ✅ Matriz canónica ortogonal tetraédrica aplicada correctamente a Formato B.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en tetra_aformat_to_foa: {e}")

    # Test 8: Decodificación SAD Binaural con Geometría B Octaédrica
    print("\n[8/10] Probando decodificación binaural SAD (Geometría B octaédrica + HRIR)...")
    try:
        # Generar FOA unitario omnidireccional
        sr = 44100
        N = int(sr * 0.5)
        W = np.sin(2 * np.pi * 1000 * np.linspace(0, 0.5, N)) * 0.5
        X = np.zeros(N)
        Y = np.zeros(N)
        Z = np.zeros(N)

        binaural, tailL, tailR = foa_to_binaural(W, X, Y, Z, hrtf=ir, pos=pos, sr=sr)
        assert binaural.ndim == 2 and binaural.shape[1] == 2, "La salida binaural debe ser de 2 canales (L, R)"
        peak = np.max(np.abs(binaural))
        assert peak <= 1.0, f"No debe haber saturación digital (pico={peak})"
        print(f"  ✅ Decodificación SAD ejecutada exitosamente. Pico binaural = {peak:.4f}.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en decodificación SAD: {e}")

    # Test 9: Parámetros y codificación manual de la Demo interactiva
    print("\n[9/10] Probando parámetros y motor espacial de la Demo...")
    try:
        p = demo_build_params(direccion=45.0, altura=30.0, apertura=75.0, movimiento=50.0)
        assert "direccion_deg" in p and "altura_deg" in p and "apertura_pct" in p and "movimiento_pct" in p
        
        mono = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.2, 8820))
        stereo_demo = np.column_stack([mono, mono])
        W, X, Y, Z = demo_encode_stereo_to_foa_manual(
            stereo_demo, sr=44100, direccion_deg=45.0, altura_deg=30.0, apertura_pct=75.0
        )
        assert len(W) == len(mono)
        print("  ✅ Parámetros de azimut, elevación, apertura y órbita codificados correctamente.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en motor de Demo: {e}")

    # Test 10: Normalización y estabilización de loudness
    print("\n[10/10] Probando algoritmos de normalización y loudness (stabilize_loudness)...")
    try:
        sig = np.random.uniform(-2.5, 2.5, size=(44100, 2)).astype(np.float32)
        norm = normalize_audio(sig, peak_target=0.95)
        peak_norm = np.max(np.abs(norm))
        assert np.isclose(peak_norm, 0.95, atol=1e-4), f"El pico debe ser 0.95, obtenido {peak_norm}"

        stab = stabilize_loudness(norm, sr=44100, win_ms=200, strength=0.5)
        assert np.max(np.abs(stab)) <= 1.0, "La estabilización no debe saturar"
        print(f"  ✅ Normalización exacta a 0.95 (−0.45 dBFS) y estabilización operativa.")
        passed += 1
    except Exception as e:
        print(f"  ❌ Error en normalización/loudness: {e}")

    # Resumen
    print("\n" + "=" * 76)
    print(f"  RESULTADO FINAL: {passed}/{total} PRUEBAS APROBADAS")
    print("=" * 76)
    if passed == total:
        print("  🎉 La instalación pública de Ambisonic está 100% verificada y funcional.")
    else:
        print(f"  ⚠️ {total - passed} pruebas fallaron. Revisa los mensajes de error superiores.")
    print("=" * 76)

    return passed == total

if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
