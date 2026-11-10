import argparse
import cv2
import numpy as np
from calibration import capture


def main():
    p = argparse.ArgumentParser(description='Read-only game-over diagnostic; no taps or saved files.')
    p.add_argument('--device')
    p.add_argument('--threshold', type=float, default=.9)
    p.add_argument('--frames', type=int, default=3)
    a = p.parse_args()
    if not 0 < a.threshold <= 1 or a.frames < 1:
        p.error('threshold must be in (0,1]; frames must be positive')
    print('Open the result screen on the phone. Select the entire yellow restart button, including its white triangle.')
    original = capture(a.device)
    scale = min(1., 960 / original.shape[0])
    def resized(frame):
        return cv2.resize(frame, None, fx=scale, fy=scale)
    first = resized(original)
    x,y,w,h = map(int, cv2.selectROI('Select restart button; Enter confirms', first, False, False))
    cv2.destroyAllWindows()
    if w < 12 or h < 12:
        raise RuntimeError('Selection cancelled or too small')
    template = first[y:y+h,x:x+w].copy()
    if template.std() < 5:
        raise RuntimeError('Select the button including the white triangle, not just a flat area')
    height,width = first.shape[:2]
    margin = max(8, int(height * .03))
    left,top = max(0,x-margin), max(0,y-margin)
    right,bottom = min(width,x+w+margin), min(height,y+h+margin)
    hits = 0
    print('Preview only. GAME_OVER means the selected button matched repeatedly; NOT_RUNNING_UNKNOWN otherwise.')
    print('Manually restart a round to verify that the detection disappears. Q or Esc exits.')
    while True:
        frame = capture(a.device)
        if frame.shape != original.shape:
            raise RuntimeError('Resolution changed; restart calibration')
        image = resized(frame)
        roi = image[top:bottom,left:right]
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        _,score,_,loc = cv2.minMaxLoc(result)
        match = np.isfinite(score) and score >= a.threshold
        hits = min(a.frames,hits+1) if match else 0
        status = 'GAME_OVER' if hits >= a.frames else ('VERIFYING' if hits else 'NOT_RUNNING_UNKNOWN')
        color = (0,0,255) if hits >= a.frames else (0,180,255)
        cv2.rectangle(image,(left,top),(right,bottom),color,1)
        if match:
            px,py = left+loc[0],top+loc[1]
            cv2.rectangle(image,(px,py),(px+w,py+h),color,2)
        cv2.putText(image,f'{status} {score:.2f} {hits}/{a.frames}',(8,25),0,.45,color,1)
        cv2.imshow('Read-only game-over preview',image)
        if cv2.waitKey(30) & 255 in (27,ord('q')) or cv2.getWindowProperty('Read-only game-over preview',cv2.WND_PROP_VISIBLE) < 1:
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('ERROR:',e)
        raise SystemExit(1)
    finally:
        cv2.destroyAllWindows()
