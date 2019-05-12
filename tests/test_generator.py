from typing import List
import unittest
import math

from lib.Generator import Generator
from lib.theory.Interval import Interval
from lib.theory.Note import Note
from lib.theory.NoteModifier import NoteModifier
from lib.theory.OctaveType import OctaveType
from lib.theory.Rest import Rest
from lib.theory.RestModifier import RestModifier
from lib.theory.Writeable import Writeable
import lib.errors as errors


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = Generator()

    def test_init(self):
        self.assertEqual((4, 4), self.generator.metre)
        self.assertEqual(4, self.generator.bar_count)

        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.start_note)
        self.assertEqual(Note('c', OctaveType.LINE_1), self.generator.end_note)
        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_4), self.generator.ambitus['highest'])
        self.assertEqual(0.5, self.generator.rest_probability)
        self.assertEqual(100, sum(self.generator.intervals_probability))

    # region get_available_note_lengths

    def test_get_available_note_lengths(self):
        actual = Generator.get_available_note_lengths()
        expected = [
            i for i in Generator.correct_note_lengths
            if Generator.shortest_note_duration / i <= Generator.shortest_note_duration and i <= Generator.shortest_note_duration
        ]

        self.assertEqual(expected, actual)

    def test_get_available_note_lengths_with_param(self):
        Generator.set_shortest_note_duration(16)
        actual = Generator.get_available_note_lengths(2)
        expected = [8, 16]

        self.assertEqual(expected, actual)

    # endregion

    # region Setters

    # region set_metre

    def test_set_metre(self):
        self.generator.set_metre(4, 4)
        self.assertEqual((4, 4), self.generator.metre)

    def test_invalid_metre(self):
        with self.assertRaises(errors.InvalidMetre):
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
        with self.assertRaises(errors.InvalidBaseNoteDuration):
            self.generator.set_shortest_note_duration(3)

    # endregion

    # region set_start_note

    def test_set_start_note(self):
        note = Note('c')
        self.generator.set_start_note(note)
        self.assertEqual(note, self.generator.start_note)

    def test_set_start_note_raises_note_outside_ambitus(self):
        note = Note('c', OctaveType.SUB_CONTRA)
        with self.assertRaises(errors.NoteOutsideAmbitus):
            self.generator.set_start_note(note)

    # endregion

    # region set_end_note

    def test_set_end_note(self):
        note = Note('c', OctaveType.LINE_2)
        self.generator.set_end_note(note)
        self.assertEqual(note, self.generator.end_note)

    def test_set_end_note_raises_note_outside_ambitus(self):
        note = Note('c', OctaveType.LINE_6)
        with self.assertRaises(errors.NoteOutsideAmbitus):
            self.generator.set_end_note(note)

    # endregion

    # region set_ambitus

    def test_set_ambitus_no_params(self):
        self.generator.set_ambitus()
        self.assertEqual(Note('c', OctaveType.SMALL), self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_4), self.generator.ambitus['highest'])

    def test_set_ambitus_lowest(self):
        note = Note('c')
        self.generator.set_ambitus(lowest=note)
        self.assertEqual(note, self.generator.ambitus['lowest'])
        self.assertEqual(Note('c', OctaveType.LINE_4), self.generator.ambitus['highest'])

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

    def test_set_ambitus_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.generator.set_ambitus(lowest=Note('c', OctaveType.LINE_6))

        with self.assertRaises(ValueError):
            self.generator.set_ambitus(highest=Note('c', OctaveType.SUB_CONTRA))

    # endregion

    # region set_rest_probability

    def test_set_rest_probability(self):
        self.generator.set_rest_probability(0.7)
        self.assertEqual(0.7, self.generator.rest_probability)

    def test_set_rest_probability_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.generator.set_rest_probability(1.5)

    # endregion

    # region set_max_consecutive_rests

    def test_set_max_consecutive_rests(self):
        self.generator.set_max_consecutive_rests(5)
        self.assertEqual(5, self.generator.max_consecutive_rests)

        self.generator.set_max_consecutive_rests(None)
        self.assertEqual(math.inf, self.generator.max_consecutive_rests)

        self.generator.set_max_consecutive_rests(3)
        self.assertEqual(3, self.generator.max_consecutive_rests)

    # endregion

    # region set_interval_probability

    def test_set_interval_probability(self):
        self.generator.set_interval_probability('1cz', 10)
        idx = Interval.names().index('1cz')
        self.assertEqual(10, self.generator.intervals_probability[idx])

    def test_set_invalid_interval_name(self):
        with self.assertRaises(errors.IntervalNotSupported):
            self.generator.set_interval_probability('1czz', 10)

    # endregion

    # region set_intervals_probability

    def test_set_intervals_probability(self):
        probabilities = [10, 5, 5, 10, 5, 5, 10, 10, 5, 5, 10, 10, 5, 5]

        self.generator.set_intervals_probability(probabilities)
        self.assertEqual(probabilities, self.generator.intervals_probability)

    def test_set_intervals_probability_invalid_length(self):
        probabilities = [0, 1, 2]

        with self.assertRaises(ValueError):
            self.generator.set_intervals_probability(probabilities)

    def test_set_intervals_probability_more_than_one_hundred(self):
        probabilities = [5 for _ in Interval.names()]

        with self.assertRaises(ValueError):
            self.generator.set_intervals_probability(probabilities)

    # endregion

    # region set_notes_probability

    def test_set_notes_probability(self):
        probabilities = [1, 1, 9, 9, 16, 8, 16, 8, 8, 8, 8, 8]

        self.generator.set_notes_probability(probabilities)
        self.assertEqual(probabilities, self.generator.notes_probability)

    def test_set_notes_probability_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.generator.set_notes_probability([100])

        with self.assertRaises(ValueError):
            self.generator.set_notes_probability([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    # endregion

    # region set_durations_probability

    def test_set_durations_probability(self):
        probabilities = [13, 13, 13, 20, 11, 10, 20]

        self.generator.set_durations_probability(probabilities)
        self.assertEqual(probabilities, self.generator.durations_probability)

    def test_set_durations_probability_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.generator.set_durations_probability([100])

        with self.assertRaises(ValueError):
            self.generator.set_durations_probability([1, 1, 1, 1, 1, 1, 1])

    # endregion

    # endregion

    # region Random generation

    # region get_random_note

    def test_random_correct_duration(self):
        self.generator.set_shortest_note_duration(16)

        for i in range(50):
            note = self.generator.get_random_note(16)
            self.assertGreaterEqual(note.get_duration(self.generator.shortest_note_duration), 1)

        for i in range(50):
            note = self.generator.get_random_note()
            self.assertGreaterEqual(note.get_duration(self.generator.shortest_note_duration), 1)

        for i in range(50):
            note = self.generator.get_random_note(1)
            self.assertEqual(note.get_duration(self.generator.shortest_note_duration), 1)

    # endregion

    # endregion

    # region Utility methods

    def test_get_next_writeable(self):
        self.generator.generated_data.append(Note('c'))

        for i in range(10):
            writeable = self.generator.get_next_writeable(8)
            self.assertLessEqual(writeable.get_duration(self.generator.shortest_note_duration), 8)

    def test_last_note_idx(self):
        self.generator.generated_data = [Rest(), Rest(), Note('c'), Rest()]
        idx = self.generator.get_last_note_idx()
        self.assertEqual(2, idx)

    def test_last_note_idx_raises(self):
        self.generator.generated_data = [Rest(), Rest(), Rest(), Rest()]
        with self.assertRaises(errors.NoNotesError):
            self.generator.get_last_note_idx()

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

    # region split_note

    def test_split_note(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=4)

        actual = self.generator.split_note(note, 2)
        expected = (
            [Note('c', base_duration=8, modifiers=[NoteModifier.TIE])],
            [Note('c', base_duration=8)]
        )

        self.assertEqual(expected, actual)

    def test_split_note_long(self):
        self.generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=1, modifiers=[NoteModifier.DOUBLE_DOT])

        actual = self.generator.split_note(note, 16)
        expected = (
            [Note('c', base_duration=1, modifiers=[NoteModifier.TIE])],
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT])]
        )

        self.assertEqual(expected, actual)

    def test_split_note_expects_dot(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=4)

        actual = self.generator.split_note(note, 3)
        expected = (
            [Note('c', base_duration=8, modifiers=[NoteModifier.DOT, NoteModifier.TIE])],
            [Note('c', base_duration=16)]
        )

        self.assertEqual(expected, actual)

    def test_split_note_expects_double_dot(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=2)

        actual = self.generator.split_note(note, 7)
        expected = (
            [Note('c', base_duration=4, modifiers=[NoteModifier.DOUBLE_DOT, NoteModifier.TIE])],
            [Note('c', base_duration=16)]
        )

        self.assertEqual(expected, actual)

    def test_split_note_multiple_notes_on_left_side(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=2)

        actual = self.generator.split_note(note, 5)
        expected = (
            [
                Note('c', base_duration=4, modifiers=[NoteModifier.TIE]),
                Note('c', base_duration=16, modifiers=[NoteModifier.TIE])
            ],
            [Note('c', base_duration=8, modifiers=[NoteModifier.DOT])]
        )

        self.assertEqual(expected, actual)

    def test_split_note_multiple_notes_on_right_side(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=2)

        actual = self.generator.split_note(note, 3)
        expected = (
            [Note('c', base_duration=8, modifiers=[NoteModifier.DOT, NoteModifier.TIE])],
            [
                Note('c', base_duration=4, modifiers=[NoteModifier.TIE]),
                Note('c', base_duration=16)
            ]
        )

        self.assertEqual(expected, actual)

    def test_split_note_expects_double_dot_and_note(self):
        Generator.set_shortest_note_duration(16)
        note = Note('c', base_duration=1)

        actual = self.generator.split_note(note, 15)
        expected = (
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOUBLE_DOT, NoteModifier.TIE]),
                Note('c', base_duration=16, modifiers=[NoteModifier.TIE])
            ],
            [Note('c', base_duration=16)]
        )
        self.assertEqual(expected, actual)

    def test_split_note_rests(self):
        Generator.set_shortest_note_duration(16)
        note = Rest(base_duration=2)

        actual = self.generator.split_note(note, 3)
        expected = (
            [Rest(base_duration=8, modifiers=[RestModifier.DOT])],
            [Rest(base_duration=4), Rest(base_duration=16)]
        )

        self.assertEqual(expected, actual)

    # endregion

    # region split_to_bars

    def test_split_to_bars(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)
        notes: List[Writeable] = [Note('c')] * 7
        notes.append(Rest())

        expected: List[List[Writeable]] = [
            [Note('c')] * 4,
            [Note('c'), Note('c'), Note('c'), Rest()]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(expected, bars)

    def test_split_to_bars_long(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)
        notes: List[Writeable] = [Note('c', base_duration=1, modifiers=[NoteModifier.DOUBLE_DOT]), Note('c')]

        expected: List[List[Writeable]] = [
            [Note('c', base_duration=1, modifiers=[NoteModifier.TIE])],
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT]), Note('c')]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(notes)

        self.assertEqual(expected, bars)

    def test_split_to_bars_break(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)
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

    def test_split_to_bars_break_rest(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)
        data: List[Writeable] = [
            Note('c'), Note('c', base_duration=2), Rest(base_duration=2),
            Note('c', base_duration=2), Rest()
        ]

        expected: List[List[Writeable]] = [
            [Note('c'), Note('c', base_duration=2), Rest()],
            [Rest(), Note('c', base_duration=2), Rest()]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(data)

        self.assertEqual(expected, bars)

    def test_split_to_bars_different_durations(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)
        data: List[Writeable] = [
            Note('c', base_duration=2), Note('d'), Note('e', base_duration=8), Note('f', base_duration=4),
            Note('c', base_duration=8), Rest(base_duration=2), Note('c', base_duration=4)
        ]

        with_tie = Note('f', base_duration=8)
        with_tie.add_modifier(NoteModifier.TIE)

        expected: List[List[Writeable]] = [
            [Note('c', base_duration=2), Note('d'), Note('e', base_duration=8), with_tie],
            [Note('f', base_duration=8), Note('c', base_duration=8), Rest(base_duration=2), Note('c')]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(data)
        self.assertEqual(expected, bars)

    def test_split_to_bars_with_dot(self):
        self.generator.set_bar_count(2)
        self.generator.set_shortest_note_duration(16)

        with_dot = Note('e', base_duration=4)
        with_dot.add_modifier(NoteModifier.DOT)

        data: List[Writeable] = [
            Note('c', base_duration=2), Note('d'), with_dot,
            Note('f', base_duration=8), Note('c', base_duration=2), Rest()
        ]

        with_tie = Note('e', base_duration=4)
        with_tie.add_modifier(NoteModifier.TIE)

        expected: List[List[Writeable]] = [
            [Note('c', base_duration=2), Note('d'), with_tie],
            [Note('e', base_duration=8), Note('f', base_duration=8), Note('c', base_duration=2), Rest()]
        ]

        bars: List[List[Writeable]] = self.generator.split_to_bars(data)
        self.assertEqual(expected, bars)

    def test_split_to_bars_long_note(self):
        self.generator.set_bar_count(3)

        data: List[Writeable] = [
            Rest(base_duration=2, modifiers=[RestModifier.DOT]),
            Note('c', base_duration=1, modifiers=[NoteModifier.DOT]),
            Rest(base_duration=2, modifiers=[RestModifier.DOT])
        ]
        expected: List[List[Writeable]] = [
            [
                Rest(base_duration=2, modifiers=[RestModifier.DOT]),
                Note('c', base_duration=4, modifiers=[NoteModifier.TIE])
            ],
            [Note('c', base_duration=1, modifiers=[NoteModifier.TIE])],
            [Note('c', base_duration=4), Rest(base_duration=2, modifiers=[RestModifier.DOT])]
        ]

        bars = self.generator.split_to_bars(data)
        self.assertEqual(expected, bars)

    # endregion

    # region group_bars

    def test_group_bars_4_4(self):
        self.generator.set_metre(4, 4)
        self.generator.set_shortest_note_duration(16)

        bars: List[List[Writeable]] = [
            [Note('c', base_duration=1)],
            [Note('c'), Note('c', base_duration=2), Note('c')],
            [Note('c', base_duration=2), Note('c', base_duration=2)],
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT]), Note('c')],
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOUBLE_DOT]), Note('c', base_duration=8)],
            [Note('c'), Note('c', base_duration=8), Note('c', modifiers=[NoteModifier.DOT]), Note('c')],
            [
                Rest(base_duration=8), Note('c', base_duration=8, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=16), Note('c', base_duration=16),
                Note('c', base_duration=8, modifiers=[NoteModifier.DOT]),
                Rest(base_duration=4, modifiers=[RestModifier.DOT])
            ]
        ]

        expected: List[List[Writeable]] = [
            [Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), Note('c', base_duration=2)],
            [Note('c'), Note('c', modifiers=[NoteModifier.TIE]), Note('c'), Note('c')],
            [Note('c', base_duration=2), Note('c', base_duration=2)],
            [Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), Note('c'), Note('c')],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), 
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', base_duration=8)
            ],
            [
                Note('c'), Note('c', base_duration=8), Note('c', base_duration=8, modifiers=[NoteModifier.TIE]),
                Note('c'), Note('c')
            ],
            [
                Rest(base_duration=8), Note('c', base_duration=8, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=16), Note('c', base_duration=16),
                Note('c', base_duration=16, modifiers=[NoteModifier.TIE]), Note('c', base_duration=8),
                Rest(base_duration=4, modifiers=[RestModifier.DOT])
            ]
        ]

        grouped_bars = self.generator.group_bars(bars)
        self.assertEqual(expected, grouped_bars)

    def test_group_bars_5_4(self):
        self.generator.set_metre(5, 4)
        self.generator.set_shortest_note_duration(16)

        # Przyjmujemy założenie że 5/4 jest grupowane w sposób 3/4 + 2/4
        bars: List[List[Writeable]] = [
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT]), Note('c', base_duration=2)],
            [Note('c', base_duration=1), Note('c')],
            [Note('c', base_duration=2), Note('c', base_duration=2), Note('c')]
        ]

        expected: List[List[Writeable]] = [
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT]), Note('c', base_duration=2)],
            [Note('c', base_duration=2, modifiers=[NoteModifier.DOT, NoteModifier.TIE]), Note('c'), Note('c')],
            [Note('c', base_duration=2), Note('c', modifiers=[NoteModifier.TIE]), Note('c'), Note('c')]
        ]

        grouped_bars = self.generator.group_bars(bars)
        self.assertEqual(expected, grouped_bars)

    def test_group_bars_6_4(self):
        self.generator.set_metre(6, 4)
        self.generator.set_shortest_note_duration(16)

        bars: List[List[Writeable]] = [
            [Note('c', base_duration=2), Note('c', base_duration=2), Note('c', base_duration=2)],
            [Note('c', base_duration=1), Note('c', base_duration=2)],
            [
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', modifiers=[NoteModifier.DOT]),
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', modifiers=[NoteModifier.DOT])
            ],
            [
                Note('c'), Note('c', base_duration=2, modifiers=[NoteModifier.DOUBLE_DOT]), Note('c', base_duration=8),
                Note('c')
            ]
        ]

        expected: List[List[Writeable]] = [
            [
                Note('c', base_duration=2), Note('c', modifiers=[NoteModifier.TIE]), Note('c'),
                Note('c', base_duration=2)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT, NoteModifier.TIE]), Note('c'),
                Note('c', base_duration=2)
            ],
            [
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', modifiers=[NoteModifier.DOT]),
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', modifiers=[NoteModifier.DOT])
            ],
            [
                Note('c'), Note('c', base_duration=2, modifiers=[NoteModifier.TIE]),
                Note('c', modifiers=[NoteModifier.DOT]), Note('c', base_duration=8), Note('c')
            ]
        ]

        grouped_bars = self.generator.group_bars(bars)
        self.assertEqual(expected, grouped_bars)

    def test_group_bars_7_4(self):
        self.generator.set_metre(7, 4)
        self.generator.set_shortest_note_duration(16)

        # Przyjmujemy założenie że 7/4 jest grupowane w sposób 3/4 + 2/4 + 2/4 = 3/4 + 4/4
        bars: List[List[Writeable]] = [
            [Note('c', base_duration=1), Note('c'), Note('c'), Note('c')],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=1)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c'), Note('c', base_duration=2), Note('c')
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2), Note('c', base_duration=2)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]), Note('c')
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2, modifiers=[NoteModifier.DOUBLE_DOT]), Note('c', base_duration=8)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c'), Note('c', base_duration=8), Note('c', modifiers=[NoteModifier.DOT]), Note('c')
            ]
        ]

        expected: List[List[Writeable]] = [
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT, NoteModifier.TIE]),
                Note('c'), Note('c'), Note('c'), Note('c')
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), Note('c', base_duration=2)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c'), Note('c', modifiers=[NoteModifier.TIE]), Note('c'), Note('c')
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2), Note('c', base_duration=2)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), Note('c'), Note('c')
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=2, modifiers=[NoteModifier.TIE]), Note('c', modifiers=[NoteModifier.DOT]),
                Note('c', base_duration=8)
            ],
            [
                Note('c', base_duration=2, modifiers=[NoteModifier.DOT]),
                Note('c'), Note('c', base_duration=8), Note('c', base_duration=8, modifiers=[NoteModifier.TIE]),
                Note('c'), Note('c')
            ]
        ]

        grouped_bars = self.generator.group_bars(bars)
        self.assertEqual(expected, grouped_bars)

    # endregion

    # region generate

    def test_generate(self):
        for _ in range(50):
            data: List[Writeable] = self.generator.generate()

            first_note = data[0]
            last_note = data[self.generator.get_last_note_idx()]

            if isinstance(first_note, Note) and isinstance(last_note, Note):
                # Check start and end note
                self.assertEqual(self.generator.start_note.note, first_note.note)
                self.assertEqual(self.generator.start_note.octave, first_note.octave)

                self.assertEqual(self.generator.end_note.note, last_note.note)
                self.assertEqual(self.generator.end_note.octave, last_note.octave)
            else:
                raise TypeError

            # Sprawdzenie długości każdej nuty
            expected_length = self.generator.get_length_to_fill()
            actual_length = sum([item.get_duration(self.generator.shortest_note_duration) for item in data])
            self.assertEqual(expected_length, actual_length)

            # Sprawdzenie czy nuty mieszczą się w ambitusie.
            notes = [item for item in data if isinstance(item, Note)]
            for idx, note in enumerate(notes):
                self.assertTrue(note <= self.generator.ambitus['highest'])
                self.assertTrue(note >= self.generator.ambitus['lowest'])

    def test_generate_group(self):
        data: List[List[Writeable]] = self.generator.generate(group=True)

        expected_bar_length = self.generator.get_length_to_fill() / self.generator.bar_count
        for bar in data:
            actual_length = sum([item.get_duration(self.generator.shortest_note_duration) for item in bar])
            self.assertEqual(expected_bar_length, actual_length)

    # endregion


if __name__ == "__main__":
    unittest.main()
