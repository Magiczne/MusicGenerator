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

    # region __repr__

    def test_repr(self):
        note = lib.Note('c')
        self.assertEqual('Note <c4>', repr(note))

    # endregion

    # region __add__ / __sub__

    def test_add_interval(self):
        note = lib.Note('c')

        intervals = lib.Interval.names()
        expected = ['c', 'des', 'd', 'ees', 'e', 'f', 'fis', 'ges', 'g', 'aes', 'a', 'bes', 'b', 'c']

        for i in range(len(expected)):
            new_note: lib.Note = note + lib.Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

        note = lib.Note('f')
        expected = ['f', 'ges', 'g', 'aes', 'a', 'bes', 'b', 'ces', 'c', 'des', 'd', 'ees', 'e', 'f']

        for i in range(len(expected)):
            new_note: lib.Note = note + lib.Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

    def test_sub_interval(self):
        note = lib.Note('c')

        intervals = lib.Interval.names()
        expected = ['c', 'b', 'bes', 'a', 'aes', 'g', 'ges', 'fis', 'f', 'e', 'ees', 'd', 'des', 'c']

        for i in range(len(expected)):
            new_note: lib.Note = note - lib.Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

        note = lib.Note('f')
        expected = ['f', 'e', 'ees', 'd', 'des', 'c', 'ces', 'b', 'bes', 'a', 'aes', 'g', 'ges', 'f']

        for i in range(len(expected)):
            new_note: lib.Note = note - lib.Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

    # endregion

    # region get_base_note / get_accidentals / get_accidentals_value

    def test_get_base_note(self):
        note = lib.Note('cis')
        self.assertEqual('c', note.get_base_note())

    def test_get_accidentals(self):
        note = lib.Note('cis')
        self.assertEqual('is', note.get_accidentals())

    def test_get_accidentals_value(self):
        note = lib.Note('cis')
        self.assertEqual(1, note.get_accidentals_value())

        note = lib.Note('ces')
        self.assertEqual(-1, note.get_accidentals_value())

    # endregion

    # region create_accidentals_string

    def test_create_accidentals_string(self):
        values = range(-3, 3)
        expected = ['eseses', 'eses', 'es', '', 'is', 'isis', 'isisis']

        for i in values:
            actual = lib.Note.create_accidentals_string(i)
            self.assertEqual(expected[i + 3], actual)

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
