# app/services/preview.py
import time
import cv2
import numpy as np
from typing import Optional
import os
import platform

def show_preview_and_capture(get_frame_func, timeout_ms: int = 15000) -> Optional[np.ndarray]:
    """
    Shows a live camera preview window and returns a captured frame when the user presses 'C'.
    Press 'Q' to cancel. Auto-timeout after timeout_ms.
    """
    title = "Enroll - press C to capture, Q to cancel"
    try:
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 900, 600)
    except cv2.error:
        # GUI not available (headless or no display)
        return None

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



from fastapi.responses import StreamingResponse
@router.get("/preview")
def preview_stream():
    global camera
    if camera is None:
        raise HTTPException(503, "Vision pipeline not ready")
    return StreamingResponse(mjpeg_generator(camera.get_frame),
                             media_type="multipart/x-mixed-replace; boundary=frame")

def mjpeg_generator(get_frame_func):
    # multipart/x-mixed-replace stream
    while True:
        frame = get_frame_func()
        if frame is None:
            time.sleep(0.01)
            continue
        ok, jpg = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")
        # keep it responsive
        time.sleep(0.02)
