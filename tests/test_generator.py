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

    # TODO: split_to_bars tests

    # endregion

    # region group_bars

    # TODO: group_bars tests

    # endregion

    # region generate

    # TODO: generate tests

    # endregion


if __name__ == "__main__":
    unittest.main()
