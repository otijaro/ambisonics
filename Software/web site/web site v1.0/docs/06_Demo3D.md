# 06. Visualización 3D (Demo Interactiva)

El módulo visualizador 3D se encuentra en `components/demo/visualizer-3d.tsx`. Su propósito es traducir los conceptos acústicos espaciales a un estímulo visual y kinestésico en la página, permitiendo a los usuarios entender "desde dónde viene" el sonido.

## Librerías Implementadas
- **Three.js (`three`):** Motor WebGL nativo utilizado para generar la matemática del lienzo y las geometrías base.
- **React Three Fiber (`@react-three/fiber`):** Puente de reconciliación de React para Three.js. Permite escribir grafos de escena WebGL mediante componentes declarativos de React (`<Canvas>`, `<ambientLight>`).
- **Drei (`@react-three/drei`):** Colección de utilidades listas para usar, principalmente empleadas para controles de cámara orbital (`OrbitControls`) y tipografía 3D (`Text`).

## Anatomía de la Escena (`Scene`)
1. **Oyente (Centro):**
   Se dibuja como un agrupamiento (`<group>`) estático compuesto por dos esferas unidas: la cabeza y el torso achatado en color verde reactivo a la luz (`meshStandardMaterial`).
2. **Fuente Sonora:**
   Representada por una esfera morada flotante. Esta esfera se crea asignándole una referencia a su malla (`const sphereRef = useRef<THREE.Mesh>(null)`).
3. **El Vector (Rayo de Conexión):**
   Implementado en el subcomponente `LinePoints`. Dibuja una línea (`<line>`) usando BufferGeometry, cuya posición inicial es el centro (0,0,0) y la final rastrea interactivamente el vector actual de `sphereRef`.

## Cálculo de Posiciones Físicas
La posición del sonido en el lienzo obedece directamente al estado (sliders de React) pasado vía props (`direccion`, `altura`, `apertura`, `movimiento`). El cálculo se realiza dentro del hook nativo de Fiber `useFrame` (que corre a 60 fps):

- **Azimut (Dirección horizontal):** Se toma el ángulo (en grados) y se convierte a radianes (`baseAzim = (direccion * Math.PI) / 180`).
- **Elevación (Altura):** Mismo cálculo a radianes desde la base.
- **Movimiento (Rotación automática):** Si el porcentaje es mayor a cero, se inyecta un *timeOffset* dependiente de `state.clock.getElapsedTime()` a la base azimutal.
- **Trigonometría (Mapeo Esférico a Cartesiano):**
  ```javascript
  const targetX = Math.sin(azimRad) * Math.cos(elevRad) * distance;
  const targetZ = -Math.cos(azimRad) * Math.cos(elevRad) * distance;
  const targetY = Math.sin(elevRad) * distance;
  ```
- **Animación suave (Lerp):** Para evitar brincos violentos, no se asigna la posición inmediatamente, sino mediante interpolación lineal (`sphereRef.current.position.lerp(..., 0.1)`).
- **Apertura (Escala):** Este parámetro no cambia la posición angular, modifica visualmente la escala (el tamaño) de la esfera.

## Cámara y Entorno
El entorno posee rejillas base (`gridHelper`) y anillos de alambre opacos (`ringGeometry`) para que el usuario pueda tener nociones de profundidad y piso físico.
La cámara se maneja de forma declarativa con `<OrbitControls>` de Drei, permitiendo orbitar libremente con el mouse, bloqueando el Zoom (`enableZoom={false}`) para proteger la cohesión de la interfaz web, e introduciendo topes angulares para que el usuario no termine "debajo" del suelo (`maxPolarAngle`, `minPolarAngle`).

## Reutilización del Componente
El componente visualizador posee dos modos controlados por la prop `mode`:
- `mode="interactive"` (usado en Demo): Habilita los cálculos trigonométricos dependientes de sliders del usuario.
- `mode="autoplay"` (usado en Inicio): Desconecta los cálculos trigonométricos de React. Automáticamente rota la cámara y mueve la esfera por el espacio mediante funciones de seno y coseno fijadas con el reloj, sirviendo como una hero-animación "zero-touch" para la landing page. Al recibir la prop `transparentBg=true`, elimina los bordes y el fondo degradado para mimetizarse totalmente con el diseño.
