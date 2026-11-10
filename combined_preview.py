import argparse
import time

import cv2
import numpy as np
from calibration import capture


def classify(button_hit, player_hit, previous_hits, required):
    hits = min(required, previous_hits + 1) if button_hit else 0
    if hits >= required:
        return 'GAME_OVER', hits
    if button_hit:
        return 'UNKNOWN', hits
    return ('PLAYER_VISIBLE' if player_hit else 'UNKNOWN'), hits


def select(image, title):
    x,y,w,h = map(int, cv2.selectROI(title, image, False, False))
    cv2.destroyAllWindows()
    if min(w,h) < 8:
        raise RuntimeError('Selection cancelled or too small')
    template = image[y:y+h,x:x+w].copy()
    if template.std() < 5:
        raise RuntimeError('Selection needs detail, not just a flat area')
    return (x,y,w,h), template


def match(image, template, origin=(0,0)):
    if image.shape[0] < template.shape[0] or image.shape[1] < template.shape[1]:
        return -1., (0,0)
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _,score,_,loc = cv2.minMaxLoc(result)
    if not np.isfinite(score):
        return -1., (0,0)
    return score, (loc[0]+origin[0],loc[1]+origin[1])


def draw(image, loc, template, color):
    h,w = template.shape[:2]
    cv2.rectangle(image,loc,(loc[0]+w,loc[1]+h),color,2)


def main():
    parser = argparse.ArgumentParser(description='Combined read-only preview. No input events or saved files.')
    parser.add_argument('--device')
    parser.add_argument('--player-threshold', type=float, default=.70)
    parser.add_argument('--button-threshold', type=float, default=.90)
    parser.add_argument('--frames', type=int, default=3)
    parser.add_argument('--self-test', action='store_true')
    a = parser.parse_args()
    if a.frames < 1 or not 0 < a.player_threshold <= 1 or not 0 < a.button_threshold <= 1:
        parser.error('Invalid thresholds or frame count')
    if a.self_test:
        assert classify(False,False,0,3) == ('UNKNOWN',0)
        assert classify(False,True,0,3) == ('PLAYER_VISIBLE',0)
        assert classify(True,True,0,3) == ('UNKNOWN',1)
        assert classify(True,True,2,3) == ('GAME_OVER',3)
        assert classify(False,False,3,3) == ('UNKNOWN',0)
        print('State logic tests passed; no ADB or detection test performed.')
        return
    print('Show the result screen on the phone, then press Enter here.')
    input()
    original = capture(a.device)
    shape = original.shape
    scale = min(1.,960 / original.shape[0])
    def resized(image):
        if image.shape != shape:
            raise RuntimeError('Resolution changed; restart calibration')
        return cv2.resize(image,None,fx=scale,fy=scale)
    first = resized(original)
    (x,y,w,h),button = select(first,'Select whole yellow restart button including triangle; Enter')
    margin = max(8,int(first.shape[0]*.03))
    left,top = max(0,x-margin),max(0,y-margin)
    right,bottom = min(first.shape[1],x+w+margin),min(first.shape[0],y+h+margin)
    print('Manually start a round on the phone. Then press Enter here to select the duck.')
    input()
    _,player = select(resized(capture(a.device)),'Select duck tightly without shadow; Enter')
    hits = 0
    previous = None
    print('Read-only. PLAYER_VISIBLE does not prove a round is running. Q or Esc exits.')
    while True:
        started = time.monotonic()
        image = resized(capture(a.device))
        button_score,button_loc = match(image[top:bottom,left:right],button,(left,top))
        player_score,player_loc = match(image,player)
        button_hit = button_score >= a.button_threshold
        player_hit = player_score >= a.player_threshold
        state,hits = classify(button_hit,player_hit,hits,a.frames)
        view = image.copy()
        if button_hit:
            draw(view,button_loc,button,(0,0,255))
        if player_hit and not button_hit:
            draw(view,player_loc,player,(255,255,0))
        elapsed = time.monotonic()-started
        cv2.rectangle(view,(0,0),(view.shape[1],68),(0,0,0),-1)
        cv2.putText(view,state,(8,20),0,.55,(255,255,255),1)
        cv2.putText(view,f'player={player_score:.2f} button={button_score:.2f}',(8,41),0,.42,(255,255,255),1)
        cv2.putText(view,f'button hits={hits}/{a.frames} frame={elapsed:.2f}s',(8,60),0,.42,(255,255,255),1)
        if state != previous:
            print(state)
            previous = state
        cv2.imshow('Combined read-only preview',view)
        if cv2.waitKey(30) & 255 in (27,ord('q')) or cv2.getWindowProperty('Combined read-only preview',cv2.WND_PROP_VISIBLE) < 1:
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
