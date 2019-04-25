import unittest
import lib


class NoteTests(unittest.TestCase):

    # region __init__

    def test_init(self):
        note = lib.Note('c', lib.OctaveType.LINE_1, 8)
        self.assertEqual(note.note, 'c')
        self.assertEqual(note.octave, lib.OctaveType.LINE_1)
        self.assertEqual(note.base_duration, 8)
        self.assertEqual(note.modifiers, None)

    def test_init_invalid_note(self):
        with self.assertRaises(ValueError):
            lib.Note('x')

    def test_init_invalid_duration(self):
        with self.assertRaises(ValueError):
            lib.Note('c', base_duration=5)

    # endregion

    # region __str__

    def test_str(self):
        note = lib.Note('c')
        self.assertEqual(
            note.__str__(),
            'c4'
        )

    def test_str_full(self):
        note = lib.Note('d', lib.OctaveType.GREAT, 16)
        self.assertEqual(
            note.__str__(),
            'c,4'
        )

    def test_str_with_modifiers(self):
        note = lib.Note('d', lib.OctaveType.GREAT, 16)
        note.add_modifier(lib.NoteModifier.TIE)
        self.assertEqual(
            note.__str__(),
            'c,4~'
        )

    # endregion

    # region get_duration

    def test_get_duration(self):
        note = lib.Note('c', base_duration=4)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(
                note.get_duration(length),
                length / 4
            )

    def test_get_duration_with_dot(self):
        note = lib.Note('c', base_duration=4)
        note.add_modifier(lib.NoteModifier.DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(
                note.get_duration(length),
                length / 4 + length / 8
            )

    def test_get_duration_with_double_dot(self):
        note = lib.Note('c', base_duration=4)
        note.add_modifier(lib.NoteModifier.DOUBLE_DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(
                note.get_duration(length),
                length / 4 + length / 8 + length / 16
            )

    # endregion


if __name__ == '__main__':
    unittest.main()
