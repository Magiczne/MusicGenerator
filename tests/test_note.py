import unittest
import lib


class NoteTests(unittest.TestCase):

    # region __init__

    def test_init(self):
        note = lib.Note('c', lib.OctaveType.LINE_1, 8)
        self.assertEqual('c', note.note)
        self.assertEqual(lib.OctaveType.LINE_1, note.octave)
        self.assertEqual(8, note.base_duration)
        self.assertEqual([], note.modifiers)

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
        self.assertEqual('c4', str(note))

    def test_str_full(self):
        note = lib.Note('d', lib.OctaveType.GREAT, 16)
        self.assertEqual('d,16', str(note))

    def test_str_with_modifiers(self):
        note = lib.Note('d', lib.OctaveType.GREAT, 16)
        note.add_modifier(lib.NoteModifier.TIE)
        self.assertEqual('d,16~', str(note))

        note.add_modifier(lib.NoteModifier.DOT)
        self.assertEqual('d,16.~', str(note))

    # endregion

    # region get_duration

    def test_get_duration(self):
        note = lib.Note('c', base_duration=4)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4, note.get_duration(length))

    def test_get_duration_with_dot(self):
        note = lib.Note('c', base_duration=4)
        note.add_modifier(lib.NoteModifier.DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8, note.get_duration(length))

    def test_get_duration_with_double_dot(self):
        note = lib.Note('c', base_duration=4)
        note.add_modifier(lib.NoteModifier.DOUBLE_DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8 + length / 16, note.get_duration(length))

    # endregion

    # region add_modifier / remove modifier

    def test_add_remove_modifier(self):
        note = lib.Note('c')
        note.add_modifier(lib.NoteModifier.DOT)
        self.assertTrue(lib.NoteModifier.DOT in note.modifiers)

        note.remove_modifier(lib.NoteModifier.DOT)
        self.assertTrue(lib.NoteModifier.DOT not in note.modifiers)

    def test_add_modifier_unique(self):
        note = lib.Note('c')
        note.add_modifier(lib.NoteModifier.DOT)
        note.add_modifier(lib.NoteModifier.DOT)

        self.assertEqual(1, len(note.modifiers))

    def test_add_modifier_double_dot_priority_over_dot(self):
        note = lib.Note('c')
        note.add_modifier(lib.NoteModifier.DOT)
        note.add_modifier(lib.NoteModifier.DOUBLE_DOT)

        self.assertTrue(lib.NoteModifier.DOUBLE_DOT in note.modifiers)
        self.assertTrue(lib.NoteModifier.DOT not in note.modifiers)

    def test_modifiers_order(self):
        note = lib.Note('c')
        note.add_modifier(lib.NoteModifier.TIE)
        note.add_modifier(lib.NoteModifier.DOT)

        self.assertEqual(2, len(note.modifiers))
        self.assertEqual(lib.NoteModifier.TIE, note.modifiers[1])
        self.assertEqual(lib.NoteModifier.DOT, note.modifiers[0])

    # endregion


if __name__ == '__main__':
    unittest.main()
