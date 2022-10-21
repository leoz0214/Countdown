#include <vector>
#include <string>
#include <set>
#include <string.h>
#include <cmath>
#include <algorithm>
#include <random>
#include <fstream>


extern "C" {
    __declspec(dllexport) int generate_number(
        int number_array[7], int recent[], int recent_count
    );
    __declspec(dllexport) void get_solution(
        int numbers_array[], int number_count, int target,
        char operators_c_str[], int parentheses_setting, int file_number
    );
    __declspec(dllexport) double eval(
        char expression[], int first, int last
    );
}


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


// Checks if a character is in a C string.
bool char_in_string(char c, char str[], int length) {
    for (int i = 0; i < length; i++) {
        if (c == str[i]) {
            return true;
        }
    }
    return false;
}


// Joins STL strings in a vector with a given separator.
std::string
join_strings(std::vector<std::string> &vector, std::string sep = "") {
    std::string result = "";
    for (std::string str : vector) {
        result += str + sep;
    }
    for (int i = 0; i < sep.length(); i++) {
        result.pop_back();
    }
    return result;
}


// Gets Cartesian product of a STL string with length n.
std::vector<std::string> string_product(std::string str, int repeat) {
    std::vector<std::string> result;
    int indexes[repeat];
    std::string new_string = "";
    for (int i = 0; i < repeat; i++) {
        indexes[i] = 0;
    }
    int max_index = str.length() - 1;
    while (true) {
        for (int i = 0; i < repeat; i++) {
            new_string += str[indexes[i]];
        }
        result.push_back(new_string);
        new_string.clear();

        for (int i = repeat - 1; i >= 0; i--) {
            if (indexes[i]++ == max_index) {
                if (i == 0) {
                    // Final product.
                    return result;
                }
            } else {
                // Reset to 0 for all characters to the right.
                for (int j = i + 1; j < repeat; j++) {
                    indexes[j] = 0;
                }
                break;
            }
        }
    }
}


// Gets permutations of a vector of length n.
std::vector<std::vector<int>>
permutations(std::vector<int> &vector, int length) {
    std::vector<std::vector<int>> result;
    std::vector<int> temp_vector, vector_part;
    if (length == 1) {
        for (int value : vector) {
            result.push_back((std::vector<int>) {value});
        }
        return result;
    }
    for (int i = 0; i < vector.size(); i++) {
        vector_part.clear();
        for (int j = 0; j < vector.size(); j++) {
            if (j != i) {
                vector_part.push_back(vector[j]);
            }
        }
        for (std::vector<int> vect : permutations(vector_part, length - 1)) {
            temp_vector = {vector[i]};
            for (int value : vect) {
                temp_vector.push_back(value);
            }
            result.push_back(temp_vector);
        }
    }
    return result;
}


// Generates a random number from a minimum to maximum.
int generate_random_number(int minimum, int maximum) {
    std::random_device device;
    std::mt19937 rng(device());
    std::uniform_int_distribution<std::mt19937::result_type>
        random_generator(minimum, maximum);
    return random_generator(rng);
}


// Add or subtract the number? Or is it the first?
void add_or_subtract(double &total, int previous_is_add, double number) {
    if (previous_is_add == -1) {
        // Start of expression - first number
        total = number;
    } else if (previous_is_add == 1) {
        // Add
        total += number;
    } else {
        total -= number;
    }
}


