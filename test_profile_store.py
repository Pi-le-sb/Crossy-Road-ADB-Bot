import unittest
import tempfile
from pathlib import Path
import numpy as np
from profile_store import save_profile,load_profile


class ProfileTests(unittest.TestCase):
    def profile(self):
        return dict(shape=np.array([2408,1080]),box=np.array([100,800,80,40]),
                    player=np.zeros((40,20,3),np.uint8),button=np.zeros((40,80,3),np.uint8))

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sub'/'profile.npz'
            original = self.profile()
            save_profile(p,original)
            loaded = load_profile(p)
            for key in original: np.testing.assert_array_equal(loaded[key],original[key])
            self.assertEqual(list(p.parent.iterdir()),[p])

    def test_invalid_template_preserves_old(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'profile.npz'
            save_profile(p,self.profile())
            old = p.read_bytes()
            broken = self.profile(); broken['player'] = np.zeros((2,2,3),np.uint8)
            with self.assertRaises(ValueError): save_profile(p,broken)
            self.assertEqual(p.read_bytes(),old)

    def test_bad_box(self):
        with tempfile.TemporaryDirectory() as d:
            broken = self.profile(); broken['box'] = np.array([900,800,80,40])
            with self.assertRaises(ValueError): save_profile(Path(d)/'x.npz',broken)

    def test_wrong_version(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.npz'; np.savez(p,version=np.array([2]))
            with self.assertRaises(ValueError): load_profile(p)

    def test_corrupt_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.npz'; p.write_bytes(b'not a profile')
            with self.assertRaises(ValueError): load_profile(p)


if __name__ == '__main__':
    unittest.main()
