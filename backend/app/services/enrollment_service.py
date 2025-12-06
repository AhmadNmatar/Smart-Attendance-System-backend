import cv2
import sys
import time
import os
from pathlib import Path

def main(out_dir: str, cam_index: int = 0, timeout_ms: int = 15000):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("ERR: Cannot open camera", file=sys.stderr)
        sys.exit(2)

    title = "Enroll - Press SPACE to start capturing (Q to quit)"
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 900, 600)

    start_time = time.time()
    saved = 0
    last_save_time = 0.0
    started = False

    while True:
        ok, frame = cap.read()
        if not ok:
            if (time.time() - start_time) * 1000 > timeout_ms:
                break
            cv2.waitKey(1)
            continue

        now = time.time()
        if started and saved < 10 and (now - last_save_time) > 0.5:
            filename = out_dir / f"frame_{saved + 1}.png"
            ok = cv2.imwrite(str(filename), frame)
            if not ok:
                print("ERR: Failed to save image", file=sys.stderr)
                sys.exit(4)
            saved += 1
            last_save_time = now

        if started:
            cv2.putText(frame, f"Saved: {saved}/10 (Q to quit)",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "Press SPACE to start capturing (Q to quit)",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow(title, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            started = True
        elif key in (ord('q'), ord('Q')):
            break
        if saved >= 10:
            break
        if (time.time() - start_time) * 1000 > timeout_ms:
            break

    cap.release()
    cv2.destroyAllWindows()

    if saved == 0:
        sys.exit(3)

if __name__ == "__main__":
    out_dir = sys.argv[1]
    cam_index = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    timeout_ms = int(sys.argv[3]) if len(sys.argv) >= 4 else 15000
    os.makedirs(out_dir, exist_ok=True)
    main(out_dir, cam_index, timeout_ms)
