"""Feature-motion groups and tentative IDs, NOT vehicle or collision detection."""
from dataclasses import dataclass, replace
import numpy as np


@dataclass(frozen=True)
class Group:
    center: np.ndarray
    velocity: np.ndarray
    bounds: tuple
    count: int


@dataclass(frozen=True)
class Track:
    id: int
    group: Group
    hits: int = 1
    missed: int = 0


def group_points(points, velocities, radius=24., speed_tolerance=40., min_points=3):
    points = np.asarray(points,dtype=float).reshape(-1,2)
    velocities = np.asarray(velocities,dtype=float).reshape(-1,2)
    if points.shape != velocities.shape:
        raise ValueError('Point/velocity count mismatch')
    valid = np.isfinite(points).all(axis=1) & np.isfinite(velocities).all(axis=1)
    points,velocities = points[valid],velocities[valid]
    if len(points)>500:
        raise ValueError('At most 500 feature points supported')
    remaining = set(range(len(points)))
    groups = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        members,queue = [seed],[seed]
        while queue:
            index = queue.pop()
            nearby = np.linalg.norm(points-points[index],axis=1)<=radius
            similar = np.linalg.norm(velocities-velocities[index],axis=1)<=speed_tolerance
            found = sorted(remaining.intersection(np.flatnonzero(nearby & similar)))
            remaining.difference_update(found)
            members.extend(found)
            queue.extend(found)
        if len(members)<min_points:
            continue
        p,v = points[members],velocities[members]
        lo,hi = np.floor(p.min(axis=0)-4).astype(int),np.ceil(p.max(axis=0)+4).astype(int)
        groups.append(Group(np.median(p,axis=0),np.median(v,axis=0),
                            (int(lo[0]),int(lo[1]),int(hi[0]),int(hi[1])),len(members)))
    return groups


class MotionTracker:
    def __init__(self):
        self.tracks = []
        self.next_id = 1

    def reset(self):
        self.tracks.clear()

    def update(self,points,velocities,camera,dt):
        camera = np.asarray(camera,dtype=float)
        if camera.shape != (2,) or not np.isfinite(camera).all() or not np.isfinite(dt) or not .02<=dt<=1.5:
            self.reset()
            raise ValueError('Invalid camera shift or time interval')
        groups = group_points(points,velocities)
        predictions = [t.group.center+camera+t.group.velocity*dt for t in self.tracks]
        pairs = []
        for i,t in enumerate(self.tracks):
            for j,g in enumerate(groups):
                distance = np.linalg.norm(g.center-predictions[i])
                speed_change = np.linalg.norm(g.velocity-t.group.velocity)
                if distance<=35 and speed_change<=60:
                    pairs.append((distance+.15*speed_change,i,j))
        used_tracks,used_groups = set(),set()
        updated,visible = [],[]
        for _,i,j in sorted(pairs):
            if i in used_tracks or j in used_groups:
                continue
            t = self.tracks[i]
            item = Track(t.id,groups[j],t.hits+1 if t.missed==0 else 1,0)
            used_tracks.add(i); used_groups.add(j)
            updated.append(item); visible.append(item)
        for j,g in enumerate(groups):
            if j not in used_groups:
                item = Track(self.next_id,g)
                self.next_id += 1
                updated.append(item); visible.append(item)
        for i,t in enumerate(self.tracks):
            if i not in used_tracks and t.missed<2:
                g = replace(t.group,center=predictions[i])
                updated.append(Track(t.id,g,t.hits,t.missed+1))
        self.tracks = updated
        return sorted(visible,key=lambda item:item.id)
