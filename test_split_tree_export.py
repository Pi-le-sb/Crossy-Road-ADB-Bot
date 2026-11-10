import json
from pathlib import Path
import tempfile
import unittest
import yaml
from PIL import Image
from split_tree_export import split_export


class SplitTests(unittest.TestCase):
    def source(self,base):
        root = base/'raw'; (root/'train/images').mkdir(parents=True); (root/'train/labels').mkdir()
        names = ['Character','Coin','Coin Total','Lily Pad','Log','Play','Red Light','Safe','Score','Tap','TopScore','Train','Tree','Vehicle']
        (root/'data.yaml').write_text(yaml.safe_dump(dict(names=names,nc=14,train='../train/images',val='../valid/images',test='../test/images')))
        for i in range(5):
            Image.new('RGB',(32,32),(30+i,110,50)).save(root/'train/images'/f'image{i}.png')
            (root/'train/labels'/f'image{i}.txt').write_text('12 0.5 0.5 0.2 0.2\n13 0.4 0.4 0.1 0.1\n')
        return root

    def test_class12_remap_and_original_kept(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base); original=(root/'data.yaml').read_bytes()
            out=base/'prepared'; report=split_export(root,out)
            self.assertEqual(report['original_tree_id'],12)
            self.assertEqual(report['counts']['val']['images'],1)
            self.assertEqual(report['counts']['train']['images'],4)
            self.assertEqual((root/'data.yaml').read_bytes(),original)
            for label in out.glob('*/labels/*.txt'):
                self.assertEqual(label.read_text().strip(),'0 0.5 0.5 0.2 0.2')
            self.assertEqual(yaml.safe_load((out/'data.yaml').read_text())['names'],['tree'])

    def test_repeatable_split(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base)
            a=split_export(root,base/'one'); b=split_export(root,base/'two')
            self.assertEqual(a['assignments'],b['assignments'])

    def test_deduplicate(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base)
            (root/'train/images/copy.png').write_bytes((root/'train/images/image0.png').read_bytes())
            (root/'train/labels/copy.txt').write_bytes((root/'train/labels/image0.txt').read_bytes())
            report=split_export(root,base/'out')
            self.assertEqual(len(report['dropped_exact_duplicates']),1)
            self.assertEqual(sum(c['images'] for c in report['counts'].values()),5)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base); out=base/'out'; out.mkdir()
            with self.assertRaises(ValueError): split_export(root,out)
            self.assertTrue(out.is_dir())

    def test_bad_label(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base)
            (root/'train/labels/image0.txt').write_text('12 0.1 0.5 0.8 0.2')
            with self.assertRaises(ValueError): split_export(root,base/'out')
            self.assertFalse((base/'out').exists())

    def test_missing_label(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base); (root/'train/labels/image0.txt').unlink()
            with self.assertRaises(ValueError): split_export(root,base/'out')

    def test_single_positive_group_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); root=self.source(base)
            for i in range(1,5): (root/'train/labels'/f'image{i}.txt').write_text('')
            with self.assertRaises(ValueError): split_export(root,base/'out')


if __name__=='__main__':
    unittest.main()
