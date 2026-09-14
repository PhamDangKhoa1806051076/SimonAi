"""
Simon Vision – Face detection and webcam monitoring.
Can run as a background watcher that greets when a face is detected.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import cv2

LOGGER = logging.getLogger("simon.vision")

FACE_CASCADE = None
try:
    if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
        CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)
        if FACE_CASCADE.empty():
            LOGGER.warning("Haar cascade file empty or not found: %s", CASCADE_PATH)
            FACE_CASCADE = None
except Exception as exc:
    LOGGER.warning("Could not initialize face cascade: %s", exc)



def detect_face(image_path: str) -> Optional[tuple[int, int, int, int]]:
    """Detect a face in an image file. Returns (x, y, w, h) or None."""
    if FACE_CASCADE is None:
        LOGGER.warning("Face detection is not available")
        return None
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
    """Wait until a face is detected via webcam. Returns True if found."""
    if FACE_CASCADE is None:
        LOGGER.warning("Face detection is not available")
        return False
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        LOGGER.error("Cannot open camera %d", camera_index)
        return False

    start = time.time()
    found = False
    try:
        while (time.time() - start) < timeout:
            ret, frame = cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                found = True
                break
            time.sleep(0.1)
    finally:
        cap.release()

    return found


class FaceWatcher:
    """
    Background thread that monitors webcam for face presence.
    Calls `on_face_detected()` when a face first appears (with cooldown).
    Calls `on_face_lost()` when face disappears for a duration.
    """

    def __init__(
        self,
        on_face_detected: Optional[Callable[[], None]] = None,
        on_face_lost: Optional[Callable[[], None]] = None,
        camera_index: int = 0,
        check_interval: float = 1.0,
        cooldown: float = 60.0,
        lost_timeout: float = 10.0,
    ) -> None:
        self.on_face_detected = on_face_detected
        self.on_face_lost = on_face_lost
        self.camera_index = camera_index
        self.check_interval = check_interval
        self.cooldown = cooldown
        self.lost_timeout = lost_timeout

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._face_present = False
        self._last_trigger_time = 0.0
        self._last_face_time = 0.0
        self._last_frame = None
        self._frame_lock = threading.Lock()

    def get_current_frame(self):
        """Thread-safely retrieve the latest captured camera frame."""
        with self._frame_lock:
            if self._last_frame is not None:
                return self._last_frame.copy()
        return None

    def _watch(self) -> None:
        """Main watch loop."""
        if FACE_CASCADE is None:
            LOGGER.warning("FaceWatcher: Classifier not available")
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            LOGGER.error("FaceWatcher: Cannot open camera %d", self.camera_index)
            return

        LOGGER.info("FaceWatcher started on camera %d", self.camera_index)

        try:
            while self._running:
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(self.check_interval)
                    continue

                with self._frame_lock:
                    self._last_frame = frame.copy()

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = FACE_CASCADE.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
                )

                now = time.time()

                if len(faces) > 0:
                    self._last_face_time = now

                    if not self._face_present:
                        # Face just appeared
                        self._face_present = True

                        if (now - self._last_trigger_time) >= self.cooldown:
                            self._last_trigger_time = now
                            LOGGER.info("Face detected – triggering greeting")
                            if self.on_face_detected:
                                try:
                                    self.on_face_detected()
                                except Exception:
                                    LOGGER.exception("on_face_detected callback failed")
                else:
                    # No face – check if it's been gone long enough
                    if self._face_present and (now - self._last_face_time) > self.lost_timeout:
                        self._face_present = False
                        LOGGER.info("Face lost")
                        if self.on_face_lost:
                            try:
                                self.on_face_lost()
                            except Exception:
                                LOGGER.exception("on_face_lost callback failed")

                time.sleep(self.check_interval)
        finally:
            cap.release()
            with self._frame_lock:
                self._last_frame = None
            LOGGER.info("FaceWatcher stopped")

    def start(self) -> None:
        """Start face watching in background."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._watch, daemon=True, name="simon-face-watcher")
        self._thread.start()

    def stop(self) -> None:
        """Stop face watching."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def face_present(self) -> bool:
        return self._face_present


# ------------------------------------------------------------------
# Tool functions for Simon Brain & GUI
# ------------------------------------------------------------------

_global_watcher: Optional[FaceWatcher] = None


def get_global_watcher() -> Optional[FaceWatcher]:
    """Get the active FaceWatcher instance if any."""
    return _global_watcher


def set_global_watcher(watcher: Optional[FaceWatcher]) -> None:
    """Set the active FaceWatcher instance."""
    global _global_watcher
    _global_watcher = watcher


def _acquire_frame(camera_index: int = 0):
    """
    Get a camera frame safely.
    If FaceWatcher is running, uses its latest frame to avoid camera device lock conflicts.
    Otherwise opens VideoCapture temporarily.
    Returns (frame, cap_to_release_or_None).
    """
    global _global_watcher
    if _global_watcher and _global_watcher.is_running:
        for _ in range(15):
            frame = _global_watcher.get_current_frame()
            if frame is not None:
                return frame, None
            time.sleep(0.1)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None, None

    for _ in range(6):
        ret, frame = cap.read()
        if ret and frame is not None:
            return frame, cap
        time.sleep(0.04)

    return None, cap


def check_camera_for_face(camera_index: int = 0) -> str:
    """Quét webcam ngay lập tức để kiểm tra xem có người/khuôn mặt ở trước máy tính không."""
    if FACE_CASCADE is None:
        return "Tính năng nhận diện khuôn mặt chưa sẵn sàng."

    frame, cap = _acquire_frame(camera_index)
    try:
        if frame is None:
            return "Không thể truy cập camera. Vui lòng kiểm tra webcam có đang kết nối không."

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        count = len(faces)
        if count == 0:
            return "Camera đang mở, hiện tại không phát hiện ai ở trước máy tính."
        elif count == 1:
            return "Phát hiện 1 người đang ở trước camera."
        else:
            return f"Phát hiện có {count} người đang ở trước camera."
    except Exception as exc:
        LOGGER.exception("Error checking camera for face")
        return f"Lỗi khi quét camera: {exc}"
    finally:
        if cap is not None:
            cap.release()


def capture_webcam_photo(camera_index: int = 0) -> str:
    """Chụp ảnh từ webcam máy tính và lưu vào Desktop."""
    frame, cap = _acquire_frame(camera_index)
    try:
        if frame is None:
            return "Không thể mở camera để chụp ảnh."

        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path.cwd()

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = desktop / f"webcam_{timestamp}.jpg"

        cv2.imwrite(str(filepath), frame)
        LOGGER.info("Webcam photo saved: %s", filepath)
        return f"Đã chụp ảnh từ webcam và lưu thành công tại: {filepath}"
    except Exception as exc:
        LOGGER.exception("Error capturing webcam photo")
        return f"Lỗi chụp ảnh webcam: {exc}"
    finally:
        if cap is not None:
            cap.release()


def toggle_face_watcher(enable: bool, on_detect_callback: Optional[Callable[[], None]] = None) -> str:
    """Bật hoặc tắt chế độ quan sát camera ngầm (Face Watcher)."""
    global _global_watcher
    if enable:
        if _global_watcher and _global_watcher.is_running:
            return "Chế độ quan sát camera (Face Watcher) hiện đã đang hoạt động."
        _global_watcher = FaceWatcher(
            on_face_detected=on_detect_callback,
            camera_index=0,
            cooldown=60.0,
        )
        _global_watcher.start()
        return "Đã kích hoạt chế độ quan sát camera. Simon sẽ tự động chào khi phát hiện Chủ nhân."
    else:
        if _global_watcher and _global_watcher.is_running:
            _global_watcher.stop()
            _global_watcher = None
            return "Đã tắt chế độ quan sát camera."
        return "Chế độ quan sát camera hiện đang không bật."

