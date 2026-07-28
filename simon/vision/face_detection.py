import logging
from typing import Optional

import cv2

LOGGER = logging.getLogger("simon.vision")
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)


def detect_face(image_path: str) -> Optional[tuple[int, int, int, int]]:
    img = cv2.imread(image_path)
    if img is None:
        LOGGER.error("Image not found: %s", image_path)
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return int(x), int(y), int(w), int(h)


def wait_for_face(timeout: int = 30, camera_index: int = 0) -> bool:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        LOGGER.error("Cannot open camera")
        return False
    for _ in range(timeout * 10):
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            cap.release()
            return True
        cv2.waitKey(100)
    cap.release()
    return False
