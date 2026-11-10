"""Persistent read-only player/game-over preview with tentative motion group IDs."""
import argparse
from pathlib import Path
import time
import cv2
import numpy as np
from calibration import capture
from combined_preview import select,match,draw,classify
from motion_preview import track,camera_shift,relative_velocity
from profile_store import save_profile,load_profile
from candidate_tracking import MotionTracker


def small(image):
    scale = min(1.,960/image.shape[0])
    return cv2.resize(image,None,fx=scale,fy=scale)


def calibrate(device,path):
    if path.exists():
        if input('Overwrite existing local profile? Type YES: ').strip() != 'YES':
            raise RuntimeError('Existing profile kept')
    input('Show result screen on phone, then Enter here: ')
    original = capture(device)
    image = small(original)
    box,button = select(image,'Select full restart button including triangle; Enter')
    input('Manually start round on phone, then Enter here: ')
    living = capture(device)
    if living.shape != original.shape:
        raise RuntimeError('Resolution changed during calibration')
    _,player = select(small(living),'Select duck tightly without shadow; Enter')
    profile = dict(shape=np.array(original.shape[:2]),box=np.array(box),player=player,button=button)
    save_profile(path,profile)
    print('Saved ONLY on PC:',path)
    return profile


def motion(previous,current,dt,player_box):
    if not .02 <= dt <= 1.5:
        return None
    hsv = cv2.cvtColor(previous,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv,np.array([30,50,35]),np.array([90,255,255]))
    mask[:int(mask.shape[0]*.15)] = 0
    mask[int(mask.shape[0]*.92):] = 0
    if player_box is not None:
        x,y,w,h = player_box
        mask[max(0,y-12):y+h+12,max(0,x-12):x+w+12] = 0
    gray0 = cv2.cvtColor(previous,cv2.COLOR_BGR2GRAY)
    gray1 = cv2.cvtColor(current,cv2.COLOR_BGR2GRAY)
    old,new = track(gray0,gray1,mask,200)
    if len(old)<8 or np.any(np.ptp(old,axis=0)<40):
        return None
    camera = camera_shift(new-old)
    if camera is None:
        return None
    field = np.full(gray0.shape,255,np.uint8)
    field[:int(field.shape[0]*.15)] = 0
    field[int(field.shape[0]*.92):] = 0
    old,new = track(gray0,gray1,field,500)
    velocity = relative_velocity(old,new,camera,dt)
    moving = (np.linalg.norm(velocity,axis=1)>=12) & (np.linalg.norm(new-old-camera,axis=1)>=2.5)
    return new[moving],velocity[moving],camera


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device')
    parser.add_argument('--calibrate',action='store_true')
    parser.add_argument('--profile',type=Path,default=Path.home()/'.crossy-road-adb-bot'/'profile.npz')
    args = parser.parse_args()
    path = args.profile.expanduser()
    if args.calibrate:
        profile = calibrate(args.device,path)
    elif path.exists():
        profile = load_profile(path)
        print('Loaded local profile:',path)
    else:
        raise RuntimeError('No profile. Run python persistent_preview.py --calibrate once.')
    player,button = profile['player'],profile['button']
    x,y,w,h = map(int,profile['box'])
    previous = None
    previous_box = None
    last_time = None
    hits = 0
    last_state = None
    tracker = MotionTracker()
    name = 'Persistent read-only preview; Q exits'
    print('Read-only motion groups, NOT vehicles or collision bounds. Saved calibration is reused.')
    while True:
        started = time.monotonic()
        original = capture(args.device)
        stamp = (started+time.monotonic())/2
        if tuple(original.shape[:2]) != tuple(profile['shape']):
            raise RuntimeError('Resolution/orientation changed; use a matching profile or --calibrate')
        image = small(original)
        margin = max(8,int(image.shape[0]*.03))
        left,top = max(0,x-margin),max(0,y-margin)
        right,bottom = min(image.shape[1],x+w+margin),min(image.shape[0],y+h+margin)
        bs,bl = match(image[top:bottom,left:right],button,(left,top))
        ps,pl = match(image,player)
        state,hits = classify(bs>=.90,ps>=.70,hits,3)
        view = image.copy()
        movement = 'MOTION_UNKNOWN (automatic retry)'
        if state == 'PLAYER_VISIBLE':
            draw(view,pl,player,(255,255,0))
            if previous is not None:
                dt = stamp-last_time
                candidates = motion(previous,image,dt,previous_box)
                if candidates is not None:
                    points,vectors,camera = candidates
                    groups = tracker.update(points,vectors,camera,dt)
                    movement = f'GROUPS {len(groups)} | features {len(points)}'
                    for item in groups:
                        g = item.group
                        color = (0,180,255) if item.hits>=2 else (160,160,160)
                        bx,by,ex,ey = g.bounds
                        cv2.rectangle(view,(bx,by),(ex,ey),color,2)
                        label = f'G{item.id} {"TRACK" if item.hits>=2 else "NEW"} {g.velocity[0]:+.0f},{g.velocity[1]:+.0f}px/s'
                        cv2.putText(view,label,(max(0,bx),max(80,by-4)),0,.32,color,1)
                        cv2.arrowedLine(view,tuple(g.center.astype(int)),tuple((g.center+g.velocity*.25).astype(int)),color,2,tipLength=.25)
                else:
                    tracker.reset()
            previous = image
            previous_box = (*pl,player.shape[1],player.shape[0])
            last_time = stamp
        else:
            tracker.reset()
            previous = None
            previous_box = None
            last_time = None
            if bs>=.90:
                draw(view,bl,button,(0,0,255))
        cv2.rectangle(view,(0,0),(view.shape[1],72),(0,0,0),-1)
        for i,text in enumerate((state,f'player={ps:.2f} button={bs:.2f}',movement)):
            cv2.putText(view,text,(8,20+i*21),0,.42,(255,255,255),1)
        if state != last_state:
            print(state)
            last_state = state
        cv2.imshow(name,view)
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
