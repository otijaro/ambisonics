\# Validación experimental - Plataforma Ambisonics





\## Descripción general



Esta carpeta contiene los archivos asociados al proceso de validación experimental de la plataforma de conversión de audio estéreo/multifuente hacia formato Ambisonics de primer orden (FOA).



La validación tiene como objetivo verificar el correcto funcionamiento del sistema desde diferentes perspectivas: estructura de las señales FOA generadas, comportamiento espacial, consistencia del procesamiento y comparación entre las diferentes etapas del sistema.



Los procesos desarrollados permiten mantener trazabilidad entre:



\- Señales de entrada utilizadas.

\- Procesamiento aplicado.

\- Scripts de análisis.

\- Resultados obtenidos.

\- Evidencias utilizadas en el informe final.





\---



\# Organización general



La carpeta validation está organizada en cuatro bloques principales:





validation/



├── audios\_tests/

│

├── scripts/

│

├── results/

│

└── Documents/





\---



\# 1. audios\_tests



Contiene los bancos de señales utilizados durante las pruebas experimentales.



Incluye:



\## Banco estéreo



Señales de prueba controladas utilizadas para verificar el comportamiento del conversor bajo entradas conocidas.



Ejemplos:



\- Impulsos.

\- Tonos senoidales.

\- Ruido blanco.

\- Fragmentos musicales.



\---



\## Banco experimental de cuatro micrófonos



Grabaciones obtenidas mediante el arreglo espacial de cuatro micrófonos.



Incluye pruebas realizadas para diferentes posiciones conocidas de la fuente:



\- +X

\- -X

\- +Y

\- -Y

\- +Z

\- -Z





\---



\## Banco auxiliar espacial



Señales adicionales utilizadas para pruebas específicas del comportamiento espacial.





\---



\# 2. scripts



Contiene los códigos desarrollados para ejecutar las diferentes métricas de validación.



Cada métrica se encuentra separada en su propia carpeta:





scripts/



├── metrica\_1/

│

├── metrica\_2/

│

├── metrica\_3/

│

└── metrica\_4/





Cada carpeta contiene:



\- Scripts de procesamiento.

\- Scripts de análisis.

\- Scripts de generación de tablas y gráficas.

\- README específico de la métrica.





\---



\# 3. results



Contiene los resultados generados durante la ejecución de los scripts.



La organización sigue la estructura:





results/



├── metrica\_1/

│

├── metrica\_2/

│

├── metrica\_3/

│

└── metrica\_4/





Cada carpeta puede contener:



\- Archivos CSV.

\- Tablas utilizadas en el informe.

\- Gráficas.

\- Resultados intermedios necesarios para la trazabilidad.





\---



\# 4. Documents



Contiene documentación complementaria utilizada durante el proceso de validación.



Puede incluir:



\- Protocolos de prueba.

\- Referencias técnicas.

\- Notas de desarrollo.

\- Documentación de apoyo.





\---



\# Flujo general de validación



El proceso general seguido es:





Banco de señales de audio



&#x20;   ↓



Organización e identificación de archivos



&#x20;   ↓



Procesamiento mediante el conversor Ambisonics



&#x20;   ↓



Obtención de señales FOA



&#x20;   ↓



Aplicación de métricas de validación



&#x20;   ↓



Generación de tablas y gráficas



&#x20;   ↓



Análisis de resultados







\---



\# Métricas de validación



Actualmente el proceso está dividido en las siguientes métricas:



\## Métrica 1

Verificación estructural y espacial del formato FOA.



Incluye:



\- Número de canales.

\- Orden de componentes W, X, Y, Z.

\- Frecuencia de muestreo.

\- Duración.

\- Valores RMS.

\- Validación de signos y predominio direccional.

\- Detección de valores inválidos y clipping.





\## Métrica 2



Comparación entre la implementación original del conversor y la versión integrada en la plataforma web.





\## Métrica 3



Evaluación de continuidad y consistencia del procesamiento por bloques.





\## Métrica 4



Pruebas adicionales de desempeño y validación del sistema.





\---



\# Reproducibilidad



Para ejecutar las validaciones:



1\. Instalar las dependencias indicadas.

2\. Ubicar los bancos de audio dentro de `audios\_tests`.

3\. Ejecutar los scripts correspondientes dentro de cada carpeta de métrica.

4\. Revisar los resultados generados dentro de `results`.



Cada métrica cuenta con su propio README donde se documenta:



\- Objetivo.

\- Procedimiento.

\- Scripts utilizados.

\- Archivos generados.

\- Interpretación de resultados.





\---



\# Consideraciones finales



La estructura implementada permite separar los datos experimentales, códigos de análisis y resultados obtenidos, facilitando la trazabilidad del proceso de validación y la reproducción de los experimentos realizados sobre la plataforma Ambisonics.