// Evaluates a simple maths expression with only +/-/*/'/'/().
// Only the requirements of this software is needed, so not for general use.
// Order of operations followed.
double eval(char expression[], int first, int last) {
    double total = 0; // Running total
    int number = -1; // Holds current number if any.
    double previous_number = -1;
    int previous_is_add = -1; // Holds if previous operator is + or not.
    double multiplying_and_dividing_total = -1;
    bool is_multiplying = false;
    bool is_dividing = false;
    bool just_evaluated_parentheses = false;
    int i = first; // Starting index
    int end = last != -1 ? last : strlen(expression) - 1; // Last index
    // Needed for parentheses evaluation.
    int r, nested;
    double result;

    while (i <= end) {
        if (expression[i] >= '0' && expression[i] <= '9') {
            // Digit
            number = (number * 10 * (number != -1)) + expression[i] - 48;
            i++;
            just_evaluated_parentheses = false;
        } else if (expression[i] == '(') {
            // Parentheses expression (evaluate recursively)
            r = 0;
            nested = 1;
            while (nested) {
                r++;
                if (expression[i+r] == '(') {
                    nested++;
                } else if (expression[i+r] == ')') {
                    nested--;
                }
            }

            result = eval(expression, i+1, i+r-1);
            previous_number = result;
            if (std::isnan(result)) {
                // Invalid
                return nan("0x12345");
            }
            if (is_multiplying) {
                if (multiplying_and_dividing_total != 0) {
                    multiplying_and_dividing_total *= result;
                }  else if (result == 0) {
                    multiplying_and_dividing_total = 0;
                }
            } else if (is_dividing)  {
                if (result == 0) {
                    // Cannot divide by 0
                    return nan("0x12345");
                } else if (multiplying_and_dividing_total != 0) {
                    multiplying_and_dividing_total /= result;
                }
            } else {
                add_or_subtract(total, previous_is_add, result);
            }
            i += r + 1;
            just_evaluated_parentheses = true;
        } else {
            // Operator
            if (is_dividing && number == 0 && !just_evaluated_parentheses) {
                return nan("0x12345");
            } else if (number != -1) {
                if (is_multiplying) {
                    multiplying_and_dividing_total *= number;
                } else if (is_dividing)  {
                    multiplying_and_dividing_total /= number;
                } else {
                    add_or_subtract(total, previous_is_add, number);
                }
                previous_number = number;
                number = -1;
            }

            is_multiplying = expression[i] == '*';
            is_dividing = expression[i] == '/';
            if (
                (is_multiplying || is_dividing) 
                && multiplying_and_dividing_total == -1
            ) {
                // Start multiplying/dividing
                multiplying_and_dividing_total = previous_number;
                if (previous_is_add == -1) {
                    total = 0;
                } else if (previous_is_add) {
                    total -= previous_number;
                } else {
                    total += previous_number;
                }
            } else if (!(is_multiplying || is_dividing)) {
                if (multiplying_and_dividing_total != -1) {
                    // Stop multiplying/dividing
                    add_or_subtract(
                        total, previous_is_add, multiplying_and_dividing_total);
                    multiplying_and_dividing_total = -1;
                }
                previous_is_add = expression[i] == '+';
            }
            i++;
            just_evaluated_parentheses = false;
        }
    }

    if (is_dividing && number == 0 && !just_evaluated_parentheses) {
        return nan("0x12345");
    } else if (number != -1) {
        // Final number
        if (is_multiplying) {
            multiplying_and_dividing_total *= number;
        } else if (is_dividing) {
            multiplying_and_dividing_total /= number;
        } else {
            add_or_subtract(total, previous_is_add, number);
        }
    }
    
    if (multiplying_and_dividing_total != -1) {
        // Final multiplying/dividing total
        add_or_subtract(
            total, previous_is_add, multiplying_and_dividing_total);
    }

    return total;
}


