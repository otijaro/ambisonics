# Ambisonics
Proyecto ambisonics - Música - Electrónica

**Trabajo de grado**:
Plataforma Web para la Conversión de Audio Estéreo Multifuente a Formato Ambisonic

**Objetivo general**
Diseñar y desarrollar una plataforma web que convierta audio estéreo capturado desde múltiples micrófonos y configuraciones a sonido ambisonic, integrando técnicas de procesamiento digital de señales y una interfaz interactiva, con el fin de facilitar la creación de contenidos inmersivos en los ámbitos musical, académico y multimedia.

**Justificación**
El sonido ambisonic es una técnica avanzada de audio espacial que permite representar un campo sonoro tridimensional, brindando experiencias inmersivas fundamentales para la realidad virtual, los videojuegos, la producción musical y los entornos multimedia interactivos. Su implementación, sin embargo, suele requerir equipos de grabación específicos y software de alto costo, lo que restringe su uso a un número limitado de productores y entidades.

En la Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T) y la Escuela de Artes y Licenciatura en Música, existe un interés creciente por la exploración de técnicas de audio inmersivo para fines académicos, de investigación y creación artística. El Grupo de Conectividad y Procesamiento de Señales, el grupo A Tempo y el laboratorio Sonosfera cuentan con experiencia y recursos que pueden potenciar el desarrollo de una herramienta tecnológica innovadora. Actualmente, el laboratorio Sonosfera dispone de una Interfaz de Audio FOCUSRITE SCARLETT 18I20 INTERFAZ DE AUDIO/MIDI USB-C (4TA GENERACION 24 bits/192 Khz), cuatro monitores profesionales (MONITORES DE ESTUDIO KRK ROKIT 8 G4) y micrófonos especializados (micrófonos sm57 y 58 unidireccionales, Akg c414 multidireccional, entre otros), recursos que, combinados con técnicas de procesamiento digital de señales, pueden permitir la conversión de audio estéreo proveniente de múltiples configuraciones a formato ambisonic.

La propuesta consiste en desarrollar una plataforma web que procese audio estéreo capturado desde diferentes disposiciones de micrófonos, aplicando algoritmos de conversión para generar salidas ambisonic compatibles con estándares internacionales. Esto permitirá a músicos, ingenieros de sonido, investigadores y estudiantes experimentar con audio inmersivo sin necesidad de equipamiento especializado costoso. Además, fomentará la integración de conocimientos entre ingeniería y artes, abriendo oportunidades para la producción de contenidos innovadores y para la investigación interdisciplinaria.

Las siguientes son las restricciones identificadas:

La plataforma debe procesar archivos en formatos WAV y MP3 con frecuencias de muestreo mínimas de 44.1 kHz.

El tiempo de conversión no debe superar el 60 % de la duración del archivo original para un archivo de hasta 10 minutos.

El sistema debe ser accesible desde navegadores web estándar sin instalación de software adicional.

La salida debe cumplir con el formato Ambisonics B-format de primer orden, con posibilidad de extensión a órdenes superiores.

El procesamiento debe permitir la selección del tipo de configuración de micrófonos utilizada en la captura para optimizar la conversión.

