import unittest
import lib


class IntervalTests(unittest.TestCase):
    def test_init(self):
        interval = lib.Interval('4zw')
        self.assertEqual('4zw', interval.name)
        self.assertEqual(4, interval.degrees)
        self.assertEqual('zw', interval.quality)

    def test_init_invalid_interval(self):
        with self.assertRaises(KeyError):
            lib.Interval('4b')

    def test_str(self):
        interval = lib.Interval('4zw')
        self.assertEqual('4zw', str(interval))

    def test_repr(self):
        interval = lib.Interval('4zw')
        self.assertEqual('Interval <4zw>', repr(interval))

    def test_get_complement_interval(self):
        intervals = lib.Interval.names()
        expected = lib.Interval.names()
        expected.reverse()

        for i in range(len(intervals)):
            interval = lib.Interval(intervals[i])
            complement = interval.get_complement_interval()
            self.assertEqual(expected[i], complement.name)
