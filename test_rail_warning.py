import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from rail_warning import RailWarningLatch,predict_with_warning


def obj(name='train_light_on',score=.8,source='primary'):
    return SimpleNamespace(name=name,confidence=score,source=source)


class WarningTests(unittest.TestCase):
    def test_on_requests_stop(self):
        decision=RailWarningLatch().update([obj()])
        self.assertTrue(decision.stop_requested);self.assertFalse(decision.crossing_clear)
    def test_blink_or_missed_frames_do_not_release(self):
        latch=RailWarningLatch();latch.update([obj()])
        for _ in range(100):self.assertTrue(latch.update([]).stop_requested)
    def test_no_detection_is_not_clear(self):
        decision=RailWarningLatch().update([])
        self.assertEqual(decision.state,'UNKNOWN_NO_WARNING_DETECTED');self.assertFalse(decision.crossing_clear)
    def test_bad_frame_requests_stop(self):
        self.assertTrue(RailWarningLatch().update([],frame_ok=False).stop_requested)
    def test_wrong_classes_sources_and_weak_scores_do_not_trigger(self):
        latch=RailWarningLatch()
        self.assertFalse(latch.update([obj('car'),obj(source='obstacles'),obj(score=.05),obj(score=float('nan'))]).stop_requested)
    def test_threshold_equality_triggers(self):
        self.assertTrue(RailWarningLatch(.1).update([obj(score=.1)]).stop_requested)
    def test_signal_threshold_does_not_lower_other_classes(self):
        calls=[];frame=object()
        def predictor(*args,**kwargs):
            calls.append((args,kwargs));return [obj(score=.15),obj('car',.15),obj('car',.8),obj('tree',.15,'obstacles')]
        out=predict_with_warning(frame,None,None,primary_conf=.25,warning_conf=.10,predictor=predictor)
        self.assertIs(calls[0][0][0],frame);self.assertEqual(calls[0][1]['primary_conf'],.10)
        self.assertEqual([(o.name,o.confidence) for o in out],[('train_light_on',.15),('car',.8),('tree',.15)])
    def test_invalid_thresholds(self):
        for value in (0,1.1,float('nan')):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):RailWarningLatch(value)
    def test_warning_evaluated_before_player_filter(self):
        tree=ast.parse(Path(__file__).with_name('dual_model_preview.py').read_text(encoding='utf-8'))
        update=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='update' and isinstance(n.func.value,ast.Name) and n.func.value.id=='warning']
        exclusion=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='exclude_player']
        self.assertTrue(update and exclusion and update[0]<exclusion[0])
    def test_preview_does_not_call_input_executor(self):
        tree=ast.parse(Path(__file__).with_name('dual_model_preview.py').read_text(encoding='utf-8'))
        names={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
        self.assertFalse(names & {'tap','swipe','run','adb_cmd'})

if __name__=='__main__':unittest.main()
