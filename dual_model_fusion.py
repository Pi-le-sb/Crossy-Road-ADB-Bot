"""Two-model detection fusion; no ADB, files, GUI or neural-network dependency."""
from dataclasses import dataclass
import math

OBSTACLE_NAMES = {'tree','trees','rock','rocks','stone','stones'}

@dataclass(frozen=True)
class Detection:
    box: tuple
    confidence: float
    source: str
    class_id: int
    name: str
    group: str


def class_name(names, cid):
    try:
        name = names[cid]
    except (KeyError,IndexError,TypeError):
        raise ValueError('Unknown model-local class ID: '+str(cid)) from None
    if not isinstance(name,str) or not name.strip():
        raise ValueError('Invalid model class name')
    return name.strip()


def is_obstacle(name):
    return name.strip().lower() in OBSTACLE_NAMES


def validate_obstacle_names(names):
    values = list(names.values()) if isinstance(names,dict) else list(names)
    if not values or any(not isinstance(n,str) or not is_obstacle(n) for n in values):
        raise ValueError('Obstacle model must contain only tree/rock/stone classes; select the trained obstacle checkpoint')


def extract(result, source, shape):
    if result.boxes is None:
        raise ValueError('Detection model required: no boxes returned')
    boxes, scores, classes = result.boxes.xyxy.tolist(),result.boxes.conf.tolist(),result.boxes.cls.tolist()
    if not len(boxes)==len(scores)==len(classes):
        raise ValueError('Inconsistent detection arrays')
    height,width = shape[:2]
    output = []
    for box,score,cid in zip(boxes,scores,classes):
        if len(box)!=4 or not all(math.isfinite(float(v)) for v in (*box,score,cid)):
            raise ValueError('Non-finite or malformed detection')
        if float(cid)!=int(cid) or int(cid)<0 or not 0<=float(score)<=1:
            raise ValueError('Invalid class/confidence')
        cid = int(cid); name = class_name(result.names,cid)
        x1,y1,x2,y2 = map(float,box)
        x1,y1,x2,y2 = max(0,min(width,x1)),max(0,min(height,y1)),max(0,min(width,x2)),max(0,min(height,y2))
        if x1>=x2 or y1>=y2: continue
        output.append(Detection((x1,y1,x2,y2),float(score),source,cid,name,'obstacle' if is_obstacle(name) else 'primary'))
    return output


def iou(a,b):
    intersection = max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union = (a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection
    return intersection/union if union>0 else 0.


def merge(primary, obstacles, threshold=.5):
    if not 0<threshold<=1: raise ValueError('IoU threshold must be in (0,1]')
    # Keep original non-obstacle classes; the specialist owns static obstacles.
    output = [d for d in primary if d.group!='obstacle']
    kept = []
    for candidate in sorted((d for d in obstacles if d.group=='obstacle'),key=lambda d:d.confidence,reverse=True):
        if all(iou(candidate.box,other.box)<threshold for other in kept): kept.append(candidate)
    return output+kept


def predict_both(frame, primary, obstacles, primary_conf=.25, obstacle_conf=.10, imgsz=640, compute='cpu', obstacle_iou=.5):
    kwargs = dict(source=frame,imgsz=imgsz,device=compute,verbose=False,save=False,save_txt=False,save_crop=False)
    first = primary.predict(conf=primary_conf,**kwargs)[0]
    second = obstacles.predict(conf=obstacle_conf,**kwargs)[0]
    validate_obstacle_names(second.names)
    return merge(extract(first,'primary',frame.shape),extract(second,'obstacles',frame.shape),obstacle_iou)
