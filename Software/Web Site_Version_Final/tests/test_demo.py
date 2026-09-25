import os
import sys
import time

# Añadir el directorio base al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.demo_processor import process_demo
from backend.core_dsp import load_sofa

def test_demo():
    print("Cargando SOFA...")
    try:
        hrtf, pos = load_sofa("Codigos/hrtf.sofa")
    except Exception:
        hrtf, pos = None, None
        print("SOFA no encontrado, usando fallback.")

    input_path = "backend/static/test_audio.wav"
    
    # Crear un audio falso de prueba
    import numpy as np
    import soundfile as sf
    sr = 44100
    t = np.linspace(0, 5, 5*sr)
    audio = np.sin(2*np.pi*440*t)
    audio_stereo = np.column_stack((audio, audio))
    os.makedirs("backend/static", exist_ok=True)
    sf.write(input_path, audio_stereo, sr)
    
    print("Ejecutando process_demo...")
    out_dir = "backend/static/test_out"
    
    start = time.time()
    process_demo(input_path, out_dir, direccion=30, altura=50, apertura=70, movimiento=40, hrtf=hrtf, pos=pos)
    print(f"Tiempo total: {time.time() - start:.2f}s")
    
if __name__ == "__main__":
    test_demo()
