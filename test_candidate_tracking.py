import unittest
import numpy as np
from candidate_tracking import group_points,MotionTracker


def cloud(x=0,y=0):
    return np.array([[x,y],[x+3,y],[x,y+3]],dtype=float)


def speed(x=10,y=0):
    return np.tile([x,y],(3,1)).astype(float)


class TrackingTests(unittest.TestCase):
    def test_empty_and_too_few(self):
        self.assertEqual(group_points([],[]),[])
        self.assertEqual(group_points([[0,0],[1,1]],[[1,0],[1,0]]),[])

    def test_two_groups(self):
        result = group_points(np.vstack([cloud(),cloud(100,0)]),np.vstack([speed(),speed()]))
        self.assertEqual(len(result),2)
        self.assertEqual(result[0].count,3)

    def test_velocity_separation(self):
        result = group_points(np.vstack([cloud(),cloud(2,0)]),np.vstack([speed(50),speed(-50)]))
        self.assertEqual(len(result),2)

    def test_invalid_points(self):
        p = np.vstack([cloud(),[float('nan'),0]])
        self.assertEqual(len(group_points(p,np.vstack([speed(),[10,0]]))),1)
        with self.assertRaises(ValueError): group_points(cloud(),[[10,0]])

    def test_camera_compensated_identity(self):
        tracker = MotionTracker()
        first = tracker.update(cloud(),speed(),[0,0],.5)[0]
        second = tracker.update(cloud(13,4),speed(),[8,4],.5)[0]
        self.assertEqual(first.id,second.id)
        self.assertEqual(second.hits,2)

    def test_missed_tracks_not_reported(self):
        tracker = MotionTracker()
        first = tracker.update(cloud(),speed(),[0,0],.5)[0]
        self.assertEqual(tracker.update([],[],[0,0],.5),[])
        recovered = tracker.update(cloud(10),speed(),[0,0],.5)[0]
        self.assertEqual(first.id,recovered.id)
        self.assertEqual(recovered.hits,1)

    def test_expiry_and_reset(self):
        tracker = MotionTracker()
        first = tracker.update(cloud(),speed(),[0,0],.5)[0]
        for _ in range(3): tracker.update([],[],[0,0],.5)
        self.assertEqual(tracker.tracks,[])
        second = tracker.update(cloud(),speed(),[0,0],.5)[0]
        self.assertNotEqual(first.id,second.id)
        tracker.reset()
        self.assertEqual(tracker.tracks,[])

    def test_invalid_timing_clears_tracks(self):
        tracker = MotionTracker()
        tracker.update(cloud(),speed(),[0,0],.5)
        with self.assertRaises(ValueError): tracker.update(cloud(),speed(),[0,0],2)
        self.assertEqual(tracker.tracks,[])


if __name__ == '__main__':
    unittest.main()
