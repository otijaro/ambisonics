\# Scripts auxiliares (Utils)





\## Descripción



Esta carpeta contiene scripts generales utilizados como apoyo durante el proceso de validación del sistema Ambisonics.



Los scripts contenidos aquí no corresponden directamente a una métrica específica, sino que proporcionan herramientas para preparación, organización y verificación de los datos utilizados durante las pruebas.





\---



\# Archivos contenidos





\## generate\_test\_signals.py



Script utilizado para la generación de señales de prueba controladas.



Permite crear señales sintéticas utilizadas durante las etapas iniciales de validación, facilitando la evaluación del comportamiento del conversor bajo condiciones conocidas.





Tipos de señales utilizadas:



\- Impulsos.

\- Tonos senoidales.

\- Señales de prueba controladas.





\---



\## inventory\_audio.py



Script encargado de realizar un inventario de los bancos de audio utilizados durante la validación.



Permite verificar:



\- Archivos disponibles.

\- Organización de carpetas.

\- Cantidad de señales por banco.

\- Estructura de los conjuntos de prueba.





Los resultados generados sirven como apoyo para garantizar la correcta selección de señales utilizadas en cada métrica.





\---



\# Uso general



Estos scripts deben ejecutarse antes o durante la preparación de las métricas cuando sea necesario verificar o generar información sobre los bancos de prueba.





Ejemplo:



```bash

python inventory\_audio.py



o



python generate\_test\_signals.py

