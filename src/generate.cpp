#include <iostream>
#include <vector>
#include <string>


struct StartParts {
    std::vector<std::string> start;
    std::vector<int> start_number_indexes;
    std::vector<int> start_operator_indexes;
};


struct Parentheses {
    int start;
    int stop;
};


// Checks if a character is in a STL string.
bool char_in_string(char c, std::string str) {
    return str.find(c) != std::string::npos;
}


// Checks if a STL string consists of entirely digits.
bool string_is_digit(std::string str) {
    for (char c : str) {
        if (c < '0' || c > '9') {
            return false;
        }
    }
    return true;
}


// Gets starting number and operator indexes, along with the
// initial parts of the expression when no parentheses have been added.
StartParts get_starting_positions(std::vector<int> numbers) {
    std::vector<int> start_number_indexes;
    for (int i = 0; i < ((numbers.size() + 1) * 2); i += 2) {
        start_number_indexes.push_back(i);
    }

    std::vector<int> start_operator_indexes;
    for (int i = 1; i < numbers.size() * 2; i += 2) {
        start_operator_indexes.push_back(i);
    }

    std::vector<std::string> start;
    for (int number : numbers) {
        start.push_back(std::to_string(number));
        start.push_back("");
    }
    start.pop_back();

    StartParts start_parts = {
        start, start_number_indexes, start_operator_indexes};
    return start_parts;
}


// Checks if there is any need to evaluate an expression
// with parentheses, as evaluation is expensive in terms of time
// and duplicate solutions are unwanted, so:
// - There is multiplication or division; and
// - All of the parentheses change evaluation
// Especially important for a large number of expression parts.
bool check_to_evaluate(
    std::string operators, std::vector<std::string> parts
) {
    if (!char_in_string('*', operators) && !char_in_string('/', operators)) {
        // No point in evaluating only +/- with any parentheses.
        return false;
    } else if (
        !char_in_string('+', operators) && !char_in_string('-', operators)
    ) {
        // No point in evaluating only x or / with any parentheses.
        return false;
    }

    int opened = 0;
    std::vector<bool> has_add_or_subtract;
    // If "+/-" both before and after parentheses expression,
    // the parentheses are obviously not needed, so return False.
    // E.g. 1 * ((2 + 3) + 4) is False as the parentheses around
    // 2 + 3 are unnecessary.
    // Also if ( or nothing is before the target ( and
    // ) is followed by +/-, False is still returned, and vice versa.
    std::vector<bool> before_opening_parenthesis;
    int operator_index = 0;
    bool temp;

    int i = -1; // First iteration i will be set to 0.
    for (std::string part : parts) {
        i++;
        if (part == "(") {
            // New set of parentheses opened.
            opened++;
            // Assume otherwise until confirmed.
            has_add_or_subtract.push_back(false);
            before_opening_parenthesis.push_back(
                !i || parts[i-1] == "("
                || char_in_string(operators[operator_index-1], "+-")
            );
        } else if (opened) {
            if (part == ")") {
                // Parentheses are closing.
                temp = has_add_or_subtract[has_add_or_subtract.size()-1];
                if (!temp) {
                    return false;
                }
                has_add_or_subtract.pop_back();

                temp = before_opening_parenthesis[
                    before_opening_parenthesis.size()-1];
                if (
                    temp &&
                    (
                        i + 1 >= parts.size() || parts[i+1] == ")"
                        || char_in_string(operators[operator_index], "+-"))
                ) {
                    return false;
                }
                before_opening_parenthesis.pop_back();

                opened--;
            } else if (!string_is_digit(part)) {
                if (char_in_string(operators[operator_index], "+-")) {
                    has_add_or_subtract[has_add_or_subtract.size()-1] = true;
                }
                operator_index++;
            }
        } else if (!string_is_digit(part)) {
            // Increment to the next operator.
            operator_index++;
        }
    }
    return true;
}


// Gets simple possible parentheses positions for n numbers.
// This is in the form of a list of lists of Parentheses structs, with
// the 1st number indicating the position of the opening parenthesis,
// and the latter indicating the position of the closing parenthesis.
std::vector<std::vector<Parentheses>>
generate_parentheses_positions(int number_count) {
    std::vector<std::vector<Parentheses>> positions;
    std::vector<Parentheses> current;
    for (int size = number_count - 1; size > 1; size--) {
        // size = number of numbers in parentheses
        for (int i = 0; i < number_count - size + 1; i++) {
            current = {(Parentheses) {i, i + size}};
            positions.push_back(current);

            if (number_count - (i + size) >= 2) {
                current = {
                    (Parentheses) {i, i + size},
                    (Parentheses) {i + size, number_count}};
                positions.push_back(current);
                // Multiple parentheses in one expression is possible.
                // Get all parentheses in one expression recursively.
                for (
                    std::vector<Parentheses> combo :
                    generate_parentheses_positions(number_count - (i + size))
                ) {
                    current = {(Parentheses) {i, i + size}};
                    for (Parentheses parentheses : combo) {
                        current.push_back(
                            (Parentheses) {
                                parentheses.start + i + size,
                                parentheses.stop + i + size}
                        );
                    }
                    positions.push_back(current);
                }
            }
        }
    }
    return positions;
}


int main() {
    std::vector<int> numbers = {1,2,3,4,5,6,7};
    for (int i = 0; i < 100000; i++) {
        generate_parentheses_positions(7);
    }
    return 0;
}