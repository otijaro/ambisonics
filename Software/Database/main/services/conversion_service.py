# services/conversion_service.py
from pathlib import Path
import numpy as np
import soundfile as sf

def stereo_to_foa_placeholder(input_path: str, output_path: str) -> None:
    """
    Placeholder: genera WAV de 4 canales (W,X,Y,Z) a partir de L/R.
    - Lee WAV
    - Si es mono, replica L=R
    - W = (L+R)/2, X=L, Y=R, Z=0
    """
    data, sr = sf.read(input_path, always_2d=True)  # (frames, channels)

    if data.shape[1] == 1:
        L = data[:, 0]
        R = data[:, 0]
    else:
        L = data[:, 0]
        R = data[:, 1]

    W = (L + R) / 2.0
    X = L
    Y = R
    Z = np.zeros_like(W)

    out = np.stack([W, X, Y, Z], axis=1)  # (frames, 4)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, out, sr)
