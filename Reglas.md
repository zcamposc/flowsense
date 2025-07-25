Fase 1: Detección Básica en un Solo Frame
1. Cargar el Modelo YOLO: Inicializa un modelo pre-entrenado de Ultralytics (por ejemplo, yolov8n.pt, yolov8s.pt). Estos modelos ya han sido entrenados en el dataset COCO, que incluye la clase 'person'.
2. Cargar y Preparar una Imagen: Lee una sola imagen de un archivo. Asegúrate de que la imagen esté en el formato correcto (por ejemplo, RGB) y del tamaño adecuado si es necesario, aunque los modelos de Ultralytics suelen manejar esto automáticamente.
3. Realizar la Inferencia: Pasa la imagen a través del modelo cargado para obtener las detecciones. El resultado incluirá las coordenadas de los cuadros delimitadores (bounding boxes), la clase detectada y la confianza de la detección.
4. Filtrar Detecciones: De todos los objetos detectados, quédate únicamente con aquellos cuya clase sea 'person'.
5. Visualizar los Resultados: Dibuja los cuadros delimitadores de las personas detectadas directamente sobre la imagen original. Muestra la imagen resultante en una ventana o guárdala en un archivo.

Fase 2: Procesamiento Básico de Video
1. Cargar el Video: Abre el archivo de video utilizando una librería como OpenCV.
2. Leer el Video Frame a Frame: Inicia un bucle que lea el video cuadro por cuadro. Verifica que cada frame se haya leído correctamente.
3. Aplicar Detección a Cada Frame: Dentro del bucle, aplica los pasos 3 y 4 de la Fase 1 a cada frame individual. Es decir, detecta y filtra las personas en el cuadro actual.
4. Visualizar en Tiempo Real: Dibuja los cuadros delimitadores en cada frame procesado y muéstralo en una ventana. Esto creará la ilusión de un video con detecciones en tiempo real.
5. Finalizar la Ejecución: Asegura que el bucle pueda terminarse (por ejemplo, al presionar una tecla como 'q') y que todos los recursos, como la captura de video y las ventanas de visualización, se liberen correctamente.

Fase 3: Implementando el Seguimiento de Objetos (Tracking)
1. Modificar la Inferencia para Tracking: Cambia la llamada al modelo del modo de predicción (predict) al modo de seguimiento (track). El modelo de Ultralytics gestionará internamente el seguimiento.
2. Extraer IDs de Seguimiento: Al procesar el video en modo track, el resultado no solo incluirá las coordenadas del cuadro delimitador, sino también un ID de seguimiento (tracker_id) para cada persona detectada.
3. Visualizar con IDs: Dibuja el cuadro delimitador en cada frame y, además, muestra el tracker_id junto al cuadro. Esto permitirá ver cómo el sistema identifica a la misma persona a lo largo de diferentes frames.
4. Contar Personas Únicas: Implementa una lógica simple para contar cuántos IDs únicos han aparecido en el video. Esto te dará un conteo total de las personas que pasaron por la escena.

Fase 4: Análisis y Funcionalidades Avanzadas
1. Dibujar la Trayectoria: Almacena las coordenadas del centro de cada cuadro delimitador para cada tracker_id a lo largo del tiempo. Usa esta lista de puntos para dibujar una línea sobre el video que represente la trayectoria o el camino que ha seguido cada persona.
2. Definir Zonas de Interés (ROI - Region of Interest): Permite al usuario definir un polígono o un área específica en el video (por ejemplo, una puerta o un pasillo).
3. Detectar Cruces de Línea o Entradas a Zonas: Implementa una lógica para verificar si el centro del cuadro delimitador de una persona ha cruzado una línea virtual definida o ha entrado dentro del polígono de la zona de interés.
4. Generar Alertas o Eventos: Cuando se detecte un cruce de línea o una entrada a una zona, activa un evento. Esto podría ser tan simple como imprimir un mensaje en la consola (ej: "Persona con ID 5 ha entrado en la zona restringida") o algo más complejo como guardar un clip de ese momento.
5. Optimización del Rendimiento: Implementa técnicas para mejorar la velocidad de procesamiento. Por ejemplo, procesar solo uno de cada 'N' frames (salto de frames o frame skipping) o realizar la inferencia en un hilo separado para no bloquear la visualización del video. Esto es crucial para aplicaciones en tiempo real con cámaras de alta resolución.