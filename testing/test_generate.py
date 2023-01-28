import unittest
import sys
import secrets

sys.path.extend((".", "./src"))

from src.mechanics import solutions
from src import game
from src.utils.io import reset_data


def generate_numbers():
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
    return numbers


class TestGenerate(unittest.TestCase):

    def test_generate_number(self):
        reset_data()
        numbers = generate_numbers()
        for _ in range(30):
            number = game.generate_number(numbers)
            self.assertTrue(201 <= number <= 999 and isinstance(number, int))
        reset_data()
    
    def test_generate_solutions(self):
        numbers = generate_numbers()
        target = game.generate_number(numbers)

        settings = solutions.SolutionGenerationSettings(
            4, 4, 1, True, "+-*/", float("inf"))
        result = solutions.generate_solutions(numbers, target, settings)
        self.assertEqual(len(result), 1)
        for r in result:
            self.assertEqual(round(
                eval(r.replace("x", "*").replace("÷", "/")), 10), target)

        settings = solutions.SolutionGenerationSettings(
            4, 4, 1, False, "+-*", float("inf"))
        result = solutions.generate_solutions(numbers, target, settings)
        self.assertEqual(len(result), 1)
        for r in result:
            self.assertEqual(round(
                eval(r.replace("x", "*").replace("÷", "/")), 10), target)
    
        settings = solutions.SolutionGenerationSettings(
            4, 7, 25, False, "+-*/", float("inf"))
        result = solutions.generate_solutions(numbers, target, settings)
        self.assertEqual(len(result), 25)
        for r in result:
            self.assertEqual(round(
                eval(r.replace("x", "*").replace("÷", "/")), 10), target)

        settings = solutions.SolutionGenerationSettings(
            4, 7, 0, True, "+-*/", 3)
        result = solutions.generate_solutions(numbers, target, settings)
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()