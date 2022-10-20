import itertools
import secrets
import ctypes
import os
from timeit import default_timer as timer

import data


genlib = ctypes.cdll.LoadLibrary(
    f"{os.path.dirname(os.path.abspath(__file__))}/generate.so")
genlib.generate_number.restype = ctypes.c_int
genlib.get_solution.restype = ctypes.c_char_p


class SolutionGenerationSettings:
    """
    Holds the settings of what types of solutions are generated
    and the maximum time limit allocated.
    """

    def __init__(
        self, min_number_count: int, max_number_count: int,
        max_solution_count: int, nested_parentheses: bool | None,
        operators: str, seconds_limit: int) -> None:

        self.min_number_count = min_number_count
        self.max_number_count = max_number_count
        self.max_solution_count = max_solution_count
        self.parentheses_option = (
            nested_parentheses if nested_parentheses is not None else -1)
        self.operators = operators
        self.seconds_limit = seconds_limit
        # In case generation is aborted.
        self.cancel = False


def generate_number(numbers: list[int]) -> int:
    """
    Gets a random suitable number
    from 201-999 for the player to try and get.
    """
    recent = data.get_recent_numbers()
    result = genlib.generate_number(
        (ctypes.c_int * 7)(*numbers),
        (ctypes.c_int * len(recent))(*recent), len(recent))
    data.add_recent_number(result)
    return result


def generate_solutions(
    numbers: list[int], target: int,
    settings: SolutionGenerationSettings) -> list[str]:
    """
    Gets solutions for a given target number with particular smaller
    numbers based on certain settings.
    """
    if not settings.operators:
        return []
    start = timer()
    solutions = []
    # Uniform probability for n numbers.
    perms = [
        list(itertools.permutations(numbers, count))
        for count in range(
            settings.min_number_count, settings.max_number_count + 1)]
    operators = ctypes.c_char_p(settings.operators.encode())
    
    while (
        timer() - start < settings.seconds_limit
        and perms and len(solutions) < settings.max_solution_count
    ):
        count_choice = secrets.choice(perms)
        choice = secrets.choice(count_choice)
        perms[perms.index(count_choice)].remove(choice)

        while [] in perms:
            perms.remove([])

        result = genlib.get_solution(
            (ctypes.c_int * len(choice))(*choice), len(choice), target,
            operators, settings.parentheses_option).decode()
        if result:
            result = result.replace("*", "x").replace("/", "÷")
            solutions.append(result)
        
        if settings.cancel:
            return []
                
    return solutions if not settings.cancel else []