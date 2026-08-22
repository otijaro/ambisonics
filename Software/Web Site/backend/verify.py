import os
import requests
import numpy as np
import soundfile as sf

# 1. Create a dummy 1-second stereo sine wave WAV file
test_wav = "test_stereo.wav"
sr = 44100
t = np.linspace(0, 1, sr, endpoint=False)
left = np.sin(2 * np.pi * 440 * t)
right = np.sin(2 * np.pi * 880 * t)
stereo = np.column_stack((left, right))

sf.write(test_wav, stereo, sr)
print(f"Created {test_wav} for testing.")

try:
    # 2. Test /api/health
    print("Testing /api/health...")
    res = requests.get("http://localhost:8000/api/health")
    print("Health Status:", res.status_code, res.json())

    # 3. Test /api/convert
    print("Testing /api/convert (this runs convert.ipynb and may take a moment)...")
    with open(test_wav, "rb") as f:
        files = {"audio": (test_wav, f, "audio/wav")}
        res = requests.post("http://localhost:8000/api/convert", files=files)
    print("Convert Status:", res.status_code)
    if res.status_code == 200:
        outputs = res.json().get("outputs", [])
        print("Generated Outputs:")
        for o in outputs:
            print(f"  - {o['key']}: wavUrl={o.get('wavUrl')}, mp3Url={o.get('mp3Url')}")
    else:
        print("Convert Error:", res.text)

    # 4. Test /api/demo
    print("Testing /api/demo (this runs demo.ipynb and may take a moment)...")
    with open(test_wav, "rb") as f:
        files = {"audio": (test_wav, f, "audio/wav")}
        data = {
            "direccion": "90",
            "altura": "20",
            "apertura": "60",
            "movimiento": "false"
        }
        res = requests.post("http://localhost:8000/api/demo", files=files, data=data)
    print("Demo Status:", res.status_code)
    if res.status_code == 200:
        outputs = res.json()
        print("Demo Outputs:")
        print(f"  - binaural: {outputs.get('binaural')}")
        print(f"  - binaural_3d: {outputs.get('binaural_3d')}")
    else:
        print("Demo Error:", res.text)

finally:
    # Clean up test wav
    if os.path.exists(test_wav):
        os.remove(test_wav)
        print("Cleaned up test file.")
