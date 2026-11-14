#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
AMBISONIC — GESTIÓN Y VERIFICACIÓN DE BASES HRIR SADIE II D1
==============================================================================
Este script comprueba la presencia e integridad criptográfica (SHA-256) de
las tres bases SOFA oficiales de SADIE II (Sujeto D1) requeridas por la
plataforma para el decodificador SAD a 44.1, 48 y 96 kHz.

Fuente oficial:
  University of York AudioLab — SADIE II Spatial Audio Database
  https://www.york.ac.uk/sadie-project/database.html
  Registro Zenodo: https://zenodo.org/records/12092466 (D1_HRIR_SOFA.zip)
  Licencia: Apache License, Version 2.0 (Copyright 2018, University of York)
==============================================================================
"""

import os
import sys
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOFA_DIR = os.path.join(BASE_DIR, "backend", "sofa")

EXPECTED_SOFA = {
    44100: {
        "filename": "D1_44K_16bit_256tap_FIR_SOFA.sofa",
        "size": 36310650,
        "sha256": "efffbf7f8e963c8162f24f44944ed6f8a44f5d3c546e76a4d74a650a0e3766d2",
        "description": "HRIR SADIE II D1 a 44.1 kHz (16 bits, 256 taps FIR, SimpleFreeFieldHRIR)",
    },
    48000: {
        "filename": "D1_48K_24bit_256tap_FIR_SOFA.sofa",
        "size": 36310650,
        "sha256": "9af7cb19531e52fb7ae8ec92621e6ab62b1d5fe584b3742be36699a0ddb0ccd4",
        "description": "HRIR SADIE II D1 a 48 kHz (24 bits, 256 taps FIR, SimpleFreeFieldHRIR)",
    },
    96000: {
        "filename": "D1_96K_24bit_512tap_FIR_SOFA.sofa",
        "size": 72366402,
        "sha256": "49c46541517cd8c43927297fc9106b8a9aee7aec25c3a6ba6d144b6da2f98983",
        "description": "HRIR SADIE II D1 a 96 kHz (24 bits, 512 taps FIR, SimpleFreeFieldHRIR)",
    },
}

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_sofa_files():
    print("=" * 72)
    print("  AMBISONIC — VERIFICACIÓN DE BASES HRIR SADIE II D1 (Apache 2.0)")
    print("=" * 72)
    print(f"Directorio de destino: {SOFA_DIR}\n")

    os.makedirs(SOFA_DIR, exist_ok=True)
    all_ok = True

    for sr, info in EXPECTED_SOFA.items():
        fname = info["filename"]
        fpath = os.path.join(SOFA_DIR, fname)
        print(f"[{sr} Hz] {fname}:")

        if not os.path.exists(fpath):
            print(f"  ❌ NO ENCONTRADO en {fpath}")
            all_ok = False
            continue

        size = os.path.getsize(fpath)
        print(f"  - Tamaño: {size:,} bytes (esperado: {info['size']:,} bytes)")
        
        sha = compute_sha256(fpath)
        if sha == info["sha256"]:
            print(f"  ✅ Integridad SHA-256 verificada: {sha}")
        else:
            print(f"  ⚠️ HASH NO COINCIDE:")
            print(f"     Obtenido: {sha}")
            print(f"     Esperado: {info['sha256']}")
            all_ok = False
        print()

    print("=" * 72)
    if all_ok:
        print("  RESULTADO: Las 3 bases SOFA SADIE II D1 están instaladas y verificadas.")
        print("  La plataforma puede procesar audio nativo a 44.1, 48 y 96 kHz.")
    else:
        print("  RESULTADO: Faltan archivos SOFA o la verificación de hash falló.")
        print("\n  Para obtener los archivos oficiales:")
        print("  1. Descarga el archivo 'D1_HRIR_SOFA.zip' desde Zenodo:")
        print("     https://zenodo.org/records/12092466/files/D1_HRIR_SOFA.zip?download=1")
        print("     o visita https://www.york.ac.uk/sadie-project/database.html")
        print("  2. Extrae los tres archivos '.sofa' correspondientes al sujeto D1 en:")
        print(f"     {SOFA_DIR}")
        print("  3. Vuelve a ejecutar este script para confirmar su integridad.")
    print("=" * 72)

    return all_ok

if __name__ == "__main__":
    ok = verify_sofa_files()
    sys.exit(0 if ok else 1)

