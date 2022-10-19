import itertools
import secrets
from timeit import default_timer as timer
import ctypes
import os

import data
from utils import evaluate


genlib = ctypes.cdll.LoadLibrary(
    f"{os.path.dirname(os.path.abspath(__file__))}/generate.so")
genlib.generate_number.restype = ctypes.c_int


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
        self.parentheses = nested_parentheses is not None
        self.nested_parentheses = bool(nested_parentheses)
        self.operators = operators
        self.seconds_limit = seconds_limit
        # In case generation is aborted.
        self.cancel = False


def get_starting_positions(numbers: list[int]) -> tuple[list]:
    """
    Gets starting number and operator indexes, along with the
    initial parts of the expression when no parentheses have been added.
    """
    start_number_indexes = list(range(0, (len(numbers) + 1) * 2, 2))
    start_operator_indexes = list(range(1, len(numbers) * 2, 2))
    start = []
    for number in numbers[:-1]:
        start.append(str(number))
        # Placeholder for an operator.
        start.append("")
    start.append(str(numbers[-1]))
    return start, start_number_indexes, start_operator_indexes


def check_to_evaluate(operators: tuple[str], parts: list[str]) -> bool:
    """
    Checks if there is any need to evaluate an expression
    with parentheses, as evaluation is expensive in terms of time
    and duplicate solutions are unwanted, so:
    - There is multiplication or division; and
    - All of the parentheses change evaluation

    Especially important for a large number of expression parts.
    """
    if "*" not in operators and "/" not in operators:
        # No point in evaluating only +/- with any parentheses.
        return False
    elif "+" not in operators and "-" not in operators:
        # No point in evaluating only x or / with any parentheses.
        return False
    # If any parentheses do not change evaluation, skip.
    opened = 0
    has_add_or_subtract = []
    # If "+/-" both before and after parentheses expression,
    # the parentheses are obviously not needed, so return False.
    # E.g. 1 * ((2 + 3) + 4) is False as the parentheses around
    # 2 + 3 are unnecessary.
    # Also if ( or nothing is before the target ( and
    # ) is followed by +/-, False is still returned, and vice versa.
    before_opening_parenthesis = []
    operator_index = 0
    for i, part in enumerate(parts):
        if part == "(":
            # New set of parentheses opened.
            opened += 1
            # Assume otherwise until confirmed
            has_add_or_subtract.append(False)
            before_opening_parenthesis.append(
                not i or parts[i-1] == "("
                or operators[operator_index - 1] in "+-")
        elif opened:
            if part == ")":
                # Parentheses are closing
                if not has_add_or_subtract.pop():
                    return False
                if before_opening_parenthesis.pop() and (
                    i + 1 >= len(parts) or parts[i+1] == ")"
                    or operators[operator_index] in "+-"
                ):
                    return False
                opened -= 1
            elif not part.isdigit():
                if operators[operator_index] in "+-":
                    has_add_or_subtract[-1] = True
                operator_index += 1
        elif not part.isdigit():
            # Increment to next operator.
            operator_index += 1

    return True


def get_solution(
    numbers: list[int], target: int,
    parentheses_positions: list[list[tuple]],
    settings: SolutionGenerationSettings, seconds_start: float) -> str | None:
    """
    Attempts to find a solution for given numbers
    in that particular order along with the target number,
    parentheses positions and operators which can be used.
    """
    start, start_number_indexes, start_operator_indexes = (
        get_starting_positions(numbers))
    
    # Further randomisation - start from a random product of operators.
    operators_product = tuple(itertools.product(
        settings.operators, repeat=len(numbers) - 1))
    shift = secrets.choice(range(0, len(operators_product)))
    operators_product = operators_product[shift:] + operators_product[:shift]
    
    for operators in operators_product:
        if (
            timer() - seconds_start > settings.seconds_limit
            or settings.cancel
        ):
            return
        for i, operator in zip(start_operator_indexes, operators):
            start[i] = operator
        expression = "".join(start)
        if evaluate(expression) == target:
            return expression

    for positions in parentheses_positions:
        current = [*start]
        number_indexes = [*start_number_indexes]
        operator_indexes = [*start_operator_indexes]

        for p in positions:
            if (
                timer() - seconds_start > settings.seconds_limit
                or settings.cancel
            ):
                return
            result = add_parentheses(
                p, current, number_indexes, operator_indexes, len(numbers),
                target, operators_product)
            if result:
                return result

        for operators in operators_product:
            if not check_to_evaluate(operators, current):
                continue
            for i, operator in zip(operator_indexes, operators):
                current[i] = operator
            expression = "".join(current)
            if evaluate(expression) == target:
                return expression


