\# Métrica 1 - Verificación estructural del formato FOA





\## Objetivo



Esta métrica tiene como objetivo verificar que la conversión realizada por el sistema Ambisonics genere correctamente señales en formato First Order Ambisonics (FOA).



Se evalúa la estructura de los canales, comportamiento energético y respuesta espacial esperada según la convención utilizada.





\---



\# Archivos de entrada



Los análisis utilizan los bancos de prueba ubicados en:





validation/audios\_tests/





Incluyendo:



\- Banco estéreo de señales controladas.

\- Banco experimental de cuatro micrófonos.





\---



\# Flujo de validación







Audio de entrada



&#x20;   ↓



Conversión FOA mediante funciones DSP del proyecto



&#x20;   ↓



Extracción de componentes W, X, Y, Z



&#x20;   ↓



Cálculo de métricas



&#x20;   ↓



Generación de tablas y gráficas







\---



\# Scripts principales





\## analyze\_foa\_structure.py



Realiza la validación estructural de las señales FOA.



Evalúa:



\- Número de canales.

\- Frecuencia de muestreo.

\- Duración.

\- Componentes W, X, Y, Z.

\- Valores RMS.

\- Valores inválidos NaN/Inf.

\- Clipping.

\- Relación direccional respecto a W.





\---



\## analyze\_tetra\_valid\_segments.py



Analiza las grabaciones experimentales del banco de cuatro micrófonos.



Evalúa los segmentos correspondientes a direcciones:



\- +X

\- -X

\- +Y

\- -Y

\- +Z

\- -Z





Permite verificar el comportamiento espacial esperado de las componentes FOA.





\---



\## plot\_foa\_results.py



Genera las gráficas utilizadas para el análisis de resultados.



Incluye:



\- RMS de componentes FOA.

\- Comportamiento direccional.

\- Comparación entre direcciones físicas.





\---



\# Scripts de diagnóstico





Los siguientes scripts fueron utilizados durante la etapa de desarrollo y comprobación del procesamiento:



\- diagnose\_tetra\_channel\_order.py

\- diagnose\_tetra\_raw\_channels.py

\- diagnose\_tetra\_time\_windows.py





Su función fue verificar:



\- Orden correcto de canales.

\- Integridad de señales.

\- Selección de ventanas temporales.





Estos scripts sirven como evidencia del proceso de depuración, aunque no forman parte del flujo final de generación de resultados.





\---



\# Resultados generados



Los resultados obtenidos se almacenan en:





validation/results/metrica\_1/





Incluyendo:



\- Tablas CSV.

\- Gráficas.

\- Archivos FOA generados durante la validación.





\---



\# Estado actual



La Métrica 1 corresponde a la primera etapa de validación del sistema y permite confirmar la correcta generación estructural y espacial del formato FOA antes de realizar comparaciones posteriores entre implementaciones.

