import os
import numpy as np
import soundfile as sf


# =========================================================
# CONFIGURACIÓN
# =========================================================

SR = 48000
DURATION = 10.0

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__),
    "test_audio"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# 1. IMPULSO ESTÉREO
# =========================================================

duration_impulse = 2.0
N_impulse = int(SR * duration_impulse)

impulse = np.zeros((N_impulse, 2), dtype=np.float32)

# Impulso a los 0.5 segundos en ambos canales
sample_impulse = int(0.5 * SR)

impulse[sample_impulse, 0] = 0.8
impulse[sample_impulse, 1] = 0.8

sf.write(
    os.path.join(OUTPUT_DIR, "A01_impulso_center.wav"),
    impulse,
    SR
)


# =========================================================
# 2. TONO DE 1 kHz
# =========================================================

N = int(SR * DURATION)

t = np.arange(N) / SR

tone = np.sin(
    2 * np.pi * 1000 * t
).astype(np.float32)


# =========================================================
# CASO CENTRO
# L = R
# =========================================================

center = np.column_stack([
    0.5 * tone,
    0.5 * tone
])

sf.write(
    os.path.join(OUTPUT_DIR, "A02_tono_1kHz_center.wav"),
    center,
    SR
)


# =========================================================
# CASO IZQUIERDA
# Mayor energía en L
# =========================================================

left = np.column_stack([
    0.8 * tone,
    0.2 * tone
])

sf.write(
    os.path.join(OUTPUT_DIR, "A02_tono_1kHz_left.wav"),
    left,
    SR
)


# =========================================================
# CASO DERECHA
# Mayor energía en R
# =========================================================

right = np.column_stack([
    0.2 * tone,
    0.8 * tone
])

sf.write(
    os.path.join(OUTPUT_DIR, "A02_tono_1kHz_right.wav"),
    right,
    SR
)


print("========================================")
print("SEÑALES DE VALIDACIÓN GENERADAS")
print("========================================")
print("Frecuencia de muestreo:", SR, "Hz")
print()
print("Archivos:")
print("- A01_impulso_center.wav")
print("- A02_tono_1kHz_center.wav")
print("- A02_tono_1kHz_left.wav")
print("- A02_tono_1kHz_right.wav")
print()
print("Ubicación:")
print(OUTPUT_DIR)