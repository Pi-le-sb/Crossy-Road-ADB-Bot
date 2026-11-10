"""Read-only motion candidates, not semantic obstacle detection or safe navigation."""
import argparse
import time
import cv2
import numpy as np
from calibration import capture


def camera_shift(displacements):
    d = np.asarray(displacements, dtype=float).reshape(-1, 2)
    d = d[np.isfinite(d).all(axis=1)]
    if len(d) < 8:
        return None
    center = np.median(d, axis=0)
    good = np.linalg.norm(d-center, axis=1) <= 2.0
    if good.sum() < 8 or good.mean() < .75:
        return None
    return np.median(d[good], axis=0)


def relative_velocity(old, new, camera, dt):
    if not np.isfinite(dt) or not .02 <= dt <= 1.5:
        raise ValueError('Frame interval outside .02..1.5 seconds')
    return (np.asarray(new)-np.asarray(old)-camera) / dt


def track(previous, current, mask, count):
    points = cv2.goodFeaturesToTrack(previous, maxCorners=count, qualityLevel=.01,
                                    minDistance=5, mask=mask, blockSize=7)
    empty = np.empty((0,2), np.float32)
    if points is None:
        return empty, empty
    params = dict(winSize=(31,31), maxLevel=3,
                  criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,30,.01))
    nxt, status, _ = cv2.calcOpticalFlowPyrLK(previous,current,points,None,**params)
    if nxt is None or status is None:
        return empty, empty
    back, backward_status, _ = cv2.calcOpticalFlowPyrLK(current,previous,nxt,None,**params)
    if back is None or backward_status is None:
        return empty, empty
    old, new = points.reshape(-1,2), nxt.reshape(-1,2)
    valid = (status.ravel()==1) & (backward_status.ravel()==1)
    valid &= np.isfinite(new).all(axis=1) & np.isfinite(back.reshape(-1,2)).all(axis=1)
    valid &= np.linalg.norm(back.reshape(-1,2)-old,axis=1) < 1.0
    valid &= (new[:,0]>=0) & (new[:,0]<current.shape[1]) & (new[:,1]>=0) & (new[:,1]<current.shape[0])
    return old[valid],new[valid]


def reference(image):
    print('Select STATIC scenery with edges: tree/rock, not duck, vehicle, water or UI. Enter confirms.')
    x,y,w,h = map(int,cv2.selectROI('Select static camera reference',image,False,False))
    cv2.destroyWindow('Select static camera reference')
    if min(w,h)<10:
        raise RuntimeError('Reference cancelled or too small')
    mask = np.zeros(image.shape[:2],np.uint8)
    mask[y:y+h,x:x+w] = 255
    return mask


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--device')
    p.add_argument('--speed',type=float,default=12.,help='Minimum residual speed in preview pixels/second')
    a = p.parse_args()
    if not np.isfinite(a.speed) or a.speed<=0:
        p.error('speed must be finite and positive')
    original = capture(a.device)
    shape = original.shape
    scale = min(1.,960 / shape[0])
    def resized(frame):
        if frame.shape != shape:
            raise RuntimeError('Resolution changed; restart preview')
        return cv2.resize(frame,None,fx=scale,fy=scale)
    image = resized(original)
    mask = reference(image)
    previous = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    # ROI interaction may take seconds; establish a fresh baseline first.
    last_time = None
    known = True
    name = 'Read-only motion candidates; R reselects scenery; Q exits'
    print('Orange arrows = residual motion, NOT identified cars or safe tiles. No taps, no saved files.')
    while True:
        before = time.monotonic()
        image = resized(capture(a.device))
        stamp = (before+time.monotonic())/2
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        view = image.copy()
        label = 'BASELINE: press R if camera moved during selection'
        if last_time is not None and known:
            dt = stamp-last_time
            if not .02 <= dt <= 1.5:
                known = False
                label = 'UNKNOWN: frame gap; R to recalibrate'
            else:
                ref_old,ref_new = track(previous,gray,mask,100)
                camera = camera_shift(ref_new-ref_old)
                if camera is None:
                    known = False
                    label = 'UNKNOWN: camera reference lost; press R'
                else:
                    field = np.full(gray.shape,255,np.uint8)
                    field[:int(gray.shape[0]*.15)] = 0
                    field[int(gray.shape[0]*.92):] = 0
                    old,new = track(previous,gray,field,500)
                    velocity = relative_velocity(old,new,camera,dt)
                    residual = new-old-camera
                    moving = (np.linalg.norm(velocity,axis=1)>=a.speed) & (np.linalg.norm(residual,axis=1)>=2.5)
                    for point,vector in zip(new[moving],velocity[moving]):
                        start = tuple(point.astype(int))
                        end = tuple((point+vector*.25).astype(int))
                        cv2.arrowedLine(view,start,end,(0,180,255),1,tipLength=.25)
                    transform = np.float32([[1,0,camera[0]],[0,1,camera[1]]])
                    mask = cv2.warpAffine(mask,transform,(gray.shape[1],gray.shape[0]),flags=cv2.INTER_NEAREST)
                    label = f'CANDIDATES {moving.sum()} | dt={dt:.2f}s'
                    cv2.putText(view,f'camera delta={camera[0]:.1f},{camera[1]:.1f} preview px',(8,43),0,.42,(255,255,255),1)
        elif not known:
            label = 'UNKNOWN: press R to select a new static reference'
        outlines,_ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(view,outlines,-1,(255,255,0),1)
        cv2.putText(view,label,(8,21),0,.43,(0,0,255),1)
        cv2.imshow(name,view)
        key = cv2.waitKey(30) & 255
        if key in (27,ord('q')) or cv2.getWindowProperty(name,cv2.WND_PROP_VISIBLE)<1:
            break
        if key == ord('r'):
            fresh = resized(capture(a.device))
            mask = reference(fresh)
            previous = cv2.cvtColor(fresh,cv2.COLOR_BGR2GRAY)
            last_time = None
            known = True
            continue
        previous,last_time = gray,stamp


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
