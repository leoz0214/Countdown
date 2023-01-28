import unittest
import sys
import math

sys.path.extend((".", "./src"))

from src.utils import utils


class TestUtils(unittest.TestCase):

    def test_evaluate(self):
        expressions_and_answers = (
            ("1+1", 2),
            ("6-3", 3),
            ("5*7", 35),
            ("25/5", 5),
            ("5", 5),
            ("592-988", -396),
            ("1+2*3/4+5", 7.5),
            ("6-5-4", -3),
            ("(3+8)*5", 55),
            ("(2-6)/5", -0.8),
            ("100/(3+5)", 12.5),
            ("0/0", float("nan")),
            ("0*0+0-0", 0),
            ("(1+2)*(3-4)", -3),
            ("(5-6)/(5*(3+2))", -0.04),
            ("(666*666)/(555/555-1)", float("nan")),
            ("((((((((((1+1))))))))))", 2)
        )
        for expression, answer in expressions_and_answers:
            value = utils.evaluate(expression)
            self.assertTrue(
                value == answer
                or (math.isnan(value) and math.isnan(answer)),
                f"{expression} != {answer}"
            )
    
    def test_seconds_to_hhmmss(self):
        seconds_and_hhmmss = (
            (0, "00:00:00"),
            (23, "00:00:23"),
            (60, "00:01:00"),
            (181, "00:03:01"),
            (3899, "01:04:59"),
            (1072 * 3600 + 52 * 60 + 41, "1072:52:41")
        )
        for seconds, hhmmss in seconds_and_hhmmss:
            self.assertEqual(utils.seconds_to_hhmmss(seconds), hhmmss)


if __name__ == "__main__":
    unittest.main()