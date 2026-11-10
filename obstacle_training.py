"""Explicit local dataset download, audit, remapping and training. No phone access."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import time
import uuid
import yaml
from PIL import Image

SOURCE = 'https://universe.roboflow.com/crossyroad-q9hpe/crossyroad-e1abn'
HOME = Path.home()/'.crossy-road-adb-bot'/'training'
ALIASES = {'tree':'tree','trees':'tree','rock':'rock','rocks':'rock','stone':'rock','stones':'rock'}


def names_from(config):
    names = config['names']
    names = dict(enumerate(names)) if isinstance(names,list) else {int(k):v for k,v in names.items()}
    if set(names) != set(range(len(names))) or not all(isinstance(v,str) for v in names.values()):
        raise ValueError('Class IDs must be contiguous zero-based names')
    return names


def audit(root,targets=('tree','rock')):
    root = Path(root).resolve()
    config = yaml.safe_load((root/'data.yaml').read_text(encoding='utf-8-sig'))
    names = names_from(config)
    mapping = {i:targets.index(ALIASES[n.strip().lower()]) for i,n in names.items()
               if ALIASES.get(n.strip().lower()) in targets}
    if set(mapping.values()) != set(range(len(targets))):
        raise ValueError('Missing requested classes. Found: '+repr(names)+'. Tree-only experiment: --tree-only; rocks are NOT learned then.')
    items,counts,seen = [],{},{}
    for split,aliases in [('train',('train',)),('val',('valid','val')),('test',('test',))]:
        choices = []
        for alias in aliases:
            choices.extend([(root/alias/'images',root/alias/'labels'),(root/'images'/alias,root/'labels'/alias)])
        choices = [(i,l) for i,l in choices if i.is_dir()]
        if len(choices)>1:
            raise ValueError('Ambiguous split layout: '+split)
        if not choices:
            if split=='test': continue
            raise ValueError('Missing split: '+split)
        image_dir,label_dir = choices[0]
        counts[split] = [0]*len(targets)
        files = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png'))
        if not files: raise ValueError('Empty split: '+split)
        for number,image in enumerate(files):
            with Image.open(image) as check: check.verify()
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in seen: raise ValueError('Duplicate image content across/within splits: '+str(image))
            seen[digest] = split
            label = label_dir/(image.stem+'.txt')
            if not label.is_file():
                raise ValueError('Missing annotation; create explicit empty .txt only for reviewed negatives: '+str(label))
            output_rows = []
            for line in label.read_text(encoding='utf-8-sig').splitlines():
                if not line.strip(): continue
                fields = line.split()
                if len(fields)!=5: raise ValueError('Expected detection label with 5 fields: '+str(label))
                cid = int(fields[0]); x,y,w,h = map(float,fields[1:])
                if cid not in names or not all(math.isfinite(v) for v in (x,y,w,h)):
                    raise ValueError('Invalid class/coordinate: '+str(label))
                if not (0<w<=1 and 0<h<=1 and x-w/2>=-1e-6 and y-h/2>=-1e-6 and x+w/2<=1+1e-6 and y+h/2<=1+1e-6):
                    raise ValueError('Box outside normalized image: '+str(label))
                if cid in mapping:
                    target = mapping[cid]
                    output_rows.append(str(target)+' '+' '.join(fields[1:]))
                    counts[split][target] += 1
            items.append((split,f'{number:06d}'+image.suffix.lower(),image,output_rows))
    for split in ('train','val'):
        if any(n==0 for n in counts[split]):
            raise ValueError('Each requested class needs labeled examples in train AND val: '+repr(counts))
    return items,counts


def prepare(root,out,tree_only=False):
    root,out = Path(root).resolve(),Path(out).resolve()
    if out.exists() or out==root or root in out.parents:
        raise ValueError('Output must be new and outside source directory; source is never overwritten')
    targets = ('tree',) if tree_only else ('tree','rock')
    items,counts = audit(root,targets)
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temporary:
        staging = Path(temporary)/'prepared'; staging.mkdir()
        for split,name,image,rows in items:
            images,labels = staging/split/'images',staging/split/'labels'
            images.mkdir(parents=True,exist_ok=True); labels.mkdir(parents=True,exist_ok=True)
            shutil.copy2(image,images/name)
            (labels/(Path(name).stem+'.txt')).write_text('\n'.join(rows)+('\n' if rows else ''),encoding='utf-8')
        config = dict(path=str(out),train='train/images',val='val/images',names=list(targets))
        if 'test' in counts: config['test']='test/images'
        (staging/'data.yaml').write_text(yaml.safe_dump(config,sort_keys=False),encoding='utf-8')
        report = dict(status='DATA_PREPARED_NOT_TRAINED',classes=list(targets),counts=counts,
                      source_folder=str(root),source_candidate=SOURCE,tree_only=tree_only)
        (staging/'preparation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        for name in ('README.roboflow.txt','README.dataset.txt','SOURCE.txt'):
            if (root/name).is_file(): shutil.copy2(root/name,staging/name)
        staging.rename(out)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command',required=True)
    download = sub.add_parser('download')
    download.add_argument('--version',type=int,required=True)
    download.add_argument('--out',type=Path)
    prep = sub.add_parser('prepare')
    prep.add_argument('--source',type=Path,required=True)
    prep.add_argument('--out',type=Path,default=HOME/'prepared')
    prep.add_argument('--tree-only',action='store_true')
    train = sub.add_parser('train')
    train.add_argument('--data',type=Path,default=HOME/'prepared'/'data.yaml')
    train.add_argument('--weights',type=Path,required=True)
    train.add_argument('--trust-weights',action='store_true')
    train.add_argument('--epochs',type=int,default=50)
    train.add_argument('--compute',default='cpu')
    train.add_argument('--tree-only',action='store_true')
    a = p.parse_args()
    if a.command=='download':
        if a.version<1: p.error('version must be positive')
        key = os.environ.get('ROBOFLOW_API_KEY')
        if not key: p.error('Set ROBOFLOW_API_KEY locally; never paste or commit it. A manual YOLOv8 export also works.')
        out = (a.out or HOME/f'raw-v{a.version}').expanduser().resolve()
        if out.exists(): p.error('Download target already exists; use a new folder')
        from roboflow import Roboflow
        project = Roboflow(api_key=key).workspace('crossyroad-q9hpe').project('crossyroad-e1abn')
        project.version(a.version).download(model_format='yolov8',location=str(out),overwrite=False)
        (out/'SOURCE.txt').write_text(f'CrossyRoad by CrossyRoad; Roboflow Universe; CC BY 4.0 as declared on source page.\n{SOURCE}\nVersion: {a.version}\nChanges: none at download. Retain export attribution and review image rights.\n',encoding='utf-8')
        print('Downloaded to PC:',out)
    elif a.command=='prepare':
        print(json.dumps(prepare(a.source,a.out,a.tree_only),indent=2))
    else:
        weights = a.weights.expanduser().resolve()
        if not weights.is_file() or not a.trust_weights:
            p.error('Select existing trusted local weights and pass --trust-weights')
        if not 1<=a.epochs<=1000: p.error('epochs must be from 1 to 1000')
        data = a.data.expanduser().resolve()
        targets = ('tree',) if a.tree_only else ('tree','rock')
        audit(data.parent,targets)
        from ultralytics import YOLO
        model = YOLO(str(weights),task='detect')
        run = HOME/'runs'/('obstacles-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
        model.train(data=str(data),epochs=a.epochs,imgsz=640,batch=4,workers=0,
                    device=a.compute,seed=42,project=str(run.parent),name=run.name,exist_ok=False)
        best = Path(model.trainer.best)
        evaluator = YOLO(str(best),task='detect')
        metrics = evaluator.val(data=str(data),split='val',device=a.compute)
        result = dict(status='TRAINED_VALIDATION_ONLY_NOT_DEVICE_VERIFIED',weights=str(best),
                      classes=list(targets),metrics={k:float(v) for k,v in metrics.results_dict.items()})
        (run/'validation_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