// Gets starting number and operator indexes, along with the
// initial parts of the expression when no parentheses have been added.
StartParts get_starting_positions(std::vector<int> &numbers) {
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
    std::string &operators, std::vector<std::string> &parts
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
    bool has_add_or_subtract[8];
    int has_add_or_subtract_index = 0;
    // If "+/-" both before and after parentheses expression,
    // the parentheses are obviously not needed, so return False.
    // E.g. 1 * ((2 + 3) + 4) is False as the parentheses around
    // 2 + 3 are unnecessary.
    // Also if ( or nothing is before the target ( and
    // ) is followed by +/-, False is still returned, and vice versa.
    bool before_opening_parenthesis[8];
    int before_opening_parenthesis_index = 0;
    int operator_index = 0;
    char add_subtract[3] = "+-";

    int i = 0;
    for (std::string part : parts) {
        if (part == "(") {
            // New set of parentheses opened.
            opened++;
            // Assume otherwise until confirmed.
            has_add_or_subtract[has_add_or_subtract_index++] = false;
            before_opening_parenthesis[before_opening_parenthesis_index++] =
                i == 0 || parts[i-1] == "("
                || char_in_string(operators[operator_index-1], add_subtract, 2);
        } else if (opened) {
            if (part == ")") {
                // Parentheses are closing.
                if (!has_add_or_subtract[--has_add_or_subtract_index]) {
                    return false;
                }
                if (
                    before_opening_parenthesis[
                        --before_opening_parenthesis_index] &&
                    (
                        i + 1 >= parts.size() || parts[i+1] == ")"
                        || char_in_string(
                            operators[operator_index], add_subtract, 2))
                ) {
                    return false;
                }
                opened--;
            } else if (part[0] < '0' || part[0] > '9') {
                if (
                    char_in_string(
                        operators[operator_index++], add_subtract, 2)
                ) {
                    has_add_or_subtract[has_add_or_subtract_index-1] = true;
                }
            }
        } else if (part[0] < '0' || part[0] > '9')  {
            // Increment to the next operator.
            operator_index++;
        }
        i++;
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


std::vector<std::vector<Parentheses>> PARENTHESES[8] = {
    generate_parentheses_positions(0), generate_parentheses_positions(1),
    generate_parentheses_positions(2), generate_parentheses_positions(3),
    generate_parentheses_positions(4), generate_parentheses_positions(5),
    generate_parentheses_positions(6), generate_parentheses_positions(7)
};


// Joins parts of an expression and evalutes it.
// If the result is within the possible target number range, add.
void check_to_add(std::vector<std::string> &parts, std::set<int> &to_add) {
    std::string expression = join_strings(parts);
    // Guaranteed to be integer as no division involved.
    int result = eval((char*) expression.c_str(), 0, -1);
    if (result >= 201 && result <= 999) {
        to_add.insert(result);
    }
}


// For generation of valid/easy numbers.
// Adds required parentheses to an expression.
// Handles nested parentheses recursively.
void add_parentheses(
    Parentheses &parentheses, std::vector<std::string> &current,
    std::vector<int> &number_indexes, std::vector<int> &operator_indexes,
    std::vector<std::string> &operators_product, std::set<int> &to_add
) {
    // Opening parentheses
    current.insert(current.begin() + number_indexes[parentheses.start], "(");
    // Shift indexes to the right.
    for (int i = parentheses.start; i < number_indexes.size(); i++) {
        number_indexes[i]++;
    }
    for (int i = parentheses.start; i < operator_indexes.size(); i++) {
        operator_indexes[i]++;
    }

    // Closing parentheses
    current.insert(current.begin() + number_indexes[parentheses.stop]-1, ")");
    for (int i = parentheses.stop; i < number_indexes.size(); i++) {
        number_indexes[i]++;
    }
    for (int i = parentheses.stop - 1; i < operator_indexes.size(); i++) {
        operator_indexes[i]++;
    }

    if (parentheses.stop - parentheses.start >= 3) {
        // Nested parentheses
        std::set<int> new_numbers;
        std::vector<std::string> deeper_current;
        std::vector<int> deeper_number_indexes, deeper_operator_indexes;
        Parentheses add;
        for (
            std::vector<Parentheses> positions
            : PARENTHESES[parentheses.stop - parentheses.start]
        ) {
            deeper_current = current;
            deeper_number_indexes = number_indexes;
            deeper_operator_indexes = operator_indexes;

            for (Parentheses p : positions) {
                add = {
                    p.start + parentheses.start,
                    p.stop + parentheses.start};
                add_parentheses(
                    add, deeper_current, deeper_number_indexes,
                    deeper_operator_indexes, operators_product,
                    new_numbers);
            }

            for (std::string operators : operators_product) {
                if (!check_to_evaluate(operators, deeper_current)) {
                    continue;
                }
                for (int i = 0; i < operators.length(); i++) {
                    deeper_current[deeper_operator_indexes[i]] = operators[i];
                }
                check_to_add(deeper_current, to_add);
            }
        }
    }
}


// Evaluates numbers using all possible operator positions
// (Cartesian product), and adds then to a particular set.
void add(
    std::vector<int> &numbers,
    std::vector<std::vector<Parentheses>> &parentheses_positions,
    std::set<int> &to_add
) {
    StartParts start_parts = get_starting_positions(numbers);
    std::vector<std::string> start = start_parts.start;
    std::vector<int> start_number_indexes = start_parts.start_number_indexes;
    std::vector<int>
        start_operator_indexes = start_parts.start_operator_indexes;

    std::vector<std::string> operators_product =
        string_product("+-*", numbers.size() - 1);
    
    for (std::string operators : operators_product) {
        for (int i = 0; i < operators.length(); i++) {
            start[start_operator_indexes[i]] = operators[i];
        }
        check_to_add(start, to_add);
    }

    std::vector<std::string> current;
    std::vector<int> number_indexes, operator_indexes;

    for (std::vector<Parentheses> positions : parentheses_positions) {
        current = start;
        number_indexes = start_number_indexes;
        operator_indexes = start_operator_indexes;

        for (Parentheses parentheses : positions) {
            add_parentheses(
                parentheses, current, number_indexes,
                operator_indexes, operators_product, to_add);
        }

        for (std::string operators : operators_product) {
            if (!check_to_evaluate(operators, current)) {
                continue;
            }
            for (int i = 0; i < operators.length(); i++) {
                current[operator_indexes[i]] = operators[i];
            }
            check_to_add(current, to_add);
        }
    }
}


// A number is too easy to get if it is possible to get with
// 3 or less smaller numbers. Easy numbers will not be generated.
std::set<int> get_too_easy(std::vector<int> numbers) {
    std::set<int> too_easy;
    for (int count = 2; count < 4; count++) {
        for (std::vector<int> perm : permutations(numbers, count)) {
            add(perm, PARENTHESES[count], too_easy);
        }
    }
    return too_easy;
}


// A number is valid if it is possible to get with only 4/7 numbers
// using +/-/*/().
// Humans are not computers so some leeway must be allowed.
std::set<int> get_valid(std::vector<int> numbers) {
    std::set<int> valid;
    for (std::vector<int> perm : permutations(numbers, 4)) {
        add(perm, PARENTHESES[4], valid);
    }
    return valid;
}


// Gets a random suitable number
// from 201-999 for the player to try and get.
int generate_number(int number_array[7], int recent[], int recent_count) {
    std::vector<int> numbers;
    for (int i = 0; i < 7; i++) {
        numbers.push_back(number_array[i]);
    }
    std::set<int> recent_set;
    for (int i = 0; i < recent_count; i++) {
        recent_set.insert(recent[i]);
    }
    std::set<int> valid = get_valid(numbers);
    std::set<int> too_easy = get_too_easy(numbers);
    std::set<int> valid_and_not_too_easy;
    std::set_difference(
        valid.begin(), valid.end(), too_easy.begin(), too_easy.end(),
        std::inserter(valid_and_not_too_easy, valid_and_not_too_easy.end()));

    std::vector<int> final_possibilities;
    std::set_difference(
        valid_and_not_too_easy.begin(), valid_and_not_too_easy.end(),
        recent_set.begin(), recent_set.end(),
        std::inserter(final_possibilities, final_possibilities.end()));

    // Generate random number by index. Uniform probability.
    return final_possibilities[
        generate_random_number(0, final_possibilities.size()-1)];
}


// Checks if an expression equals target and returns it if true.
// Or else, an empty string is returned.
std::string check_expression_equals_target(
    std::vector<std::string> parts, long double target
) {
    std::string expression = join_strings(parts);
    long double value = eval((char*) expression.c_str(), 0, -1);
    if (value >= target - 0.0000000001 && value <= target + 0.0000000001) {
        return expression;
    }
    return "";
}


// For generation of solutions.
// Adds required parentheses to an expression.
// Handles nested parentheses recursively.
std::string add_parentheses(
    Parentheses &parentheses, std::vector<std::string> &current,
    std::vector<int> &number_indexes, std::vector<int> &operator_indexes,
    std::vector<std::string> &operators_product, int target,
    int parentheses_setting
) {
    // Opening parentheses
    current.insert(current.begin() + number_indexes[parentheses.start], "(");
    // Shift indexes to the right.
    for (int i = parentheses.start; i < number_indexes.size(); i++) {
        number_indexes[i]++;
    }
    for (int i = parentheses.start; i < operator_indexes.size(); i++) {
        operator_indexes[i]++;
    }

    // Closing parentheses
    current.insert(current.begin() + number_indexes[parentheses.stop]-1, ")");
    for (int i = parentheses.stop; i < number_indexes.size(); i++) {
        number_indexes[i]++;
    }
    for (int i = parentheses.stop - 1; i < operator_indexes.size(); i++) {
        operator_indexes[i]++;
    }

    if (parentheses_setting && parentheses.stop - parentheses.start >= 3) {
        // Nested parentheses
        std::string result;
        std::vector<std::string> deeper_current;
        std::vector<int> deeper_number_indexes, deeper_operator_indexes;
        Parentheses add;
        for (
            std::vector<Parentheses> positions
            : PARENTHESES[parentheses.stop - parentheses.start]
        ) {
            deeper_current = current;
            deeper_number_indexes = number_indexes;
            deeper_operator_indexes = operator_indexes;

            for (Parentheses p : positions) {
                add = {
                    p.start + parentheses.start,
                    p.stop + parentheses.start};
                result = add_parentheses(
                    add, deeper_current, deeper_number_indexes,
                    deeper_operator_indexes, operators_product,
                    target, parentheses_setting);
                if (result != "") {
                    return result;
                }
            }

            for (std::string operators : operators_product) {
                if (!check_to_evaluate(operators, deeper_current)) {
                    continue;
                }
                for (int i = 0; i < operators.length(); i++) {
                    deeper_current[deeper_operator_indexes[i]] = operators[i];
                }
                result = check_expression_equals_target(deeper_current, target);
                if (result != "") {
                    return result;
                }
            }
        }
    }
    return "";
}


// Writes the solution to a file.
void write_solution(std::string solution, int file_number) {
    std::string filename = std::to_string(file_number) + ".countdown";
    std::ofstream file(filename);
    file << solution;
    file.close();
}


// Attempts to find a solution for given numbers
// in that particular order along with the target number,
// parentheses positions and operators which can be used.
void get_solution(
    int numbers_array[], int number_count, int target,
    char operators_c_str[], int parentheses_setting, int file_number
) {
    std::vector<int> numbers;
    for (int i = 0; i < number_count; i++) {
        numbers.push_back(numbers_array[i]);
    }
    std::string operators = operators_c_str;

    StartParts start_parts = get_starting_positions(numbers);
    std::vector<std::string> start = start_parts.start;
    std::vector<int> start_number_indexes = start_parts.start_number_indexes;
    std::vector<int>
        start_operator_indexes = start_parts.start_operator_indexes;
    
    std::vector<std::string> operators_product = string_product(
        operators, number_count-1);
    std::rotate(
        operators_product.begin(),
        operators_product.begin() + generate_random_number(
            0, operators_product.size()-1),
        operators_product.end());
    
    std::string result;
    
    for (std::string operators : operators_product) {
        for (int i = 0; i < operators.length(); i++) {
            start[start_operator_indexes[i]] = operators[i];
        }
        result = check_expression_equals_target(start, target);
        if (result != "") {
            write_solution(result, file_number);
            return;
        }
    }

    if (parentheses_setting == -1) {
        return;
    }

    std::vector<std::string> current;
    std::vector<int> number_indexes, operator_indexes;

    for (
        std::vector<Parentheses> positions :
        generate_parentheses_positions(number_count)
    ) {
        current = start;
        number_indexes = start_number_indexes;
        operator_indexes = start_operator_indexes;

        for (Parentheses p : positions) {
            result = add_parentheses(
                p, current, number_indexes, operator_indexes,
                operators_product, target, parentheses_setting);
            if (result != "") {
                write_solution(result, file_number);
                return;
            }
        }

        for (std::string operators : operators_product) {
            if (!check_to_evaluate(operators, current)) {
                continue;
            }
            for (int i = 0; i < operators.length(); i++) {
                current[operator_indexes[i]] = operators[i];
            }
            result = check_expression_equals_target(current, target);
            if (result != "") {
                write_solution(result, file_number);
                return;
            }
        }
    }
}