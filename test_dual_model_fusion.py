import unittest
from types import SimpleNamespace
from dual_model_fusion import Detection,extract,merge,predict_both,validate_obstacle_names

class Values(list):
    def tolist(self): return list(self)

def result(names,cid=0,box=(10,10,30,30),confidence=.8):
    return SimpleNamespace(names=names,boxes=SimpleNamespace(xyxy=Values([box]),conf=Values([confidence]),cls=Values([cid])))

def detection(name,box=(10,10,30,30),score=.8,source='obstacles'):
    return Detection(box,score,source,0,name,'obstacle' if name in ('tree','rock') else 'primary')

class FusionTests(unittest.TestCase):
    def test_model_local_ids(self):
        first=extract(result({0:'car'}),'primary',(80,100,3))
        second=extract(result({0:'tree'}),'obstacles',(80,100,3))
        self.assertEqual([d.group for d in merge(first,second)],['primary','obstacle'])
    def test_tree_rock_duplicate(self):
        objects=merge([],[detection('tree'),detection('rock',score=.4)])
        self.assertEqual(len(objects),1);self.assertEqual(objects[0].name,'tree')
    def test_distant_obstacles_kept(self):
        self.assertEqual(len(merge([],[detection('tree'),detection('rock',(50,50,70,70))])),2)
    def test_primary_objects_not_suppressed_by_obstacle(self):
        self.assertEqual(len(merge([detection('car',source='primary')],[detection('tree')])),2)
    def test_primary_tree_replaced_by_specialist(self):
        objects=merge([detection('tree',source='primary')],[detection('rock')])
        self.assertEqual(len(objects),1);self.assertEqual(objects[0].source,'obstacles')
    def test_specialist_rejects_other_classes(self):
        with self.assertRaises(ValueError):validate_obstacle_names({0:'car'})
    def test_aliases(self):
        validate_obstacle_names({0:' Tree ',1:'Stone'})
    def test_empty_results(self):
        empty=SimpleNamespace(names={0:'tree'},boxes=SimpleNamespace(xyxy=Values(),conf=Values(),cls=Values()))
        self.assertEqual(extract(empty,'obstacles',(80,100,3)),[])
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):extract(result({0:'tree'},confidence=float('nan')),'obstacles',(80,100,3))
    def test_clips_to_frame(self):
        self.assertEqual(extract(result({0:'tree'},box=(-1,-1,120,90)),'obstacles',(80,100,3))[0].box,(0,0,100,80))
    def test_same_frame_separate_confidence_and_no_saves(self):
        calls=[]
        class Model:
            def __init__(self,name):self.name=name
            def predict(self,**kwargs):calls.append(kwargs);return [result({0:self.name})]
        frame=SimpleNamespace(shape=(80,100,3))
        objects=predict_both(frame,Model('car'),Model('tree'))
        self.assertEqual(len(objects),2);self.assertEqual(len(calls),2)
        self.assertIs(calls[0]['source'],frame);self.assertIs(calls[1]['source'],frame)
        self.assertEqual([c['conf'] for c in calls],[.25,.10])
        self.assertTrue(all(c['save'] is False and c['save_txt'] is False and c['save_crop'] is False for c in calls))
    def test_invalid_iou(self):
        with self.assertRaises(ValueError):merge([],[],0)

if __name__=='__main__':unittest.main()
