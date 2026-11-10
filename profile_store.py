"""Local PC calibration storage. No ADB access; no pickle loading."""
from pathlib import Path
import os
import tempfile
import numpy as np


def validate(profile):
    shape = np.asarray(profile['shape'])
    box = np.asarray(profile['box'])
    if shape.shape != (2,) or not np.issubdtype(shape.dtype,np.integer) or np.any(shape < 32):
        raise ValueError('Invalid screen shape')
    if box.shape != (4,) or not np.issubdtype(box.dtype,np.integer):
        raise ValueError('Invalid button box')
    x,y,w,h = map(int,box)
    scale = min(1.,960/int(shape[0]))
    ph,pw = int(round(shape[0]*scale)),int(round(shape[1]*scale))
    if min(x,y)<0 or min(w,h)<8 or x+w>pw or y+h>ph:
        raise ValueError('Button box outside preview')
    for name in ('player','button'):
        image = profile[name]
        if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
            raise ValueError('Invalid template: '+name)
        if min(image.shape[:2])<8 or image.shape[0]>ph or image.shape[1]>pw:
            raise ValueError('Invalid template size: '+name)
    if profile['button'].shape[:2] != (h,w):
        raise ValueError('Button dimensions do not match box')
    return profile


def save_profile(path,profile):
    validate(profile)
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True,exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.npz',delete=False) as f:
            name = f.name
            np.savez_compressed(f,version=np.array([1]),**profile)
        os.replace(name,path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def load_profile(path):
    with np.load(Path(path).expanduser(),allow_pickle=False) as data:
        if data['version'].shape != (1,) or data['version'][0] != 1:
            raise ValueError('Unsupported profile version; recalibrate')
        profile = {key:data[key].copy() for key in ('shape','box','player','button')}
    return validate(profile)
