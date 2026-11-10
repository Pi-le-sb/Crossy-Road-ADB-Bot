import unittest
import numpy as np
from motion_preview import camera_shift, relative_velocity


class MotionTests(unittest.TestCase):
    def test_camera_translation(self):
        np.testing.assert_allclose(camera_shift(np.tile([3,-4],(12,1))),[3,-4])

    def test_reference_outliers(self):
        d = np.vstack([np.tile([2,1],(16,1)),np.tile([90,30],(4,1))])
        np.testing.assert_allclose(camera_shift(d),[2,1])

    def test_insufficient_reference(self):
        self.assertIsNone(camera_shift([[1,1]]*7))
        self.assertIsNone(camera_shift([[float('nan'),1]]*12))

    def test_inconsistent_reference(self):
        self.assertIsNone(camera_shift([[i*10,0] for i in range(12)]))

    def test_camera_removed_from_velocity(self):
        old = np.array([[10.,10.],[30.,30.]])
        new = old + [[3,2],[13,2]]
        np.testing.assert_allclose(relative_velocity(old,new,np.array([3,2]),.5),[[0,0],[20,0]])

    def test_bad_intervals(self):
        for dt in (0,-1,2,float('nan')):
            with self.assertRaises(ValueError): relative_velocity(np.zeros((1,2)),np.zeros((1,2)),np.zeros(2),dt)


if __name__ == '__main__':
    unittest.main()
