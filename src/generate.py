import itertools
import secrets

import data


def get_too_easy(numbers: list[int]) -> set[int]:
    """
    A number is too easy to get if it is possible to get with
    3 or less smaller numbers. Easy numbers will not be generated.
    """
    too_easy = set()
    for count in range(2, 4):
        parentheses_positions = generate_parentheses_positions(count)
        for perm in itertools.permutations(numbers, count):
            add(perm, parentheses_positions, too_easy)
    return too_easy


def get_valid(numbers: list[int]) -> set[int]:
    """
    A number is valid if it is possible to get with only 4/7 numbers
    using +/-/*/().
    Humans are not computers so some leeway must be allowed.
    """
    valid = set()
    parentheses_positions = generate_parentheses_positions(4)
    for perm in itertools.permutations(numbers, 4):
        add(perm, parentheses_positions, valid)
    return valid


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


def check_to_evaluate(
    numbers: list[int], operators: tuple[str], parts: list[str]) -> bool:
    """
    Checks if there is any need to evaluate an expression
    with parentheses:
    - There is multiplication or division
    - Any of the parentheses change evaluation
    """
    if "*" not in operators:
        # No point in evaluating only +/- with any parentheses.
        return False
    # If any parentheses do not change evaluation, skip.
    opened = False
    only_multiply = True
    operator_index = 0
    for part in parts:
        if part == "(":
            opened = True
        elif opened:
            if part == ")":
                if only_multiply:
                    return False
                opened = False
                only_multiply = True
            elif not part.isdigit():
                if operators[operator_index] in "+-":
                    only_multiply = False
                operator_index += 1
        elif not part.isdigit():
            operator_index += 1
    return True


def add(
    numbers: list[int], parentheses_positions: list[tuple],
    to_add: set[int]) -> None:
    """
    Evaluates numbers using all possible operator positions
    (Cartesian product), and adds then to a particular set.
    """
    start, start_number_indexes, start_operator_indexes = (
        get_starting_positions(numbers))

    for operators in itertools.product("+-*", repeat=len(numbers) - 1):
        for i, operator in zip(start_operator_indexes, operators):
            start[i] = operator
        
        expression = "".join(start)
        result = evaluate(expression)
        if 201 <= result <= 999:
            to_add.add(result)

    for positions in parentheses_positions:
        # Copy of original expression/indexes required for each change
        # in parentheses positions.
        current = [*start]
        number_indexes = [*start_number_indexes]
        operator_indexes = [*start_operator_indexes]

        for p in positions:
            add_parentheses(p, current, number_indexes, operator_indexes)
        for operators in itertools.product("+-*", repeat=len(numbers) - 1):
            if check_to_evaluate(numbers, operators, current):
                for i, operator in zip(operator_indexes, operators):
                    current[i] = operator

                expression = "".join(current)
                result = evaluate(expression)
                if 201 <= result <= 999:
                    to_add.add(result)


def add_parentheses(
    to_add: tuple, current: list[str],
    number_indexes: list[int], operator_indexes: list[int]) -> None:
    """
    Adds required parentheses to an expression.
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


def generate_parentheses_positions(number_count: int) -> list[tuple]:
    """
    Gets simple possible parentheses positions for n numbers.
    This is in the form of a list of lists of 2-tuples, with
    the 1st number indicating the position of the opening parenthesis,
    and the latter indicating the position of the closing parenthesis.
    Not recursive, so no nested parentheses.
    """
    if number_count < 3:
        # No possible ambiguity with order of operations.
        return []
    
    positions = []
    for size in range(number_count - 1, 1, -1):
        # size = number of numbers in parentheses
        for i in range(number_count - size + 1):
            positions.append([(i, i + size)])
            if number_count - (i + size) >= 2:
                positions.append([(i, i + size), (i + size, number_count)])
                # Multiple parentheses in one expression is possible.
                for pos in generate_parentheses_positions(
                    number_count - (i + size)
                ):
                    new = [(i, i + size)]
                    for p in pos:
                        new.append((p[0] + i + size, p[1] + i + size))
                    positions.append(new)

    return positions


def evaluate(expression: str) -> int:
    """
    Evaluates a simple maths expression with only +/-/*/().
    BIDMAS followed (but no indices and divsion).
    No nested parentheses also.
    A good bit faster than the built in eval(), and also safer!
    """
    # Parts consist of numbers and operators
    # Even indexes = numbers, odd indexes = operators.
    # Parentheses never included, they are evaluated beforehand.
    parts = []
    # Number digits
    number = ""
    i = 0
    multiplying_total = None
    length = len(expression)
    while i < length:
        if expression[i].isdigit():
            # Digit
            number += expression[i]
            i += 1
        elif expression[i] == "(":
            # Parentheses evaluation (recursive).
            r = 2
            while expression[i + r] != ")":
                r += 1
            result = evaluate(expression[i+1:i+r])
            if multiplying_total is not None:
                multiplying_total *= result
            else:
                parts.append(result)
            i += r + 1
        else:
            # Operator
            if number:
                if multiplying_total is not None:
                    multiplying_total *= int(number)
                else:
                    parts.append(int(number))
                number = ""

            is_multiplying = expression[i] == "*"
            if is_multiplying and multiplying_total is None:
                multiplying_total = parts.pop()
            elif not is_multiplying:
                if multiplying_total is not None:
                    parts.append(multiplying_total)
                    multiplying_total = None
                parts.append(expression[i])
            i += 1
    # Last number (if final character not a closing parenthesis).
    if number:
        if multiplying_total is not None:
            multiplying_total *= int(number)
        else:
            parts.append(int(number))

    # Ending multiplying total.
    if multiplying_total is not None:
        parts.append(multiplying_total)

    # Remaining parts should only be numbers, + and -.
    total = parts[0]
    for i in range(1, len(parts), 2):
        if parts[i] == "+":
            total += parts[i+1]
        else:
            total -= parts[i+1]
    
    return total


def generate_number(numbers: list[int]) -> int:
    """
    Gets a random suitable number
    from 201-999 for the player to try and get.
    """
    # Removes too easy numbers from valid numbers.
    valid = get_valid(numbers) - get_too_easy(numbers)
    # Removes recently generated numbers.
    no_recent = valid - set(data.get_recent_numbers())
    # If no numbers except recent ones are valid,
    # select any valid number instead.
    choice = secrets.choice(tuple(no_recent or valid))
    data.add_recent_number(choice)
    return choice