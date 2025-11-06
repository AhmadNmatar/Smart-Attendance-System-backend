# app/services/preview.py
import time
import cv2
import numpy as np
from typing import Optional
import os

def show_preview_and_capture(get_frame_func, timeout_ms: int = 15000) -> Optional[np.ndarray]:
    """
    Shows a live camera preview window and returns a captured frame when the user presses 'C'.
    Press 'Q' to cancel. Auto-timeout after timeout_ms.
    """
    # Basic guard for headless Linux servers (no DISPLAY)
    if os.name != "nt" and not os.environ.get("DISPLAY"):
        # No GUI available
        return None

    title = "Enroll - press C to capture, Q to cancel"
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 900, 600)

    start = time.time()
    captured = None

    while True:
        frame = get_frame_func()
        if frame is None:
            # no frame yet, keep spinning briefly
            cv2.waitKey(1)
            continue

        cv2.imshow(title, frame)
        key = cv2.waitKey(1) & 0xFF

        if key in (ord('c'), ord('C')):
            captured = frame.copy()
            break
        if key in (ord('q'), ord('Q')):
            break

        if (time.time() - start) * 1000 > timeout_ms:
            break

    cv2.destroyWindow(title)
    return captured
