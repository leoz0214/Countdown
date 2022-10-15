#include <string.h>
#include <cmath>


extern "C" {
    __declspec(dllexport) double eval(
        char expression[], int first, int last);
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