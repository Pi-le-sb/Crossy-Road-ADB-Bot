"""Read-only dual-model preview with player selection and a latched rail warning."""
import argparse
from collections import Counter
from pathlib import Path
import time
from dual_model_fusion import validate_obstacle_names
from player_obstacle_filter import exclude_player,player_box_in_frame,select_player,class_inventory
from rail_warning import predict_with_warning,RailWarningLatch,is_warning


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--weights',type=Path,required=True,help='Original local model')
    p.add_argument('--obstacle-weights',type=Path,required=True,help='Trained local tree/rock model')
    p.add_argument('--trust-weights',action='store_true',help='Explicitly trust BOTH local model files')
    p.add_argument('--device')
    p.add_argument('--profile',type=Path,default=Path.home()/'.crossy-road-adb-bot'/'profile.npz')
    p.add_argument('--conf',type=float,default=.25,help='Original-model confidence except warning lights')
    p.add_argument('--obstacle-conf',type=float,default=.10)
    p.add_argument('--obstacle-iou',type=float,default=.5)
    p.add_argument('--warning-conf',type=float,default=.10,help='Separate train_light_on threshold; lower values may cause false stops')
    p.add_argument('--player-filter-score',type=float,default=.70,help='Template similarity threshold, not a probability')
    p.add_argument('--player-model-score',type=float,default=.65,help='Minimum original-model player confidence')
    p.add_argument('--no-player-filter',action='store_true',help='Disable player exclusion for comparison')
    p.add_argument('--imgsz',type=int,default=640)
    p.add_argument('--compute',default='cpu')
    p.add_argument('--image',type=Path,help='Local image instead of live ADB')
    a = p.parse_args()
    paths = [a.weights.expanduser().resolve(),a.obstacle_weights.expanduser().resolve()]
    if any(not w.is_file() or w.suffix.lower() not in ('.pt','.onnx') for w in paths):
        p.error('Select TWO existing local detection models; nothing is downloaded')
    if paths[0]==paths[1]: p.error('Select different original and obstacle models')
    if not a.trust_weights: p.error('Explicitly trust both files with --trust-weights')
    if not all(0<v<=1 for v in (a.conf,a.obstacle_conf,a.obstacle_iou,a.warning_conf,a.player_filter_score,a.player_model_score)) or a.imgsz<320 or a.imgsz%32:
        p.error('Thresholds must be in (0,1]; imgsz >=320 and divisible by 32')
    import cv2
    from ultralytics import YOLO
    from calibration import capture
    from combined_preview import match,classify
    from persistent_preview import small
    from profile_store import load_profile
    primary,obstacles = [YOLO(str(w),task='detect') for w in paths]
    validate_obstacle_names(obstacles.names)
    profile_path = a.profile.expanduser()
    profile = load_profile(profile_path) if profile_path.exists() else None
    print('Original weights:',paths[0])
    print('Original classes:',primary.names)
    print('Obstacle weights:',paths[1])
    print('Obstacle classes:',obstacles.names,'=> obstacle')
    print('Known-alias class inventory (availability only, NOT verified recognition):',class_inventory(primary.names))
    names = primary.names.values() if isinstance(primary.names,dict) else primary.names
    if not any(n.strip().lower()=='train_light_on' for n in names):
        print('WARNING: original model has no train_light_on class; no warning detection is possible.')
    print('Warning-light stop intent only; NO train-body class or automatic crossing clearance.')
    print('A warning stays latched for this process. Missing detections never mean LIGHT_OFF or SAFE.')
    print('The legacy main.py blind tap loop is NOT connected to this preview. Do not run it as a guarded controller.')
    print('Reusing profile:'+str(profile_path) if profile is not None else 'No profile: original-model player detection only; no calibration dialogs.')
    print('Player filter:', 'OFF' if a.no_player_filter else 'ON; template and geometry are heuristics, not verified identity')
    print('READ ONLY: no taps, swipes, automatic restart, screenshot saves or uploads. Q/Esc exits.')
    warning = RailWarningLatch(a.warning_conf)
    hits,last_report = 0,0.
    window = 'Two-model read-only preview'
    try:
        while True:
            started = time.monotonic()
            frame = cv2.imread(str(a.image)) if a.image else capture(a.device)
            if frame is None: raise RuntimeError('Could not load screenshot')
            objects = predict_with_warning(frame,primary,obstacles,a.conf,a.obstacle_conf,a.imgsz,a.compute,a.obstacle_iou,a.warning_conf)
            rail = warning.update(objects)
            clean = small(frame)
            view = clean.copy()
            sx,sy = view.shape[1]/frame.shape[1],view.shape[0]/frame.shape[0]
            state,ps,template_box,button_hit = 'UNKNOWN',-1.,None,False
            if profile is not None:
                if tuple(frame.shape[:2])!=tuple(profile['shape']):
                    raise RuntimeError('Screen dimensions differ from saved profile; use a matching --profile')
                x,y,w,h = map(int,profile['box'])
                margin = max(8,int(clean.shape[0]*.03))
                left,top = max(0,x-margin),max(0,y-margin)
                right,bottom = min(clean.shape[1],x+w+margin),min(clean.shape[0],y+h+margin)
                bs,_ = match(clean[top:bottom,left:right],profile['button'],(left,top))
                ps,pl = match(clean,profile['player'])
                button_hit = bs>=.90
                state,hits = classify(button_hit,ps>=a.player_filter_score,hits,3)
                template_box = player_box_in_frame(pl,profile['player'].shape,clean.shape,frame.shape)
            player_box,player_score,source = select_player(objects,template_box,ps,button_hit,a.player_filter_score,a.player_model_score)
            if player_box is not None: state = 'PLAYER_VISIBLE'
            removed = 0
            before = dict(Counter(o.name for o in objects if o.source=='primary'))
            if not a.no_player_filter:
                minimum = a.player_model_score if source=='PRIMARY_PLAYER' else a.player_filter_score
                objects,removed = exclude_player(objects,player_box,player_score,state,minimum)
            reason = 'DISABLED' if a.no_player_filter else source if player_box is None else 'PLAYER_BOX_REMOVED' if removed else 'NO_MATCHING_OBSTACLE_BOX'
            for obj in objects:
                x1,y1,x2,y2 = obj.box
                left,top,right,bottom = int(x1*sx),int(y1*sy),int(x2*sx),int(y2*sy)
                color = (0,0,255) if is_warning(obj) else (0,165,255) if obj.group=='obstacle' else (0,220,0)
                text = ('OBSTACLE' if obj.group=='obstacle' else obj.name)+f' {obj.confidence:.2f}'
                cv2.rectangle(view,(left,top),(right,bottom),color,2)
                cv2.putText(view,text,(left,max(14,top-4)),0,.42,color,1)
            if player_box is not None:
                x1,y1,x2,y2 = player_box
                pt = (int(x1*sx),int(y1*sy))
                cv2.rectangle(view,pt,(int(x2*sx),int(y2*sy)),(255,255,0),2)
                cv2.putText(view,'PLAYER',(pt[0],max(14,pt[1]-4)),0,.42,(255,255,0),1)
            elapsed = time.monotonic()-started
            count = sum(o.group=='obstacle' for o in objects)
            cv2.rectangle(view,(0,0),(view.shape[1],94),(0,0,0),-1)
            rows = (f'{state} | original={len(objects)-count} obstacles={count} | {elapsed:.2f}s',
                    f'player={source} score={player_score:.2f} template={ps:.2f}',
                    f'excluded={removed} reason={reason}',f'RAIL: {rail.state} | crossing_clear=False | READ ONLY')
            for i,text in enumerate(rows):
                color = (0,0,255) if i==3 and rail.stop_requested else (255,255,255)
                cv2.putText(view,text,(8,20+i*21),0,.40,color,1)
            if started-last_report>=2 or a.image:
                print('Preview:',dict(state=state,player_source=source,player_score=round(player_score,3),template_score=round(ps,3),excluded=removed,reason=reason,primary_seen=before,rail_state=rail.state,stop_requested=rail.stop_requested,crossing_clear=rail.crossing_clear),flush=True)
                last_report = started
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
