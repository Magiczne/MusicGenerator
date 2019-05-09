import unittest

from lib.theory.OctaveType import OctaveType


class TestOctaveType(unittest.TestCase):
    def test_get_id(self):
        octave_id = OctaveType.get_id(OctaveType.LINE_1)
        self.assertEqual(5, octave_id)

    def test_from_id(self):
        octave = OctaveType.from_id(5)
        self.assertEqual(OctaveType.LINE_1, octave)

    def test_from_id_out_of_range(self):
        octave = OctaveType.from_id(-1)
        self.assertEqual(OctaveType.DOUBLE_CONTRA, octave)

        octave = OctaveType.from_id(11)
        self.assertEqual(OctaveType.LINE_6, octave)

    def test_octave_down(self):
        self.assertEqual(OctaveType.LINE_3, OctaveType.get_octave_down(OctaveType.LINE_4))


if __name__ == "__main__":
    unittest.main()
