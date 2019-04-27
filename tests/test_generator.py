from typing import List
import unittest
import lib


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = lib.Generator()

    # region set_metre

    def test_set_metre(self):
        self.generator.set_metre(4, 4)
        self.assertEqual(
            self.generator.metre,
            (4, 4)
        )

    def test_invalid_metre(self):
        with self.assertRaises(ValueError):
            self.generator.set_metre(1, 3)

    # endregion

    # region set_bar_count

    def test_set_bar_count(self):
        self.generator.set_bar_count(16)
        self.assertEqual(
            self.generator.bar_count,
            16
        )

    def test_invalid_bar_count(self):
        with self.assertRaises(ValueError):
            self.generator.set_bar_count(-5)

    # endregion

    # region set_shortest_note_duration

    def test_set_shortest_note_duration(self):
        self.generator.set_shortest_note_duration(8)
        self.assertEqual(
            self.generator.shortest_note_duration,
            8
        )

    def test_set_invalid_note_duration(self):
        with self.assertRaises(ValueError):
            self.generator.set_shortest_note_duration(3)

    # endregion

    # region set_start_note

    def test_set_start_note(self):
        note = lib.Note('c')
        self.generator.set_start_note(note)
        self.assertEqual(
            self.generator.start_note,
            note
        )

    # endregion

    # region set_end_note

    def test_set_end_note(self):
        note = lib.Note('c')
        self.generator.set_end_note(note)
        self.assertEqual(
            self.generator.end_note,
            note
        )

    # endregion

    # region set_ambitus

    def test_set_ambitus_no_params(self):
        self.generator.set_ambitus()
        self.assertEqual(
            self.generator.ambitus['lowest'],
            lib.Note('c', lib.OctaveType.SMALL)
        )
        self.assertEqual(
            self.generator.ambitus['highest'],
            lib.Note('c', lib.OctaveType.LINE_1)
        )

    def test_set_ambitus_lowest(self):
        note = lib.Note('c')
        self.generator.set_ambitus(lowest=note)
        self.assertEqual(
            self.generator.ambitus['lowest'],
            note
        )
        self.assertEqual(
            self.generator.ambitus['highest'],
            lib.Note('c', lib.OctaveType.LINE_1)
        )

    def test_set_ambitus_highest(self):
        note = lib.Note('c')
        self.generator.set_ambitus(highest=note)
        self.assertEqual(
            self.generator.ambitus['lowest'],
            lib.Note('c', lib.OctaveType.SMALL)
        )
        self.assertEqual(
            self.generator.ambitus['highest'],
            note
        )

    def test_set_ambitus(self):
        lowest = lib.Note('d')
        highest = lib.Note('e')
        self.generator.set_ambitus(lowest=lowest, highest=highest)
        self.assertEqual(
            self.generator.ambitus['lowest'],
            lowest
        )
        self.assertEqual(
            self.generator.ambitus['highest'],
            highest
        )

    # endregion

    # region set_interval_probability

    def test_set_interval_probability(self):
        self.generator.set_interval_probability('1cz', 0.1)
        idx = self.generator.intervals.index('1cz')
        self.assertEqual(
            self.generator.probability[idx],
            0.1
        )

    def test_set_invalid_interval_name(self):
        with self.assertRaises(KeyError):
            self.generator.set_interval_probability('1czz', 0.1)

    # endregion

    # region set_intervals_probability

    def test_set_intervals_probability(self):
        probabilities = [10, 5, 5, 10, 5, 5, 10, 10, 5, 5, 10, 10, 5, 5]

        self.generator.set_intervals_probability(probabilities)
        self.assertEqual(
            self.generator.probability,
            probabilities
        )

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

    # region split_to_bars

    def test_split_to_bars(self):
        notes: List[lib.Writeable] = [lib.Note('c')] * 7
        notes.append(lib.Rest())

        expected: List[List[lib.Writeable]] = [
            [lib.Note('c')] * 4,
            [lib.Note('c'), lib.Note('c'), lib.Note('c'), lib.Rest()]
        ]

        bars: List[List[lib.Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(bars, expected)

    def test_split_to_bars_with_break(self):
        notes: List[lib.Writeable] = [
            lib.Note('c'), lib.Note('c', base_duration=2), lib.Note('c', base_duration=2),
            lib.Note('c', base_duration=2), lib.Rest()
        ]

        with_tie = lib.Note('c')
        with_tie.add_modifier(lib.NoteModifier.TIE)

        expected: List[List[lib.Writeable]] = [
            [lib.Note('c'), lib.Note('c', base_duration=2), with_tie],
            [lib.Note('c'), lib.Note('c', base_duration=2), lib.Rest()]
        ]

        bars: List[List[lib.Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(bars, expected)

    # endregion

    # region group_bars

    def test_group_bars_4_4(self):
        bars: List[List[lib.Writeable]] = [
            lib.Note('c'), lib.Note('c', base_duration=2), lib.Note('c')
        ]

        with_tie = lib.Note('c')
        with_tie.add_modifier(lib.NoteModifier.TIE)
        expected: List[List[lib.Writeable]] = [
            [lib.Note('c'), with_tie, lib.Note('c'), lib.Note('c')]
        ]

        grouped_bars: List[List[lib.Writeable]] = self.generator.group_bars(bars)

        self.assertEqual(grouped_bars, expected)

    # endregion


if __name__ == "__main__":
    unittest.main()
