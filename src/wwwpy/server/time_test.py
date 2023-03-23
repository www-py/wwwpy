import unittest
from datetime import date

from .time import first_day_next_month


class MyTestCase(unittest.TestCase):

    def test_1(self):
        target = first_day_next_month(today=date(2023, 1, 4))
        self.assertEqual(target, date(2023, 2, 1))

    def test_2(self):
        target = first_day_next_month(today=date(2022, 12, 5))
        self.assertEqual(target, date(2023, 1, 1))

    def test_3(self):
        target = first_day_next_month(today=date(2023, 1, 1))
        self.assertEqual(target, date(2023, 2, 1))

    def test_4(self):
        target = first_day_next_month(today=date(2023, 2, 1))
        self.assertEqual(target, date(2023, 3, 1))

    def test_5(self):
        target = first_day_next_month(today=date(2023, 2, 28))
        self.assertEqual(target, date(2023, 3, 1))


if __name__ == '__main__':
    unittest.main()
