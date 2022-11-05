import unittest
import sys
import random
import time

sys.path.extend((".", "./src"))

from src import data
from src import end


class TestData(unittest.TestCase):

    def test_win_streak(self):
        data.reset_data()
        for count in range(20):
            for _ in range(count):
                data.increment_win_streak()
            self.assertEqual(data.get_win_streak(), count)
            data.reset_win_streak()
        self.assertEqual(data.get_best_win_streak(), 0)
        data.reset_data()
    
    def test_xp(self):
        data.reset_data()
        i = random.randint(1, 100)
        for xp in range(1, i + 1):
            data.add_total_xp(xp)
        self.assertEqual(data.get_total_xp(), (i**2 + i)/2)
        data.add_total_xp(-10**1000)
        self.assertEqual(data.get_total_xp(), 0)
        data.reset_data()
    
    def test_seconds_played(self):
        data.reset_data()
        to_add = [
            random.random() * 10. ** random.randint(0, 10) for _ in range(100)]
        for add in to_add:
            data.add_seconds_played(add)
        self.assertEqual(data.get_seconds_played(), sum(to_add))
        data.add_seconds_played(-10 ** 100.)
        self.assertEqual(data.get_total_xp(), 0)
        data.reset_data()
    
    def test_operators_used(self):
        data.reset_data()
        to_add = [
            {op: random.randint(1, 1000) for op in data.OPERATORS}
            for _ in range(random.randint(10, 50))]
        for add in to_add:
            data.add_operators_used(add)
        for operator, count in data.get_operators_used().items():
            self.assertEqual(count, sum(add[operator] for add in to_add))
        data.add_operators_used({"+": 0.5})
        self.assertEqual(
            data.get_operators_used(), {op: 0 for op in data.OPERATORS})
        data.reset_data()
    
    def test_recent_numbers(self):
        data.reset_data()
        numbers = [random.randint(201, 999) for _ in range(100)]
        for number in numbers:
            data.add_recent_number(number)
        self.assertEqual(
            numbers[-data.MAX_RECENT_NUMBERS_COUNT:],
            data.get_recent_numbers()[::-1])
        data.add_recent_number(645.234)
        self.assertEqual(data.get_recent_numbers(), [])
        data.reset_data()
    
    def test_game_data(self):
        data.reset_data()
        for _ in range(10):
            current_time = time.time()
            total_count = random.randint(1, 2000)
            new_count = random.randint(1, total_count)
            for i in range(total_count - new_count):
                end.GameData([1,2,3,4,5,6,7], 250, "1+2+3", i, i + 30).save()
            for i in range(new_count):
                end.GameData(
                    [1,2,3,4,5,6,7], 332, "10x10",
                    current_time - (i / new_count) * data.SECONDS_IN_30_DAYS,
                    current_time - (i / new_count) * data.SECONDS_IN_30_DAYS + 30
                ).save()
            self.assertEqual(
                len(data.get_game_data()),
                max(1000, new_count) if total_count >= 1000 else total_count)
            data.reset_data()
    
    def test_special_achievements(self):
        data.reset_data()
        for achievement in data.get_special_achievements():
            data.complete_special_achievement(achievement)
        self.assertEqual(len(set(data.get_special_achievements().values())), 1)
        data.reset_data()
    
    def test_options(self):
        data.reset_data()
        options = start = data.get_options()
        options["music"]["on"] = random.choice((True, False))
        options["music"]["countdown"] = "cancan.wav"
        options["sfx"] = random.choice((True, False))
        options["stats"] = random.choice((True, False))
        options["auto_generate"]["on"] = random.choice((True, False))
        options["auto_generate"]["min_small"] = random.randint(2, 5)
        options["solution_time_limit"]["on"] = random.choice((True, False))
        options["solution_time_limit"]["minutes"] = random.randint(1, 5)
        data.set_options(options)
        self.assertEqual(data.get_options(), options)
        options["music"]["countdown"] = "DOESNOTEXIST"*100000
        data.set_options(options)
        self.assertEqual(data.get_options(), start)
        data.reset_data()


if __name__ == "__main__":
    unittest.main()