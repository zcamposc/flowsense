import cv2
import json

def draw_points(img, points, color=(0, 255, 0)):
    for pt in points:
        cv2.circle(img, pt, 5, color, -1)
    if len(points) > 1:
        cv2.polylines(img, [np.array(points)], False, color, 2)

def select_line(image_path):
    img = cv2.imread(image_path)
    clone = img.copy()
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Selecciona 2 puntos para la línea", img)

    cv2.imshow("Selecciona 2 puntos para la línea", img)
    cv2.setMouseCallback("Selecciona 2 puntos para la línea", click_event)
    while len(points) < 2:
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    return points

def select_polygon(image_path):
    img = cv2.imread(image_path)
    clone = img.copy()
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            if len(points) > 1:
                cv2.line(img, points[-2], points[-1], (255, 0, 0), 2)
            cv2.imshow("Haz clic para el polígono, Enter para terminar", img)

    cv2.imshow("Haz clic para el polígono, Enter para terminar", img)
    cv2.setMouseCallback("Haz clic para el polígono, Enter para terminar", click_event)
    while True:
        key = cv2.waitKey(1)
        if key == 13 and len(points) > 2:  # Enter
            break
    cv2.destroyAllWindows()
    return points

if __name__ == "__main__":
    import numpy as np
    image_path = "image_1.png"  # Cambia por tu imagen
    zonas = {"lines": [], "polygons": []}

    print("Selecciona una línea:")
    linea = select_line(image_path)
    zonas["lines"].append(linea)

    print("Selecciona un polígono:")
    poligono = select_polygon(image_path)
    zonas["polygons"].append(poligono)

    with open("zonas.json", "w") as f:
        json.dump(zonas, f, indent=2)
    print("Zonas guardadas en zonas.json")