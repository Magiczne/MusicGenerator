import unittest
import lib


class TestOctaveType(unittest.TestCase):
    def test_get_id(self):
        octave_id = lib.OctaveType.get_id(lib.OctaveType.LINE_1)
        self.assertEqual(5, octave_id)

    def test_from_id(self):
        octave = lib.OctaveType.from_id(5)
        self.assertEqual(lib.OctaveType.LINE_1, octave)

    def test_from_id_too_low(self):
        with self.assertRaises(KeyError):
            lib.OctaveType.from_id(-1)

    def test_from_id_too_high(self):
        with self.assertRaises(KeyError):
            lib.OctaveType.from_id(12)

    def test_octave_down(self):
        self.assertEqual(lib.OctaveType.LINE_3, lib.OctaveType.get_octave_down(lib.OctaveType.LINE_4))