def add_parentheses(
    to_add: tuple, current: list[str],
    number_indexes: list[int], operator_indexes: list[int],
    number_count: int, target: int, operators_product: tuple[tuple]) -> str:
    """
    Adds required parentheses to an expression.
    Handles nested parentheses recursively.
    """
    start = to_add[0]
    stop = to_add[1]

    # Opening parentheses
    current.insert(number_indexes[start], "(")
    # Shift indexes to the right.
    for i in range(start, len(number_indexes)):
        number_indexes[i] += 1
    for i in range(start, len(operator_indexes)):
        operator_indexes[i] += 1

    # Closing parentheses.
    current.insert(number_indexes[stop] - 1, ")")
    # Shift indexes to the right again.
    for i in range(stop, len(number_indexes)):
        number_indexes[i] += 1
    for i in range(stop - 1, len(operator_indexes)):
        operator_indexes[i] += 1
    
    if len(to_add) == 3:
        # Nested parentheses
        for positions in to_add[2]:
            deeper_current = [*current]
            deeper_number_indexes = [*number_indexes]
            deeper_operator_indexes = [*operator_indexes]

            for p in positions:
                add = (p[0] + start, p[1] + start)
                if len(p) == 3:
                    add = (p[0] + start, p[1] + start, p[2])

                result = add_parentheses(
                    add, deeper_current, deeper_number_indexes,
                    deeper_operator_indexes, number_count,
                    target, operators_product)
                if result:
                    return result

            for operators in operators_product:
                if not check_to_evaluate(operators, deeper_current):
                    continue
                for i, operator in zip(deeper_operator_indexes, operators):
                    deeper_current[i] = operator

                expression = "".join(deeper_current)
                if evaluate(expression) == target:
                    return expression


def generate_parentheses_positions(
    number_count: int, nested: bool = False) -> list[list[tuple]]:
    """
    Gets simple possible parentheses positions for n numbers.
    This is in the form of a list of lists of 2 or 3-tuples, with
    the 1st number indicating the position of the opening parenthesis,
    and the latter indicating the position of the closing parenthesis.
    If a tuple is of length 3, the third element contains nested
    parentheses.
    """
    positions = []
    for size in range(number_count - 1, 1, -1):
        # size = number of numbers in parentheses
        for i in range(number_count - size + 1):
            positions.append([(i, i + size)])
            if number_count - (i + size) >= 2:
                positions.append([(i, i + size), (i + size, number_count)])
                # Multiple parentheses in one expression is possible.
                for pos in generate_parentheses_positions(
                    number_count - (i + size), nested
                ):
                    new = [(i, i + size)]
                    for p in pos:
                        new.append((p[0] + i + size, p[1] + i + size))
                    positions.append(new)
    
    if nested:
        for i, combination in tuple(enumerate(positions)):
            # Using pre-computed length iteration to allow for appended
            # recursive parentheses positions.
            new_combo = []
            for j in range(len(combination)):
                p = combination[j]
                if p[1] - p[0] >= 3:
                    new = (
                        p[0], p[1],
                        generate_parentheses_positions(p[1] - p[0], True))
                    new_combo.append(new)
            if new_combo:
                positions.append(new_combo)

    return positions


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
    parentheses_positions = {
        count: generate_parentheses_positions(
            count, settings.nested_parentheses)
            if settings.parentheses else []
        for count in range(
            settings.min_number_count, settings.max_number_count + 1)
    }
    # Uniform probability for n numbers.
    perms = [
        list(itertools.permutations(numbers, count))
        for count in range(
            settings.min_number_count, settings.max_number_count + 1)]
    
    while (
        timer() - start < settings.seconds_limit
        and perms and len(solutions) < settings.max_solution_count
    ):
        count_choice = secrets.choice(perms)
        choice = secrets.choice(count_choice)
        perms[perms.index(count_choice)].remove(choice)

        while [] in perms:
            perms.remove([])

        result = get_solution(
            choice, target, parentheses_positions[len(choice)],
            settings, start)
        if result is not None:
            result = result.replace("*", "x").replace("/", "÷")
            solutions.append(result)
        
        if settings.cancel:
            return []
            
    return solutions if not settings.cancel else []