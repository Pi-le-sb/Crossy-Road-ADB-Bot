"""Read-only YOLO object preview with existing local state calibration."""
import argparse
from pathlib import Path
import time
import cv2
from calibration import capture
from combined_preview import match,draw,classify
from persistent_preview import small
from profile_store import load_profile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--weights',type=Path,required=True)
    p.add_argument('--trust-weights',action='store_true',help='Explicitly trust the selected third-party model file')
    p.add_argument('--device')
    p.add_argument('--profile',type=Path,default=Path.home()/'.crossy-road-adb-bot'/'profile.npz')
    p.add_argument('--conf',type=float,default=.25)
    p.add_argument('--imgsz',type=int,default=960)
    p.add_argument('--compute',default='cpu',help='Inference device, e.g. cpu or 0')
    p.add_argument('--image',type=Path,help='Test a local screenshot instead of ADB')
    a = p.parse_args()
    weights = a.weights.expanduser().resolve()
    if not weights.is_file() or weights.suffix.lower() not in ('.pt','.onnx'):
        p.error('Select an existing local .pt or .onnx detection model; nothing is downloaded automatically')
    if not a.trust_weights:
        p.error('Review the model source first, then explicitly pass --trust-weights. Model files are not guaranteed safe.')
    if not 0 < a.conf <= 1 or a.imgsz < 320 or a.imgsz%32:
        p.error('conf must be in (0,1]; imgsz must be >=320 and divisible by 32')
    try:
        from ultralytics import YOLO
    except ImportError as e:
        raise RuntimeError('Install optional dependencies: python -m pip install -r requirements-vision.txt') from e
    model = YOLO(str(weights),task='detect')
    profile_path = a.profile.expanduser()
    profile = load_profile(profile_path) if profile_path.exists() else None
    if profile is None:
        print('No local profile: object detection only; state remains UNKNOWN. No selection dialogs.')
    else:
        print('Reusing profile:',profile_path)
    print('Read-only. No taps, swipes, automatic restart or image saves. Q/Esc exits.')
    hits = 0
    shown_names = False
    name = 'YOLO read-only object preview'
    while True:
        started = time.monotonic()
        frame = cv2.imread(str(a.image)) if a.image else capture(a.device)
        if frame is None:
            raise RuntimeError('Could not load screenshot')
        result = model.predict(source=frame,imgsz=a.imgsz,conf=a.conf,device=a.compute,
                               verbose=False,save=False,save_txt=False,save_crop=False)[0]
        if result.boxes is None:
            raise RuntimeError('Model did not return detection boxes; select a detection model')
        if not shown_names:
            print('Actual model classes:',result.names)
            print('A class absent from this list cannot be added by lowering --conf.')
            shown_names = True
        view = small(result.plot())
        clean = small(frame)
        state = 'UNKNOWN'
        if profile is not None:
            if tuple(frame.shape[:2]) != tuple(profile['shape']):
                raise RuntimeError('Screen dimensions differ from profile; select a matching --profile')
            x,y,w,h = map(int,profile['box'])
            margin = max(8,int(clean.shape[0]*.03))
            left,top = max(0,x-margin),max(0,y-margin)
            right,bottom = min(clean.shape[1],x+w+margin),min(clean.shape[0],y+h+margin)
            bs,_ = match(clean[top:bottom,left:right],profile['button'],(left,top))
            ps,pl = match(clean,profile['player'])
            state,hits = classify(bs>=.90,ps>=.70,hits,3)
            if state == 'PLAYER_VISIBLE':
                draw(view,pl,profile['player'],(255,255,0))
        elapsed = time.monotonic()-started
        label = f'{state} | boxes={len(result.boxes)} | {elapsed:.2f}s'
        cv2.rectangle(view,(0,0),(view.shape[1],30),(0,0,0),-1)
        cv2.putText(view,label,(8,20),0,.43,(255,255,255),1)
        cv2.imshow(name,view)
        if a.image:
            cv2.waitKey(0)
            break
        if cv2.waitKey(30)&255 in (27,ord('q')) or cv2.getWindowProperty(name,cv2.WND_PROP_VISIBLE)<1:
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
