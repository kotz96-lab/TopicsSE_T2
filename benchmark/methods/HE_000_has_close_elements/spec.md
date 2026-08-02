# has_close_elements

Given a list of floats `numbers` and a positive `threshold`, return `True`
if there exist two *distinct* elements in the list whose absolute difference
is strictly less than `threshold`, and `False` otherwise.

Examples:

    has_close_elements([1.0, 2.0, 3.0], 0.5)   -> False
    has_close_elements([1.0, 2.8, 3.0, 4.0], 0.3) -> True

Source: HumanEval task 0.
