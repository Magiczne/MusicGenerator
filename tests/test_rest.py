import unittest

from lib.Rest import Rest
from lib.RestModifier import RestModifier


class RestTests(unittest.TestCase):

    def test_init(self):
        rest = Rest(base_duration=8)
        self.assertEqual(8, rest.base_duration)
        self.assertEqual([], rest.modifiers)

    def test_init_invalid_duration(self):
        with self.assertRaises(ValueError):
            Rest(base_duration=5)

    def test_eq(self):
        rest = Rest(base_duration=8)
        rest2 = Rest(base_duration=8)
        self.assertEqual(rest, rest2)

    def test_str(self):
        rest = Rest(base_duration=8)
        self.assertEqual('r8', str(rest))

    def test_str_with_modifiers(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOUBLE_DOT)
        self.assertEqual('r4..', str(rest))

    def test_repr(self):
        rest = Rest()
        self.assertEqual('Rest <r4>', repr(rest))

    def test_get_duration(self):
        rest = Rest()
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4, rest.get_duration(length))

    def test_get_duration_with_dot(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8, rest.get_duration(length))

    def test_get_duration_with_double_dot(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOUBLE_DOT)
        lengths = [64, 32, 16, 8, 4, 2, 1]

        for length in lengths:
            self.assertEqual(length / 4 + length / 8 + length / 16, rest.get_duration(length))

    def test_add_remove_modifier(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOT)
        self.assertTrue(RestModifier.DOT in rest.modifiers)

        rest.remove_modifier(RestModifier.DOT)
        self.assertTrue(RestModifier.DOT not in rest.modifiers)

    def test_add_modifier_unique(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOT)
        rest.add_modifier(RestModifier.DOT)

        self.assertEqual(1, len(rest.modifiers))

    def test_add_modifier_double_dot_priority_over_dot(self):
        rest = Rest()
        rest.add_modifier(RestModifier.DOT)
        rest.add_modifier(RestModifier.DOUBLE_DOT)

        self.assertTrue(RestModifier.DOUBLE_DOT in rest.modifiers)
        self.assertTrue(RestModifier.DOT not in rest.modifiers)


if __name__ == '__main__':
    unittest.main()
