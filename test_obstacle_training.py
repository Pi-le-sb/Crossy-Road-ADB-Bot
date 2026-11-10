import tempfile
from pathlib import Path
import unittest
import yaml
from PIL import Image
from obstacle_training import prepare,audit


class DatasetTests(unittest.TestCase):
    def make_data(self,root,names=None):
        names = names or ['Tree','Stone','car']
        (root/'data.yaml').write_text(yaml.safe_dump(dict(names=names)),encoding='utf-8')
        for i,split in enumerate(('train','valid')):
            (root/split/'images').mkdir(parents=True)
            (root/split/'labels').mkdir()
            Image.new('RGB',(32,32),(30+i,120,40)).save(root/split/'images'/'one.png')
            (root/split/'labels'/'one.txt').write_text('0 0.25 0.25 0.2 0.2\n1 0.7 0.7 0.2 0.2\n2 0.5 0.5 0.1 0.1\n',encoding='utf-8')

    def test_remap_and_retention(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'source'; root.mkdir(); self.make_data(root)
            out = Path(d)/'prepared'; report = prepare(root,out)
            self.assertEqual(report['counts']['train'],[1,1])
            self.assertEqual((out/'train/labels/000000.txt').read_text().splitlines(),['0 0.25 0.25 0.2 0.2','1 0.7 0.7 0.2 0.2'])
            self.assertEqual(len((root/'train/labels/one.txt').read_text().splitlines()),3)

    def test_missing_rock_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.make_data(root,['Tree','coin','car'])
            with self.assertRaises(ValueError): audit(root)
            self.assertEqual(audit(root,('tree',))[1]['val'],[1])

    def test_missing_label_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.make_data(root); (root/'train/labels/one.txt').unlink()
            with self.assertRaises(ValueError): audit(root)

    def test_duplicates_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.make_data(root)
            (root/'valid/images/one.png').write_bytes((root/'train/images/one.png').read_bytes())
            with self.assertRaises(ValueError): audit(root)

    def test_invalid_box_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.make_data(root)
            (root/'train/labels/one.txt').write_text('0 0.1 0.5 0.8 0.2')
            with self.assertRaises(ValueError): audit(root)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/'source'; root.mkdir(); self.make_data(root)
            out = Path(d)/'out'; out.mkdir(); (out/'keep.txt').write_text('keep')
            with self.assertRaises(ValueError): prepare(root,out)
            self.assertEqual((out/'keep.txt').read_text(),'keep')

    def test_missing_validation_class_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.make_data(root)
            (root/'valid/labels/one.txt').write_text('0 0.25 0.25 0.2 0.2')
            with self.assertRaises(ValueError): audit(root)


if __name__=='__main__':
    unittest.main()
