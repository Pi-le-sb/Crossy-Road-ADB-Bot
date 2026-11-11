"""Player selection and geometric exclusion; no model/device/file access."""
import math

PLAYER_NAMES = {'player','chicken','duck','character'}


def valid_box(box):
    return box is not None and len(box)==4 and all(math.isfinite(v) for v in box) and box[2]>box[0] and box[3]>box[1]


def player_box_in_frame(location,template_shape,display_shape,frame_shape):
    h,w = template_shape[:2]
    dh,dw = display_shape[:2]
    fh,fw = frame_shape[:2]
    x,y = location
    if min(h,w,dh,dw,fh,fw)<=0: raise ValueError('Invalid image dimensions')
    return (x*fw/dw,y*fh/dh,(x+w)*fw/dw,(y+h)*fh/dh)


def select_player(objects,template_box,template_score,blocked=False,template_threshold=.70,model_threshold=.65):
    if blocked: return None,-1.,'BUTTON_VISIBLE'
    candidates = [o for o in objects if o.source=='primary' and o.name.strip().lower() in PLAYER_NAMES
                  and math.isfinite(o.confidence) and o.confidence>=model_threshold and valid_box(o.box)]
    if len(candidates)==1:
        player = candidates[0]
        if valid_box(template_box) and math.isfinite(template_score) and template_score>=template_threshold:
            a,b = player.box,template_box
            overlap = max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
            if overlap==0: return None,-1.,'PLAYER_SOURCES_DISAGREE'
        return player.box,player.confidence,'PRIMARY_PLAYER'
    if valid_box(template_box) and math.isfinite(template_score) and template_score>=template_threshold:
        return template_box,template_score,'TEMPLATE_PLAYER'
    return None,-1.,'AMBIGUOUS_PRIMARY' if len(candidates)>1 else 'NO_PLAYER_LOCATION'


def exclude_player(objects,player_box,score,state,min_score=.70):
    objects = list(objects)
    if not valid_box(player_box) or state!='PLAYER_VISIBLE' or not math.isfinite(score) or score<min_score:
        return objects,0
    px1,py1,px2,py2 = player_box
    area = (px2-px1)*(py2-py1)
    kept = []
    for obj in objects:
        if obj.group!='obstacle' or not valid_box(obj.box):
            kept.append(obj); continue
        x1,y1,x2,y2 = obj.box
        size = (x2-x1)*(y2-y1)
        intersection = max(0,min(x2,px2)-max(x1,px1))*max(0,min(y2,py2)-max(y1,py1))
        overlap = intersection/(area+size-intersection)
        centered = px1<=(x1+x2)/2<=px2 and py1<=(y1+y2)/2<=py2
        if .35<=size/area<=2.2 and overlap>=.45 and centered: continue
        kept.append(obj)
    return kept,len(objects)-len(kept)


def class_inventory(names):
    values = list(names.values()) if isinstance(names,dict) else list(names)
    normalize = lambda n: ''.join(c for c in n.lower() if c.isalnum())
    present = {normalize(n) for n in values}
    aliases = {'player':PLAYER_NAMES,'train':{'train','trains'},'log':{'log','logs','woodenlog'},
               'turtle':{'turtle','turtles'},'coin':{'coin','coins'},'road':{'road','roads'},
               'water':{'water','river'},'rail':{'rail','rails','railway','railroad'}}
    return {kind:bool(present & {normalize(n) for n in choices}) for kind,choices in aliases.items()}
