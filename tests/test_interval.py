import unittest

from lib.theory.Interval import Interval


class IntervalTests(unittest.TestCase):
    def test_init(self):
        interval = Interval('4zw')
        self.assertEqual('4zw', interval.name)
        self.assertEqual(4, interval.degrees)
        self.assertEqual('zw', interval.quality)

    def test_init_invalid_interval(self):
        with self.assertRaises(KeyError):
            Interval('4b')

    def test_str(self):
        interval = Interval('4zw')
        self.assertEqual('4zw', str(interval))

    def test_repr(self):
        interval = Interval('4zw')
        self.assertEqual('Interval <4zw>', repr(interval))

    def test_get_complement_interval(self):
        intervals = Interval.names()
        expected = Interval.names()
        expected.reverse()

        for i in range(len(intervals)):
            interval = Interval(intervals[i])
            complement = interval.get_complement_interval()
            self.assertEqual(expected[i], complement.name)


if __name__ == "__main__":
    unittest.main()
