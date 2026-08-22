# 04. Procesamiento Digital de Señales (DSP)

Este documento detalla la lógica matemática y de procesamiento de audio que reside principalmente en `backend/core_dsp.py`. El DSP es el "cerebro" de Ambisonic, encargado de convertir señales de audio en formatos inmersivos tridimensionales.

## Librerías Fundamentales
- **`numpy`:** Usado para procesamiento de arreglos vectorizados.
- **`scipy.signal`:** Para Transformada de Fourier a Corto Plazo (STFT / iSTFT) y convoluciones (`fftconvolve`).
- **`pysofaconventions`:** Para leer el archivo HRTF (.sofa).

## El Formato FOA (First Order Ambisonics)
Ambisonics no guarda audio por "canales de altavoz" (Izquierdo/Derecho), sino en un formato armónico esférico de 4 canales:
- **W:** Presión acústica global (Omnidireccional).
- **X:** Eje adelante-atrás.
- **Y:** Eje izquierda-derecha.
- **Z:** Eje arriba-abajo.

## Paso 1: Lectura y Normalización
1. El archivo entra al sistema y se analiza su duración.
2. Si es estéreo, se divide en L y R.
3. Se normaliza la señal (0.95 del pico máximo) mediante `normalize_multichannel` y se elimina la corriente continua (DC offset) restando la media global.

## Paso 2: Conversión (Codificación) a FOA

### Si el origen es Estéreo (`stereo_to_foa` / `stereo_to_foa_demo`)
Convertir estéreo a 3D espacial requiere "pseudo-espacializar" la señal usando análisis de espectro:
1. Se calcula la STFT del canal L y R.
2. Se extrae la señal Mid (suma) y Side (resta).
3. **Análisis Direccional (Azimut):** El balance de energía espectral entre L y R determina el ángulo horizontal del sonido (`np.arcsin(balance)`).
4. **Análisis de Altura (Elevación):** A través de un análisis del espectro alto (frecuencias > 3000Hz), la difusividad (falta de correlación) y la inclinación espectral, se genera un vector de "confianza de altura" (pseudo-elevación).
5. Se mapean M y S hacia la base espacial X, Y, Z usando senos y cosenos de estos ángulos inferidos.
6. Se hace la transformada inversa (iSTFT) para regresar al dominio del tiempo obteniendo (W, X, Y, Z).

### Si el origen es Tetraédrico (`tetra_aformat_to_foa`)
Para capturas reales de 4 micrófonos (A-Format), simplemente se aplica una **Matriz de Transformación (M_tetra)** estándar que decodifica las cápsulas hacia W, X, Y, Z sin necesidad de análisis de espectro (STFT), dado que el espacio físico ya fue capturado con exactitud.

## Paso 3: Renderizado a Binaural (HRTF)
El FOA es un formato de "transporte". Para que un humano lo escuche con audífonos, hay que pasarlo a Binaural.

### Uso de HRTF (`foa_to_binaural`)
1. Se utilizan respuestas al impulso relacionadas con la cabeza (`hrtf.sofa`), que contienen la forma en que los oídos humanos alteran el sonido según su dirección.
2. La técnica de Ambisonic instancia "Altavoces Virtuales" (`CONVERT_VIRTUAL_SPEAKERS`) en posiciones fijas en el espacio (frente, izquierda, derecha, atrás, elevación).
3. Las señales WXYZ se proyectan matemáticamente sobre estos altavoces.
4. Cada altavoz virtual sufre una **convolución Fast-Fourier (fftconvolve)** utilizando el par de filtros izquierdo/derecho del archivo HRTF correspondiente a ese punto.
5. Se suman todas las señales convolucionadas para construir un simple archivo de dos canales (L y R).
6. *Fallback:* Si el archivo HRTF no se encuentra, se utiliza una aproximación pasiva matemática (`foa_to_binaural_fallback`).

## Paso 4: Generación de Opciones (Salidas múltiples)
Además del binaural, el motor genera exportaciones alternativas para sistemas reales de altavoces (`foa_to_4_speakers`), mediante decodificación directa del FOA a arreglos cuádruples horizontales y de techo (altura).

## Paso 5: Estabilización de Loudness
Dado que convertir estéreo a Ambisonics y luego a binaural altera masivamente el volumen percibido debido a las cancelaciones de fase de la HRTF, se aplica una función `stabilize_loudness`. 
- Usa una ventana deslizante de energía (RMSE) de 450ms.
- Genera una curva envolvente (envelope).
- Inyecta ganancia a los pasajes que cayeron en intensidad, devolviendo un audio maestro competitivo con el estándar comercial.
