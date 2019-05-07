import unittest

import lib
from lib.theory.Interval import Interval
from lib.theory.Note import Note
from lib.theory.NoteModifier import NoteModifier
from lib.theory.OctaveType import OctaveType
from lib.errors import InvalidNoteDuration


class NoteTests(unittest.TestCase):

    # region __init__

    def test_init(self):
        note = Note('c', OctaveType.LINE_1, 8)
        self.assertEqual('c', note.note)
        self.assertEqual(OctaveType.LINE_1, note.octave)
        self.assertEqual(8, note.base_duration)
        self.assertEqual([], note.modifiers)

    def test_init_invalid_note(self):
        with self.assertRaises(ValueError):
            Note('x')

    def test_init_invalid_duration(self):
        with self.assertRaises(ValueError):
            Note('c', base_duration=5)

    # endregion

    # region __str__

    def test_str(self):
        note = Note('c')
        self.assertEqual('c4', str(note))

    def test_str_full(self):
        note = Note('d', OctaveType.GREAT, 16)
        self.assertEqual('d,16', str(note))

    def test_str_with_modifiers(self):
        note = Note('d', OctaveType.GREAT, 16)
        note.add_modifier(NoteModifier.TIE)
        self.assertEqual('d,16~', str(note))

        note.add_modifier(NoteModifier.DOT)
        self.assertEqual('d,16.~', str(note))

    # endregion

    # region __repr__

    def test_repr(self):
        note = Note('c')
        self.assertEqual('Note <c4>', repr(note))

    # endregion

    # region __add__ / __sub__

    def test_add_interval(self):
        note = Note('c')

        intervals = Interval.names()
        expected = ['c', 'des', 'd', 'ees', 'e', 'f', 'fis', 'ges', 'g', 'aes', 'a', 'bes', 'b', 'c']

        for i in range(len(expected)):
            new_note: Note = note + Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

        note = Note('f')
        expected = ['f', 'ges', 'g', 'aes', 'a', 'bes', 'b', 'ces', 'c', 'des', 'd', 'ees', 'e', 'f']

        for i in range(len(expected)):
            new_note: Note = note + Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

    def test_add_unsupported(self):
        note = Note('c')

        with self.assertRaises(NotImplementedError):
            note + 5

    def test_sub_interval(self):
        note = Note('c')

        intervals = Interval.names()
        expected = ['c', 'b', 'bes', 'a', 'aes', 'g', 'ges', 'fis', 'f', 'e', 'ees', 'd', 'des', 'c']

        for i in range(len(expected)):
            new_note: Note = note - Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

        note = Note('f')
        expected = ['f', 'e', 'ees', 'd', 'des', 'c', 'ces', 'b', 'bes', 'a', 'aes', 'g', 'ges', 'f']

        for i in range(len(expected)):
            new_note: Note = note - Interval(intervals[i])
            self.assertEqual(expected[i], new_note.note)

    def test_sub_unsupported(self):
        note = Note('c')

        with self.assertRaises(NotImplementedError):
            note - 5

    # endregion

    # region __eq__

    def test_eq(self):
        note_1 = Note('c', base_duration=4)
        note_2 = Note('c', base_duration=4)

        self.assertEqual(note_1, note_2)

    # endregion

    # region __lt__ / __le__

    def test_lt(self):
        note_1 = Note('d')
        note_2 = Note('c')
        self.assertTrue(note_2 < note_1)

        note_2 = Note('d')
        self.assertFalse(note_2 < note_1)

        note_1 = Note('d', OctaveType.CONTRA)
        note_2 = Note('d', OctaveType.SMALL)
        self.assertFalse(note_2 < note_1)

    def test_le(self):
        note_1 = Note('d')
        note_2 = Note('c')
        self.assertTrue(note_2 <= note_1)

        note_2 = Note('d')
        self.assertTrue(note_2 <= note_1)

        note_1 = Note('d', OctaveType.CONTRA)
        note_2 = Note('d', OctaveType.SMALL)
        self.assertFalse(note_2 <= note_1)

    # endregion

    # region __gt__ / __ge__

    def test_gt(self):
        note_1 = Note('c')
        note_2 = Note('d')
        self.assertTrue(note_2 > note_1)

        note_2 = Note('c')
        self.assertFalse(note_2 > note_1)

        note_1 = Note('d', OctaveType.CONTRA)
        note_2 = Note('d', OctaveType.SMALL)
        self.assertTrue(note_2 > note_1)

    def test_ge(self):
        note_1 = Note('c')
        note_2 = Note('d')
        self.assertTrue(note_2 >= note_1)

        note_2 = Note('c')
        self.assertTrue(note_2 >= note_1)

        note_1 = Note('d', OctaveType.CONTRA)
        note_2 = Note('d', OctaveType.SMALL)
        self.assertTrue(note_2 >= note_1)

    # endregion

    # region get_base_note / get_base_note_id / get_id / get_accidentals / get_accidentals_value

    def test_get_base_note(self):
        note = Note('cis')
        self.assertEqual('c', note.get_base_note())

    def test_get_base_note_id(self):
        note = Note('cis')
        self.assertEqual(0, note.get_base_note_id())

    def test_get_id(self):
        note = Note('cis')
        self.assertEqual(49, note.get_id())

    def test_get_accidentals(self):
        note = Note('cis')
        self.assertEqual('is', note.get_accidentals())

    def test_get_accidentals_value(self):
        note = Note('cis')
        self.assertEqual(1, note.get_accidentals_value())

        note = Note('ces')
        self.assertEqual(-1, note.get_accidentals_value())

    # endregion

    # region create_accidentals_string

    def test_create_accidentals_string(self):
        values = range(-3, 3)
        expected = ['eseses', 'eses', 'es', '', 'is', 'isis', 'isisis']

        for i in values:
            actual = Note.create_accidentals_string(i)
            self.assertEqual(expected[i + 3], actual)

    # endregion

    # region random

    def test_random_correct_duration(self):
        lib.Generator.set_shortest_note_duration(16)

        for i in range(50):
            note = Note.random(16)
            self.assertGreaterEqual(note.get_duration(lib.Generator.shortest_note_duration), 1)

        for i in range(50):
            note = Note.random()
            self.assertGreaterEqual(note.get_duration(lib.Generator.shortest_note_duration), 1)

        for i in range(50):
            note = Note.random(1)
            self.assertEqual(note.get_duration(lib.Generator.shortest_note_duration), 1)

    # endregion

    # region get_duration

    def test_get_duration(self):
        note = Note('c', base_duration=4)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4, note.get_duration(length))

    def test_get_duration_with_dot(self):
        note = Note('c', base_duration=4)
        note.add_modifier(NoteModifier.DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8, note.get_duration(length))

    def test_get_duration_with_double_dot(self):
        note = Note('c', base_duration=4)
        note.add_modifier(NoteModifier.DOUBLE_DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8 + length / 16, note.get_duration(length))

    def test_get_duration_raises_exception(self):
        note = Note('c')

        with self.assertRaises(InvalidNoteDuration):
            note.get_duration(5)

    # endregion

    # region add_modifier / remove modifier

    def test_add_remove_modifier(self):
        note = Note('c')
        note.add_modifier(NoteModifier.DOT)
        self.assertTrue(NoteModifier.DOT in note.modifiers)

        note.remove_modifier(NoteModifier.DOT)
        self.assertTrue(NoteModifier.DOT not in note.modifiers)

    def test_add_modifier_unique(self):
        note = Note('c')
        note.add_modifier(NoteModifier.DOT)
        note.add_modifier(NoteModifier.DOT)

        self.assertEqual(1, len(note.modifiers))

    def test_add_modifier_double_dot_removes_dot(self):
        note = Note('c')
        note.add_modifier(NoteModifier.DOT)
        note.add_modifier(NoteModifier.DOUBLE_DOT)

        self.assertTrue(NoteModifier.DOUBLE_DOT in note.modifiers)
        self.assertTrue(NoteModifier.DOT not in note.modifiers)

    def test_add_modifier_dot_removes_double_dot(self):
        note = Note('c')
        note.add_modifier(NoteModifier.DOUBLE_DOT)
        note.add_modifier(NoteModifier.DOT)

        self.assertTrue(NoteModifier.DOT in note.modifiers)
        self.assertTrue(NoteModifier.DOUBLE_DOT not in note.modifiers)

    def test_modifiers_order(self):
        note = Note('c')
        note.add_modifier(NoteModifier.TIE)
        note.add_modifier(NoteModifier.DOT)

        self.assertEqual(2, len(note.modifiers))
        self.assertEqual(NoteModifier.TIE, note.modifiers[1])
        self.assertEqual(NoteModifier.DOT, note.modifiers[0])

    # endregion


if __name__ == '__main__':
    unittest.main()
