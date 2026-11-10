"""Prepare a new tree-only train/validation dataset from a train-only YOLO export."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import tempfile
import yaml
from PIL import Image


def split_export(source,out,fraction=.2,seed=42):
    source,out = Path(source).resolve(),Path(out).resolve()
    if not .05<=fraction<=.5:
        raise ValueError('validation fraction must be .05..0.5')
    if out.exists() or out==source or source in out.parents:
        raise ValueError('Output must be new and outside source; nothing is overwritten')
    if any((source/name/'images').is_dir() for name in ('valid','val','test')):
        raise ValueError('This helper accepts train-only exports; use obstacle_training.py prepare for existing splits')
    config = yaml.safe_load((source/'data.yaml').read_text(encoding='utf-8-sig'))
    raw = config['names']
    names = dict(enumerate(raw)) if isinstance(raw,list) else {int(k):v for k,v in raw.items()}
    trees = [i for i,n in names.items() if str(n).strip().lower() in ('tree','trees')]
    if len(trees)!=1:
        raise ValueError('Exactly one Tree class required; found '+repr(names))
    tree_id = trees[0]
    images,labels = source/'train'/'images',source/'train'/'labels'
    files = sorted(p for p in images.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png'))
    if not files: raise ValueError('No train images found')
    groups,seen,dropped = {},{},[]
    for image in files:
        with Image.open(image) as check: check.verify()
        label = labels/(image.stem+'.txt')
        if not label.is_file(): raise ValueError('Missing label: '+str(label))
        rows = []
        for line in label.read_text(encoding='utf-8-sig').splitlines():
            if not line.strip(): continue
            fields = line.split()
            if len(fields)!=5: raise ValueError('Expected five label fields: '+str(label))
            cid = int(fields[0]); x,y,w,h = map(float,fields[1:])
            if cid not in names or not all(math.isfinite(v) for v in (x,y,w,h)):
                raise ValueError('Invalid class/coordinate: '+str(label))
            if not (0<w<=1 and 0<h<=1 and x-w/2>=-1e-6 and y-h/2>=-1e-6 and x+w/2<=1+1e-6 and y+h/2<=1+1e-6):
                raise ValueError('Invalid normalized box: '+str(label))
            if cid==tree_id: rows.append((x,y,w,h))
        rows = sorted(rows)
        digest = hashlib.sha256(image.read_bytes()).hexdigest()
        if digest in seen:
            if seen[digest]!=rows: raise ValueError('Same image has conflicting Tree annotations')
            dropped.append(image.name)
            continue
        seen[digest] = rows
        key = image.stem.split('.rf.')[0]
        groups.setdefault(key,[]).append((image,rows))
    keys = sorted(groups)
    rng = random.Random(seed); rng.shuffle(keys)
    positives = [k for k in keys if any(rows for _,rows in groups[k])]
    if len(positives)<2:
        raise ValueError('Need at least two distinct filename groups containing trees; cannot create meaningful train/val split')
    desired = max(1,min(len(keys)-1,int(len(keys)*fraction+.5)))
    val_keys = {positives[0]}
    reserved_train = positives[1]
    for key in keys:
        if len(val_keys)>=desired: break
        if key!=reserved_train: val_keys.add(key)
    counts = {s:dict(images=0,trees=0) for s in ('train','val')}
    manifest = dict(status='TREE_DATASET_ONLY_NOT_TRAINED',source=str(source),original_tree_id=tree_id,
                    validation_fraction=fraction,seed=seed,dropped_exact_duplicates=dropped,assignments={})
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temporary:
        staging = Path(temporary)/'dataset'; staging.mkdir()
        number = 0
        for key in keys:
            split = 'val' if key in val_keys else 'train'
            manifest['assignments'][key] = split
            for image,rows in groups[key]:
                dest_images,dest_labels = staging/split/'images',staging/split/'labels'
                dest_images.mkdir(parents=True,exist_ok=True); dest_labels.mkdir(parents=True,exist_ok=True)
                stem = f'{number:06d}'; number += 1
                shutil.copy2(image,dest_images/(stem+image.suffix.lower()))
                text = ''.join('0 '+' '.join(f'{v:.8g}' for v in row)+'\n' for row in rows)
                (dest_labels/(stem+'.txt')).write_text(text,encoding='utf-8')
                counts[split]['images'] += 1; counts[split]['trees'] += len(rows)
        data = dict(path=str(out),train='train/images',val='val/images',nc=1,names=['tree'])
        (staging/'data.yaml').write_text(yaml.safe_dump(data,sort_keys=False),encoding='utf-8')
        manifest['counts'] = counts
        (staging/'split_report.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        for name in ('README.dataset.txt','README.roboflow.txt','SOURCE.txt'):
            if (source/name).is_file(): shutil.copy2(source/name,staging/name)
        staging.rename(out)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('training-data/raw'))
    p.add_argument('--out',type=Path,default=Path('training-data/tree-prepared'))
    p.add_argument('--val-fraction',type=float,default=.2)
    p.add_argument('--seed',type=int,default=42)
    a = p.parse_args()
    print(json.dumps(split_export(a.source,a.out,a.val_fraction,a.seed),indent=2))


if __name__=='__main__':
    main()
