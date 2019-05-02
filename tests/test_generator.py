from typing import List
import unittest

from lib.Generator import Generator
from lib.Note import Note
from lib.NoteModifier import NoteModifier
from lib.OctaveType import OctaveType
from lib.Rest import Rest
from lib.Writeable import Writeable


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = Generator()

    def test_init(self):
        self.assertEqual((4, 4), self.generator.metre)
        self.assertEqual(4, self.generator.bar_count)
        self.assertEqual(4, self.generator.shortest_note_duration)

        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.start_note)
        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.end_note)
        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.ambitus['highest'])
        self.assertEqual(100, sum(self.generator.probability))

    # region Setters

    # region set_metre

    def test_set_metre(self):
        self.generator.set_metre(4, 4)
        self.assertEqual((4, 4), self.generator.metre)

    def test_invalid_metre(self):
        with self.assertRaises(ValueError):
            self.generator.set_metre(1, 3)

    # endregion

    # region set_bar_count

    def test_set_bar_count(self):
        self.generator.set_bar_count(16)
        self.assertEqual(16, self.generator.bar_count)

    def test_invalid_bar_count(self):
        with self.assertRaises(ValueError):
            self.generator.set_bar_count(-5)

    # endregion

    # region set_shortest_note_duration

    def test_set_shortest_note_duration(self):
        self.generator.set_shortest_note_duration(8)
        self.assertEqual(8, self.generator.shortest_note_duration)

    def test_set_invalid_note_duration(self):
        with self.assertRaises(ValueError):
            self.generator.set_shortest_note_duration(3)

    # endregion

    # region set_start_note

    def test_set_start_note(self):
        note = Note('c')
        self.generator.set_start_note(note)
        self.assertEqual(note, self.generator.start_note)

    # endregion

    # region set_end_note

    def test_set_end_note(self):
        note = Note('c')
        self.generator.set_end_note(note)
        self.assertEqual(note, self.generator.end_note)

    # endregion

    # region set_ambitus

    def test_set_ambitus_no_params(self):
        self.generator.set_ambitus()
        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.ambitus['highest'])

    def test_set_ambitus_lowest(self):
        note = Note('c')
        self.generator.set_ambitus(lowest=note)
        self.assertEqual(note, self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.ambitus['highest'])

    def test_set_ambitus_highest(self):
        note = Note('c')
        self.generator.set_ambitus(highest=note)
        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.ambitus['lowest'])
        self.assertEqual(note, self.generator.ambitus['highest'])

    def test_set_ambitus(self):
        lowest = Note('d')
        highest = Note('e')
        self.generator.set_ambitus(lowest=lowest, highest=highest)
        self.assertEqual(lowest, self.generator.ambitus['lowest'])
        self.assertEqual(highest, self.generator.ambitus['highest'])

    # endregion

    # region set_interval_probability

    def test_set_interval_probability(self):
        self.generator.set_interval_probability('1cz', 10)
        idx = self.generator.intervals.index('1cz')
        self.assertEqual(10, self.generator.probability[idx])

    def test_set_invalid_interval_name(self):
        with self.assertRaises(KeyError):
            self.generator.set_interval_probability('1czz', 10)

    # endregion

    # region set_intervals_probability

    def test_set_intervals_probability(self):
        probabilities = [10, 5, 5, 10, 5, 5, 10, 10, 5, 5, 10, 10, 5, 5]

        self.generator.set_intervals_probability(probabilities)
        self.assertEqual(probabilities, self.generator.probability)

    def test_set_intervals_probability_invalid_length(self):
        probabilities = [0, 1, 2]

        with self.assertRaises(ValueError):
            self.generator.set_intervals_probability(probabilities)

    def test_set_intervals_probability_more_than_one(self):
        intervals = self.generator.intervals
        probabilities = [0.5 for _ in intervals]

        with self.assertRaises(ValueError):
            self.generator.set_intervals_probability(probabilities)

    # endregion

    # endregion

    # region Utility methods

    def test_get_random_writeable(self):
        for i in range(10):
            writeable = self.generator.get_random_writeable(8)
            self.assertLessEqual(writeable.get_duration(self.generator.shortest_note_duration), 8)

    def test_get_random_note(self):
        note = self.generator.get_random_note('d', OctaveType.LINE_5)
        self.assertEqual('d', note.note)
        self.assertEqual(OctaveType.LINE_5, note.octave)

    def test_last_note_idx(self):
        self.generator.generated_data = [Rest(), Rest(), Note('c'), Rest()]
        idx = self.generator.get_last_note_idx()
        self.assertEqual(2, idx)

        self.generator.generated_data = [Rest(), Rest(), Rest(), Rest()]
        idx = self.generator.get_last_note_idx()
        self.assertEqual(-1, idx)

    def test_get_length_to_fill(self):
        self.generator.set_bar_count(1)
        self.generator.set_metre(4, 4)
        self.generator.set_shortest_note_duration(4)
        self.assertEqual(4, self.generator.get_length_to_fill())

        self.generator.set_bar_count(2)
        self.assertEqual(8, self.generator.get_length_to_fill())

        self.generator.set_shortest_note_duration(8)
        self.assertEqual(16, self.generator.get_length_to_fill())

    # endregion

    # region split_to_bars

    def test_split_to_bars(self):
        notes: List[Writeable] = [Note('c')] * 7
        notes.append(Rest())

        expected: List[List[Writeable]] = [
            [Note('c')] * 4,
            [Note('c'), Note('c'), Note('c'), Rest()]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(expected, bars)

    def test_split_to_bars_with_break(self):
        notes: List[Writeable] = [
            Note('c'), Note('c', base_duration=2), Note('c', base_duration=2),
            Note('c', base_duration=2), Rest()
        ]

        with_tie = Note('c')
        with_tie.add_modifier(NoteModifier.TIE)

        expected: List[List[Writeable]] = [
            [Note('c'), Note('c', base_duration=2), with_tie],
            [Note('c'), Note('c', base_duration=2), Rest()]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(expected, bars)

    # endregion

    # region group_bars

    def test_group_bars_4_4(self):
        bars: List[List[Writeable]] = [
            Note('c'), Note('c', base_duration=2), Note('c')
        ]

        with_tie = Note('c')
        with_tie.add_modifier(NoteModifier.TIE)
        expected: List[List[Writeable]] = [
            [Note('c'), with_tie, Note('c'), Note('c')]
        ]

        grouped_bars: List[List[Writeable]] = self.generator.group_bars(bars)

        self.assertEqual(expected, grouped_bars)

    # endregion

    # region generate

    def test_generate(self):
        data: List[Writeable] = self.generator.generate()

        first_note: Note = data[0]
        last_note: Note = data[self.generator.get_last_note_idx()]

        # Check start and end note
        self.assertEqual(self.generator.start_note.note, first_note.note)
        self.assertEqual(self.generator.start_note.octave, first_note.octave)

        last_note_idx = self.generator.get_last_note_idx()
        self.assertEqual(self.generator.end_note.note, last_note.note)
        self.assertEqual(self.generator.end_note.octave, last_note.note)

        # Check length
        expected_length = self.generator.get_length_to_fill()
        actual_length = sum([item.get_duration(self.generator.shortest_note_duration) for item in data])
        self.assertEqual(expected_length, actual_length)

        # Check ambitus
        notes = [item for item in data if isinstance(item, Note)]
        for note in notes:
            # TODO: Check if each of notes contains in ambitus (except first and last)
            pass

    def test_generate_group(self):
        data: List[List[Writeable]] = self.generator.generate(group=True)

        expected_bar_length = self.generator.get_length_to_fill() / self.generator.bar_count
        for bar in data:
            actual_length = sum([item.get_duration(self.generator.shortest_note_duration) for item in bar])
            self.assertEqual(expected_bar_length, actual_length)

    # endregion


if __name__ == "__main__":
    unittest.main()
