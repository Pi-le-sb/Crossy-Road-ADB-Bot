import argparse
import subprocess
import time

import cv2
import numpy as np


def capture(device):
    cmd = ['adb'] + (['-s', device] if device else [])
    r = subprocess.run(cmd + ['exec-out', 'screencap', '-p'], capture_output=True, timeout=15)
    if r.returncode:
        raise RuntimeError(r.stderr.decode(errors='replace'))
    if not r.stdout:
        raise RuntimeError('ADB returned no image')
    img = cv2.imdecode(np.frombuffer(r.stdout, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError('Invalid PNG from ADB')
    return img


def points(image):
    clicks = []
    name = 'Click: feet, forward tile, right tile; Enter confirms; Esc cancels'
    def mouse(event, x, y, flags, data):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 3:
            clicks.append((x, y))
    cv2.namedWindow(name)
    cv2.setMouseCallback(name, mouse)
    try:
        while True:
            view = image.copy()
            for i, p in enumerate(clicks):
                cv2.circle(view, p, 5, (0, 0, 255), -1)
                cv2.putText(view, str(i + 1), p, 0, .7, (255, 255, 255), 2)
            cv2.imshow(name, view)
            key = cv2.waitKey(30) & 255
            if key == 27 or cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1:
                raise RuntimeError('Calibration cancelled')
            if key in (10, 13) and len(clicks) == 3:
                return np.asarray(clicks, dtype=float)
            if key == ord('r'):
                clicks.clear()
    finally:
        cv2.destroyWindow(name)


def main():
    p = argparse.ArgumentParser(description='Read-only preview. No input events, no files saved.')
    p.add_argument('--device')
    p.add_argument('--threshold', type=float, default=.8)
    a = p.parse_args()
    if not 0 < a.threshold <= 1:
        p.error('threshold must be in (0, 1]')
    print('Start a round. Select the duck tightly, without its shadow; Enter confirms.')
    original = capture(a.device)
    scale = min(1., 960 / original.shape[0])
    def resize(img):
        return cv2.resize(img, None, fx=scale, fy=scale)
    initial = resize(original)
    x, y, w, h = map(int, cv2.selectROI('Select duck; Enter confirms', initial, False, False))
    cv2.destroyAllWindows()
    if w < 5 or h < 5:
        raise RuntimeError('Player selection cancelled or too small')
    template = initial[y:y+h, x:x+w].copy()
    if template.std() < 2:
        raise RuntimeError('Template has too little detail')
    print('Click 1: ground point between duck feet. Click 2: center of next forward tile.')
    print('Click 3: center of adjacent right tile. Enter confirms, R resets, Esc cancels.')
    anchor, forward, right = points(initial)
    forward -= anchor
    right -= anchor
    if min(np.linalg.norm(forward), np.linalg.norm(right)) < 5 or abs(np.linalg.det(np.array([forward, right]))) < 25:
        raise RuntimeError('Tile vectors too small or parallel; recalibrate')
    offset = anchor - np.array([x, y])
    print('Preview only: markers are geometry, NOT safe moves. Q or Esc exits. No files saved.')
    while True:
        start = time.monotonic()
        full = capture(a.device)
        if full.shape != original.shape:
            raise RuntimeError('Resolution changed; restart calibration')
        img = resize(full)
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, loc = cv2.minMaxLoc(result)
        view = img.copy()
        valid = np.isfinite(confidence) and confidence >= a.threshold
        if valid:
            cv2.rectangle(view, loc, (loc[0]+w, loc[1]+h), (255, 255, 0), 2)
            base = np.array(loc) + offset
            for row in range(5):
                for col in range(-2, 3):
                    center = base + row * forward + col * right
                    corners = [center + s * forward / 2 + t * right / 2 for s,t in [(-1,-1),(-1,1),(1,1),(1,-1)]]
                    cv2.polylines(view, [np.asarray(corners, dtype=np.int32)], True, (0, 180, 255), 1)
            cv2.circle(view, tuple(base.astype(int)), 5, (255, 255, 0), -1)
        label = f'{"MATCH" if valid else "LOST"} {confidence:.2f} | geometry only | {time.monotonic()-start:.2f}s'
        cv2.putText(view, label, (8, 25), 0, .45, (0, 0, 255), 1)
        cv2.imshow('Read-only calibration', view)
        if cv2.waitKey(30) & 255 in (27, ord('q')) or cv2.getWindowProperty('Read-only calibration', cv2.WND_PROP_VISIBLE) < 1:
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('ERROR:', e)
        raise SystemExit(1)
    finally:
        cv2.destroyAllWindows()
