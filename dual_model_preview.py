"""Read-only two-model preview with conservative player-obstacle exclusion."""
import argparse
from pathlib import Path
import time
from dual_model_fusion import predict_both,validate_obstacle_names
from player_obstacle_filter import exclude_player,player_box_in_frame


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--weights',type=Path,required=True,help='Original local model')
    p.add_argument('--obstacle-weights',type=Path,required=True,help='Trained local tree/rock model')
    p.add_argument('--trust-weights',action='store_true',help='Explicitly trust BOTH local model files')
    p.add_argument('--device')
    p.add_argument('--profile',type=Path,default=Path.home()/'.crossy-road-adb-bot'/'profile.npz')
    p.add_argument('--conf',type=float,default=.25,help='Original-model confidence')
    p.add_argument('--obstacle-conf',type=float,default=.10)
    p.add_argument('--obstacle-iou',type=float,default=.5)
    p.add_argument('--player-filter-score',type=float,default=.90,help='Minimum template similarity for player exclusion; not a probability')
    p.add_argument('--no-player-filter',action='store_true',help='Disable display-time player exclusion for comparison')
    p.add_argument('--imgsz',type=int,default=640)
    p.add_argument('--compute',default='cpu')
    p.add_argument('--image',type=Path,help='Local image instead of live ADB')
    a = p.parse_args()
    paths = [a.weights.expanduser().resolve(),a.obstacle_weights.expanduser().resolve()]
    if any(not w.is_file() or w.suffix.lower() not in ('.pt','.onnx') for w in paths):
        p.error('Select TWO existing local detection models; nothing is downloaded')
    if paths[0]==paths[1]: p.error('Select different original and obstacle models')
    if not a.trust_weights: p.error('Explicitly trust both files with --trust-weights')
    if not all(0<v<=1 for v in (a.conf,a.obstacle_conf,a.obstacle_iou,a.player_filter_score)) or a.imgsz<320 or a.imgsz%32:
        p.error('Thresholds must be in (0,1]; imgsz >=320 and divisible by 32')
    import cv2
    from ultralytics import YOLO
    from calibration import capture
    from combined_preview import match,draw,classify
    from persistent_preview import small
    from profile_store import load_profile
    primary,obstacles = [YOLO(str(w),task='detect') for w in paths]
    validate_obstacle_names(obstacles.names)
    profile_path = a.profile.expanduser()
    profile = load_profile(profile_path) if profile_path.exists() else None
    print('Original classes:',primary.names)
    print('Obstacle classes:',obstacles.names,'=> obstacle')
    print('Reusing profile:'+str(profile_path) if profile is not None else 'No profile: detection only, state UNKNOWN. No calibration dialogs.')
    print('Player filter:', 'OFF' if a.no_player_filter or profile is None else f'template similarity >= {a.player_filter_score:.2f}; geometric heuristic, not verified identity')
    print('READ ONLY: one capture per cycle, two sequential predictions; no taps, swipes, restarts or image saves. Q/Esc exits.')
    hits = 0
    window = 'Two-model read-only preview'
    try:
        while True:
            started = time.monotonic()
            frame = cv2.imread(str(a.image)) if a.image else capture(a.device)
            if frame is None: raise RuntimeError('Could not load screenshot')
            objects = predict_both(frame,primary,obstacles,a.conf,a.obstacle_conf,a.imgsz,a.compute,a.obstacle_iou)
            clean = small(frame)
            view = clean.copy()
            sx,sy = view.shape[1]/frame.shape[1],view.shape[0]/frame.shape[0]
            state,ps,pl,player_box = 'UNKNOWN',-1.,None,None
            if profile is not None:
                if tuple(frame.shape[:2])!=tuple(profile['shape']):
                    raise RuntimeError('Screen dimensions differ from saved profile; use a matching --profile')
                x,y,w,h = map(int,profile['box'])
                margin = max(8,int(clean.shape[0]*.03))
                left,top = max(0,x-margin),max(0,y-margin)
                right,bottom = min(clean.shape[1],x+w+margin),min(clean.shape[0],y+h+margin)
                bs,_ = match(clean[top:bottom,left:right],profile['button'],(left,top))
                ps,pl = match(clean,profile['player'])
                state,hits = classify(bs>=.90,ps>=.70,hits,3)
                if state=='PLAYER_VISIBLE':
                    player_box = player_box_in_frame(pl,profile['player'].shape,clean.shape,frame.shape)
            removed = 0
            if not a.no_player_filter:
                objects,removed = exclude_player(objects,player_box,ps,state,a.player_filter_score)
            for obj in objects:
                x1,y1,x2,y2 = obj.box
                left,top,right,bottom = int(x1*sx),int(y1*sy),int(x2*sx),int(y2*sy)
                color = (0,165,255) if obj.group=='obstacle' else (0,220,0)
                text = ('OBSTACLE' if obj.group=='obstacle' else obj.name)+f' {obj.confidence:.2f}'
                cv2.rectangle(view,(left,top),(right,bottom),color,2)
                cv2.putText(view,text,(left,max(14,top-4)),0,.42,color,1)
            if state=='PLAYER_VISIBLE':
                draw(view,pl,profile['player'],(255,255,0))
            elapsed = time.monotonic()-started
            count = sum(o.group=='obstacle' for o in objects)
            cv2.rectangle(view,(0,0),(view.shape[1],52),(0,0,0),-1)
            cv2.putText(view,f'{state} | original={len(objects)-count} obstacles={count} | {elapsed:.2f}s',(8,20),0,.43,(255,255,255),1)
            cv2.putText(view,f'player-score={ps:.2f} excluded={removed} filter={"OFF" if a.no_player_filter or profile is None else "ON"}',(8,42),0,.43,(255,255,255),1)
            cv2.imshow(window,view)
            if a.image:
                cv2.waitKey(0)
                break
            if cv2.waitKey(30)&255 in (27,ord('q')) or cv2.getWindowProperty(window,cv2.WND_PROP_VISIBLE)<1: break
    finally:
        cv2.destroyAllWindows()


if __name__=='__main__':
    try: main()
    except KeyboardInterrupt: pass
    except Exception as e:
        print('ERROR:',e)
        raise SystemExit(1)
