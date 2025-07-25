import cv2
from ultralytics import YOLO
from typing import Optional
import typer
import json
import numpy as np


app = typer.Typer(help="Detección de personas en imágenes usando YOLO.")


def detectar_personas_en_imagen(
    image_path: str,
    model_path: str,
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar la imagen de salida"
    )
) -> None:
    """
    Detecta personas en una imagen usando un modelo YOLO y guarda la imagen
    resultante con los bounding boxes.

    Args:
        image_path (str): Ruta de la imagen de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar la imagen de salida.
            Si es None, se usará 'output_image.png'.

    Raises:
        FileNotFoundError: Si la imagen no se puede cargar.
    """
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen: {image_path}"
        )

    results = model(image)
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            if cls == 0:  # 0 es 'person' en COCO
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                label = f"person {conf:.2f}"
                cv2.rectangle(
                    image, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                cv2.putText(
                    image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )

    if output_path is None:
        output_path = 'output_image.png'
    cv2.imwrite(output_path, image)
    typer.echo(f"Imagen de salida guardada en: {output_path}")
    cv2.imshow('Detección de Personas', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cargar_zonas_desde_json(json_path: str):
    """
    Carga zonas de interés (líneas o polígonos) desde un archivo JSON.
    El formato esperado es:
    {
        "lines": [ [[x1, y1], [x2, y2]], ... ],
        "polygons": [ [[x1, y1], [x2, y2], [x3, y3], ...], ... ]
    }
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    lines = data.get('lines', [])
    polygons = data.get('polygons', [])
    return lines, polygons


def punto_en_poligono(point, polygon):
    """Devuelve True si el punto está dentro del polígono (usando ray casting)."""
    x, y = point
    poly = np.array(polygon)
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def cruza_linea(p1, p2, linea):
    """Devuelve True si el segmento p1-p2 cruza la línea definida por dos puntos."""
    a1, a2 = np.array(linea[0]), np.array(linea[1])
    b1, b2 = np.array(p1), np.array(p2)
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (ccw(a1, a2, b1) != ccw(a1, a2, b2))


@app.command()
def video(
    video_path: str = typer.Option(
        ..., 
        help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., 
        help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output_path: Optional[str] = typer.Option(
        None, 
        help="Ruta para guardar el video de salida con detecciones"
    )
) -> None:
    """
    Detecta personas en un video usando un modelo YOLO, mostrando los resultados en tiempo real
    y permitiendo guardar el video procesado. El bucle puede terminarse presionando 'q'.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar el video de salida. Si es None, no se guarda.
    """
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        typer.echo(f"No se pudo abrir el video: {video_path}")
        raise typer.Exit(code=1)

    writer = None
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (width, height)
        )

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if cls == 0:  # 0 es 'person' en COCO
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    label = f"person {conf:.2f}"
                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    cv2.putText(
                        frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
        cv2.imshow(
            'Detección de Personas en Video', frame
        )
        if writer is not None:
            writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    typer.echo("Procesamiento de video finalizado.")


@app.command()
def track(
    video_path: str = typer.Option(
        ..., 
        help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., 
        help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output_path: Optional[str] = typer.Option(
        None, 
        help="Ruta para guardar el video de salida con tracking"
    )
) -> None:
    """
    Detecta y hace seguimiento de personas en un video usando YOLO en modo tracking.
    Muestra los IDs de seguimiento únicos y cuenta el total de personas detectadas.
    El bucle puede terminarse presionando 'q'.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar el video de salida. Si es None, no se guarda.
    """
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        typer.echo(f"No se pudo abrir el video: {video_path}")
        raise typer.Exit(code=1)

    writer = None
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (width, height)
        )

    # Conjunto para almacenar IDs únicos de personas
    unique_person_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Realizar tracking en lugar de solo detección
        results = model.track(frame, persist=True)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()

            for box, track_id, conf, cls in zip(
                boxes, track_ids, confidences, classes
            ):
                if int(cls) == 0:  # 0 es 'person' en COCO
                    x1, y1, x2, y2 = map(int, box)
                    unique_person_ids.add(int(track_id))
                    
                    # Dibujar bounding box con ID de tracking
                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    
                    # Mostrar ID de tracking y confianza
                    label = f"ID: {int(track_id)} conf: {conf:.2f}"
                    cv2.putText(
                        frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )

        # Mostrar contador de personas únicas en el frame
        cv2.putText(
            frame, 
            f"Personas únicas: {len(unique_person_ids)}", 
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
        )

        cv2.imshow(
            'Tracking de Personas en Video', frame
        )
        if writer is not None:
            writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    
    typer.echo(
        f"Tracking finalizado. Total de personas únicas: {len(unique_person_ids)}"
    )
    typer.echo(
        f"IDs de personas detectadas: {sorted(unique_person_ids)}"
    )


@app.command()
def analyze(
    video_path: str = typer.Option(
        ..., help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    zones_json: Optional[str] = typer.Option(
        None, help="Archivo JSON con definición de zonas de interés (líneas/polígonos)"
    ),
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar el video de salida con análisis"
    )
) -> None:
    """
    Analiza el video: dibuja trayectorias, detecta cruces de línea y entradas a zonas de interés,
    y genera alertas/eventos. Permite definir zonas desde un archivo JSON.
    """
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        typer.echo(f"No se pudo abrir el video: {video_path}")
        raise typer.Exit(code=1)

    writer = None
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (width, height)
        )

    # Cargar zonas de interés
    lines, polygons = [], []
    if zones_json is not None:
        lines, polygons = cargar_zonas_desde_json(zones_json)

    # Diccionario para trayectorias: tracker_id -> lista de centros
    trayectorias = dict()
    # Para alertas de cruce/entrada
    ids_en_zona = set()
    ids_cruzaron_linea = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model.track(frame, persist=True)
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            for box, track_id, cls in zip(boxes, track_ids, classes):
                if int(cls) == 0:
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    # Trayectorias
                    if int(track_id) not in trayectorias:
                        trayectorias[int(track_id)] = []
                    trayectorias[int(track_id)].append((cx, cy))
                    # Dibuja trayectoria
                    pts = trayectorias[int(track_id)]
                    for i in range(1, len(pts)):
                        cv2.line(frame, pts[i-1], pts[i], (0, 0, 255), 2)
                    # Dibuja bounding box e ID
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame, f"ID:{int(track_id)}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )
                    # Detección de entrada a zona (polígono)
                    for poly in polygons:
                        if punto_en_poligono((cx, cy), poly) and int(track_id) not in ids_en_zona:
                            ids_en_zona.add(int(track_id))
                            typer.echo(f"[ALERTA] Persona ID {int(track_id)} ha entrado en una zona de interés.")
                    # Detección de cruce de línea
                    if len(pts) > 1:
                        for linea in lines:
                            if cruza_linea(pts[-2], pts[-1], linea) and int(track_id) not in ids_cruzaron_linea:
                                ids_cruzaron_linea.add(int(track_id))
                                typer.echo(f"[ALERTA] Persona ID {int(track_id)} ha cruzado una línea de interés.")
        # Dibuja zonas
        for linea in lines:
            cv2.line(frame, tuple(linea[0]), tuple(linea[1]), (255, 0, 0), 2)
        for poly in polygons:
            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=2)
        cv2.imshow('Análisis de Personas en Video', frame)
        if writer is not None:
            writer.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    typer.echo("Análisis de video finalizado.")


@app.command()
def main(
    image: str = typer.Option(
        ..., help="Ruta de la imagen de entrada"
    ),
    model: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output: Optional[str] = typer.Option(
        None, help="Ruta para guardar la imagen de salida"
    )
) -> None:
    """
    Procesa los argumentos de línea de comandos y ejecuta la detección de personas.
    """
    detectar_personas_en_imagen(image, model, output)


if __name__ == "__main__":
    app()
