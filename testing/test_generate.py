import unittest
import shutil
import sys
import secrets
from contextlib import suppress

sys.path.extend((".", "./src"))

from src import generate


class TestGenerate(unittest.TestCase):

    def test_generate_number(self):
        with suppress(FileNotFoundError):
            shutil.rmtree("./data")

        possible_small_numbers = list(range(2, 10))
        possible_big_numbers = [25, 50, 75, 100] * 2

        small_number_count = secrets.choice(range(2, 6))
        big_number_count = 7 - small_number_count

        numbers = []
        for possible in (possible_small_numbers, possible_big_numbers):
            for _ in range(
                small_number_count if possible == possible_small_numbers
                else big_number_count
            ):
                number = secrets.choice(possible)
                numbers.append(number)
                possible.remove(number)

        for _ in range(30):
            number = generate.generate_number(numbers)
            self.assertTrue(201 <= number <= 999 and isinstance(number, int))

        shutil.rmtree("./data")


if __name__ == "__main__":
    unittest.main()