import cv2
import threading
import time
import numpy as np
from typing import Optional

class Camera:
    def __init__(self, index: int = 0):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")
        self.lock = threading.Lock()
        self.latest = None
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while self.running:
            ok, frame = self.cap.read()
            if ok:
                with self.lock:
                    self.latest = frame
            else:
                time.sleep(0.01)

    def get_frame(self) -> Optional[np.ndarray]:
        with self.lock:
            return None if self.latest is None else self.latest.copy()

    def release(self):
        self.running = False
        try:
            self.thread.join(timeout=0.5)
        except:  # noqa: E722
            pass
        self.cap.release()
