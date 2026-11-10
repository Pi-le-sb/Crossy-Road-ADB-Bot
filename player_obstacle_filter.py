"""Conservative display-time player exclusion; no model changes or device access."""
import math


def player_box_in_frame(location,template_shape,display_shape,frame_shape):
    h,w = template_shape[:2]
    dh,dw = display_shape[:2]
    fh,fw = frame_shape[:2]
    x,y = location
    if min(h,w,dh,dw,fh,fw)<=0: raise ValueError('Invalid image dimensions')
    return (x*fw/dw,y*fh/dh,(x+w)*fw/dw,(y+h)*fh/dh)


def exclude_player(objects,player_box,score,state,min_score=.90):
    objects = list(objects)
    if player_box is None or state!='PLAYER_VISIBLE' or not math.isfinite(score) or score<min_score:
        return objects,0
    if len(player_box)!=4 or not all(math.isfinite(v) for v in player_box): return objects,0
    px1,py1,px2,py2 = player_box
    area = (px2-px1)*(py2-py1)
    if px2<=px1 or py2<=py1: return objects,0
    kept = []
    for obj in objects:
        x1,y1,x2,y2 = obj.box
        size = (x2-x1)*(y2-y1)
        intersection = max(0,min(x2,px2)-max(x1,px1))*max(0,min(y2,py2)-max(y1,py1))
        center_inside = px1<=(x1+x2)/2<=px2 and py1<=(y1+y2)/2<=py2
        # Narrow heuristic: do not mask the whole player neighborhood.
        resembles_player = size>0 and .35<=size/area<=1.6 and intersection/size>=.85 and center_inside
        if obj.group=='obstacle' and resembles_player: continue
        kept.append(obj)
    return kept,len(objects)-len(kept)
