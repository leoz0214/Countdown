import unittest
import sys
import random
import time

sys.path.extend((".", "./src"))

from src.mechanics import stats
from src import end
from src import game
from src.mechanics import history
from src.utils.io import reset_data
from src.utils.utils import days_to_seconds
from src.mechanics import achievements
from src.mechanics.options import get_options, set_options


class TestData(unittest.TestCase):

    def test_win_streak(self):
        reset_data()
        for count in range(20):
            for _ in range(count):
                stats.increment_win_streak()
            self.assertEqual(stats.get_win_streak(), count)
            stats.reset_win_streak()
        self.assertEqual(stats.get_best_win_streak(), 0)
        reset_data()
    
    def test_xp(self):
        reset_data()
        i = random.randint(1, 100)
        for xp in range(1, i + 1):
            stats.add_total_xp(xp)
        self.assertEqual(stats.get_total_xp(), (i**2 + i)/2)
        stats.add_total_xp(-10**1000)
        self.assertEqual(stats.get_total_xp(), 0)
        reset_data()
    
    def test_seconds_played(self):
        reset_data()
        to_add = [
            random.random() * 10. ** random.randint(0, 10) for _ in range(100)]
        for add in to_add:
            stats.add_seconds_played(add)
        self.assertEqual(stats.get_seconds_played(), sum(to_add))
        stats.add_seconds_played(-10 ** 100.)
        self.assertEqual(stats.get_total_xp(), 0)
        reset_data()
    
    def test_operators_used(self):
        reset_data()
        to_add = [
            {op: random.randint(1, 1000) for op in stats.OPERATORS}
            for _ in range(random.randint(10, 50))]
        for add in to_add:
            stats.add_operators_used(add)
        for operator, count in stats.get_operators_used().items():
            self.assertEqual(count, sum(add[operator] for add in to_add))
        stats.add_operators_used({"+": 0.5})
        self.assertEqual(
            stats.get_operators_used(), {op: 0 for op in stats.OPERATORS})
        reset_data()
    
    def test_recent_numbers(self):
        reset_data()
        numbers = [random.randint(201, 999) for _ in range(100)]
        for number in numbers:
            game.add_recent_number(number)
        self.assertEqual(
            numbers[-game.MAX_RECENT_NUMBERS_COUNT:],
            game.get_recent_numbers()[::-1])
        game.add_recent_number(645.234)
        self.assertEqual(game.get_recent_numbers(), [])
        reset_data()
    
    def test_game_data(self):
        reset_data()
        for _ in range(10):
            current_time = time.time()
            total_count = random.randint(1, 2000)
            new_count = random.randint(1, total_count)
            for i in range(total_count - new_count):
                end.GameData([1,2,3,4,5,6,7], 250, "1+2+3", i, i + 30).save()
            for i in range(new_count):
                end.GameData(
                    [1,2,3,4,5,6,7], 332, "10x10",
                    current_time - (i / new_count) * days_to_seconds(30),
                    current_time - (i / new_count) * days_to_seconds(30) + 30
                ).save()
            self.assertEqual(
                len(history.get_game_data()),
                max(1000, new_count) if total_count >= 1000 else total_count)
            reset_data()
    
    def test_special_achievements(self):
        reset_data()
        for achievement in achievements.get_special_achievements():
            achievements.complete_special_achievement(achievement)
        self.assertEqual(len(set(achievements.get_special_achievements().values())), 1)
        reset_data()
    
    def test_options(self):
        reset_data()
        options = start = get_options()
        options["music"]["on"] = random.choice((True, False))
        options["music"]["countdown"] = "cancan.wav"
        options["sfx"] = random.choice((True, False))
        options["stats"] = random.choice((True, False))
        options["auto_generate"]["on"] = random.choice((True, False))
        options["auto_generate"]["min_small"] = random.randint(2, 5)
        options["solution_time_limit"]["on"] = random.choice((True, False))
        options["solution_time_limit"]["minutes"] = random.randint(1, 5)
        set_options(options)
        self.assertEqual(get_options(), options)
        options["music"]["countdown"] = "DOESNOTEXIST"*100000
        set_options(options)
        self.assertEqual(get_options(), start)
        reset_data()


if __name__ == "__main__":
    unittest.main()