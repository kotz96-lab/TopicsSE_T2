"""The 29 benchmark tasks (in addition to the hand-authored HE_000).

Each entry defines:
  * task_id           — folder name under benchmark/methods/
  * he_id             — HumanEval task id we base it on
  * mutation_type     — category label (used in analysis + meta.json)
  * faulty_region     — short human-readable label for the buggy region
  * mutation_description — one-liner about what changed
  * mutate            — function (original_source -> mutated_source)
  * extra_tests       — pytest assertion bodies to append (each uses
                        `candidate` as the function under test)

Mutation categories spread across the batch:
  boundary        (5)   < vs <=, > vs >=, off-by-one boundary
  operator        (4)   swap arithmetic op or replace with sibling
  off_by_one      (4)   range/index bounds shifted by 1
  wrong_constant  (4)   base case or literal changed
  logical_op      (3)   and <-> or
  invert          (3)   return / condition inverted
  wrong_variable  (3)   wrong argument or wrong variable returned
  delete_check    (2)   guard condition removed / made trivially false
  wrong_slice     (1)   slice bound shifted
"""

from __future__ import annotations

from scripts.scaffold_tasks import TaskSpec


def _replace_once(src: str, old: str, new: str) -> str:
    """.replace with n=1, and hard-fail if the substring is missing so we
    catch drift between the task plan and HumanEval source."""
    if old not in src:
        raise AssertionError(f"substring not found in source: {old!r}")
    return src.replace(old, new, 1)


TASK_SPECS: list[TaskSpec] = [
    # ---------------- boundary (5) ----------------
    TaskSpec(
        task_id="HE_003_below_zero",
        he_id="HumanEval/3",
        mutation_type="boundary",
        faulty_region="balance sign check",
        mutation_description="changed strict `<` to `<=` so a zero balance now incorrectly flags as below zero",
        mutate=lambda s: _replace_once(s, "if balance < 0:", "if balance <= 0:"),
        extra_tests=[
            "candidate([]) == False",
            "candidate([1, -1]) == False",  # ends at 0, mutant returns True
            "candidate([0]) == False",       # first op leaves balance 0, mutant returns True
            "candidate([5]) == False",
            "candidate([-1]) == True",
            "candidate([1, 2, 3, -5]) == False",
            "candidate([1, 2, 3, -7]) == True",
        ],
    ),
    TaskSpec(
        task_id="HE_012_longest",
        he_id="HumanEval/12",
        mutation_type="boundary",
        faulty_region="maxlen computation",
        mutation_description="took `min` instead of `max` of string lengths, returning the shortest match rather than the longest",
        mutate=lambda s: _replace_once(s, "maxlen = max(len(x) for x in strings)", "maxlen = min(len(x) for x in strings)"),
        extra_tests=[
            "candidate([]) is None",
            "candidate(['a']) == 'a'",
            "candidate(['a', 'bb', 'ccc']) == 'ccc'",
            "candidate(['aaa', 'bb', 'c']) == 'aaa'",
            "candidate(['hi', 'hello', 'hey']) == 'hello'",
            "candidate(['same', 'size']) == 'same'",
            "candidate(['x', 'yy', 'zzz', 'wwww']) == 'wwww'",
        ],
    ),
    TaskSpec(
        task_id="HE_031_is_prime",
        he_id="HumanEval/31",
        mutation_type="boundary",
        faulty_region="early-return guard",
        mutation_description="widened the early-return guard from `< 2` to `<= 2`, so 2 is incorrectly reported as not prime",
        mutate=lambda s: _replace_once(s, "if n < 2:", "if n <= 2:"),
        extra_tests=[
            "candidate(2) == True",  # mutant returns False
            "candidate(3) == True",
            "candidate(4) == False",
            "candidate(5) == True",
            "candidate(0) == False",
            "candidate(1) == False",
            "candidate(15) == False",
        ],
    ),
    TaskSpec(
        task_id="HE_052_below_threshold",
        he_id="HumanEval/52",
        mutation_type="boundary",
        faulty_region="threshold comparison",
        mutation_description="changed `>=` to `>` so elements exactly equal to the threshold are wrongly accepted",
        mutate=lambda s: _replace_once(s, "if e >= t:", "if e > t:"),
        extra_tests=[
            "candidate([], 100) == True",
            "candidate([5, 5, 5], 5) == False",       # mutant returns True
            "candidate([1, 2, 3], 3) == False",       # mutant returns True (3 == threshold)
            "candidate([1, 2, 3], 4) == True",
            "candidate([10], 10) == False",           # mutant returns True
            "candidate([-1, -2, -3], 0) == True",
        ],
    ),
    TaskSpec(
        task_id="HE_071_triangle_area",
        he_id="HumanEval/71",
        mutation_type="boundary",
        faulty_region="triangle-inequality check",
        mutation_description="changed `<=` to `<` in the inequality check, so degenerate triangles (sum of two sides == third) no longer return -1",
        mutate=lambda s: _replace_once(
            s,
            "if a + b <= c or a + c <= b or b + c <= a:",
            "if a + b < c or a + c < b or b + c < a:",
        ),
        extra_tests=[
            "candidate(3, 4, 5) == 6.0",
            "candidate(1, 2, 3) == -1",       # 1+2 == 3 boundary, mutant returns 0.0
            "candidate(2, 2, 4) == -1",       # 2+2 == 4 boundary, mutant returns 0.0
            "candidate(1, 2, 10) == -1",
            "candidate(6, 8, 10) == 24.0",
            "candidate(3, 3, 3) == round(3.897114317029974, 2)",
        ],
    ),

    # ---------------- operator (4) ----------------
    TaskSpec(
        task_id="HE_008_sum_product",
        he_id="HumanEval/8",
        mutation_type="operator",
        faulty_region="running sum accumulator",
        mutation_description="replaced `+=` with `-=` so the sum accumulator subtracts each element",
        mutate=lambda s: _replace_once(s, "sum_value += n", "sum_value -= n"),
        extra_tests=[
            "candidate([]) == (0, 1)",
            "candidate([1, 2, 3, 4]) == (10, 24)",
            "candidate([0, 1, 2]) == (3, 0)",
            "candidate([5]) == (5, 5)",
            "candidate([-1, 1]) == (0, -1)",
            "candidate([2, 2, 2]) == (6, 8)",
            "candidate([10, 20]) == (30, 200)",
        ],
    ),
    TaskSpec(
        task_id="HE_013_greatest_common_divisor",
        he_id="HumanEval/13",
        mutation_type="operator",
        faulty_region="return value",
        mutation_description="returned `b` instead of `a` after the Euclidean loop; since b is 0 at exit this always yields 0",
        mutate=lambda s: _replace_once(s, "    return a\n", "    return b\n"),
        extra_tests=[
            "candidate(12, 18) == 6",
            "candidate(100, 25) == 25",
            "candidate(7, 13) == 1",
            "candidate(48, 60) == 12",
            "candidate(9, 3) == 3",
            "candidate(1, 1) == 1",
            "candidate(50, 15) == 5",
        ],
    ),
    TaskSpec(
        task_id="HE_021_rescale_to_unit",
        he_id="HumanEval/21",
        mutation_type="operator",
        faulty_region="numerator of rescale",
        mutation_description="subtracted max instead of min when rescaling, so all outputs are shifted",
        mutate=lambda s: _replace_once(
            s,
            "return [(x - min_number) / (max_number - min_number) for x in numbers]",
            "return [(x - max_number) / (max_number - min_number) for x in numbers]",
        ),
        extra_tests=[
            "candidate([0.0, 1.0]) == [0.0, 1.0]",
            "candidate([2.0, 6.0, 10.0]) == [0.0, 0.5, 1.0]",
            "candidate([-1.0, 0.0, 1.0]) == [0.0, 0.5, 1.0]",
            "candidate([1.0, 2.0, 3.0, 4.0, 5.0]) == [0.0, 0.25, 0.5, 0.75, 1.0]",
            "candidate([10.0, 20.0]) == [0.0, 1.0]",
            "candidate([5.0, 10.0, 15.0]) == [0.0, 0.5, 1.0]",
        ],
    ),
    TaskSpec(
        task_id="HE_035_max_element",
        he_id="HumanEval/35",
        mutation_type="operator",
        faulty_region="comparison operator",
        mutation_description="flipped `>` to `<` so this computes the minimum instead of the maximum",
        mutate=lambda s: _replace_once(s, "if e > m:", "if e < m:"),
        extra_tests=[
            "candidate([1, 2, 3]) == 3",
            "candidate([3, 2, 1]) == 3",
            "candidate([-1, -2, -3]) == -1",
            "candidate([5]) == 5",
            "candidate([1, 100, 50, 200, 3]) == 200",
            "candidate([0, 0, 0]) == 0",
            "candidate([-100, 0, 100]) == 100",
            "candidate([7, 7, 8]) == 8",
        ],
    ),

    # ---------------- off_by_one (4) ----------------
    TaskSpec(
        task_id="HE_014_all_prefixes",
        he_id="HumanEval/14",
        mutation_type="off_by_one",
        faulty_region="prefix slice length",
        mutation_description="took slice `string[:i]` instead of `string[:i+1]`, so each prefix is one character short (and the first prefix is empty)",
        mutate=lambda s: _replace_once(
            s, "result.append(string[:i+1])", "result.append(string[:i])"
        ),
        extra_tests=[
            "candidate('') == []",
            "candidate('a') == ['a']",
            "candidate('ab') == ['a', 'ab']",
            "candidate('abc') == ['a', 'ab', 'abc']",
            "candidate('xyz') == ['x', 'xy', 'xyz']",
            "candidate('hello') == ['h', 'he', 'hel', 'hell', 'hello']",
            "candidate('1234') == ['1', '12', '123', '1234']",
        ],
    ),
    TaskSpec(
        task_id="HE_018_how_many_times",
        he_id="HumanEval/18",
        mutation_type="off_by_one",
        faulty_region="scan-window upper bound",
        mutation_description="dropped the `+ 1` from the range upper bound, missing matches at the last possible position",
        mutate=lambda s: _replace_once(
            s,
            "for i in range(len(string) - len(substring) + 1):",
            "for i in range(len(string) - len(substring)):",
        ),
        extra_tests=[
            "candidate('', 'a') == 0",
            "candidate('a', 'a') == 1",              # mutant returns 0 (range empty)
            "candidate('aa', 'a') == 2",             # mutant returns 1 (misses last)
            "candidate('abcabc', 'abc') == 2",       # mutant returns 1
            "candidate('aaaa', 'aa') == 3",          # mutant returns 2
            "candidate('abc', 'd') == 0",
            "candidate('xxyz', 'z') == 1",           # mutant returns 0
        ],
    ),
    TaskSpec(
        task_id="HE_024_largest_divisor",
        he_id="HumanEval/24",
        mutation_type="off_by_one",
        faulty_region="divisibility check",
        mutation_description="checked `n % i == 1` instead of `== 0`, so no valid divisor is ever found",
        mutate=lambda s: _replace_once(s, "if n % i == 0:", "if n % i == 1:"),
        extra_tests=[
            "candidate(15) == 5",
            "candidate(100) == 50",
            "candidate(12) == 6",
            "candidate(6) == 3",
            "candidate(49) == 7",
            "candidate(50) == 25",
            "candidate(9) == 3",
        ],
    ),
    TaskSpec(
        task_id="HE_047_median",
        he_id="HumanEval/47",
        mutation_type="off_by_one",
        faulty_region="odd/even length check",
        mutation_description="flipped `% 2 == 1` to `% 2 == 0`, so even-length lists take the odd branch and vice versa",
        mutate=lambda s: _replace_once(s, "if len(l) % 2 == 1:", "if len(l) % 2 == 0:"),
        extra_tests=[
            "candidate([3, 1, 2]) == 2",
            "candidate([1, 2, 3, 4]) == 2.5",       # mutant returns 3 (single index)
            "candidate([5]) == 5",
            "candidate([1, 2]) == 1.5",             # mutant returns 2
            "candidate([-10, 4, 6, 1000, 10, 20]) == 8.0",
            "candidate([7, 3, 1, 5]) == 4.0",
            "candidate([0, 0, 0, 1]) == 0.0",
        ],
    ),

    # ---------------- wrong_constant (4) ----------------
    TaskSpec(
        task_id="HE_046_fib4",
        he_id="HumanEval/46",
        mutation_type="wrong_constant",
        faulty_region="base-case seed",
        mutation_description="changed the seed table `[0, 0, 2, 0]` to `[0, 0, 1, 0]`, corrupting fib4(2) and every value that depends on it",
        mutate=lambda s: _replace_once(s, "results = [0, 0, 2, 0]", "results = [0, 0, 1, 0]"),
        extra_tests=[
            "candidate(0) == 0",
            "candidate(1) == 0",
            "candidate(2) == 2",       # mutant returns 1
            "candidate(3) == 0",
            "candidate(4) == 2",       # 0+2+0+0
            "candidate(5) == 4",       # 2+0+2+0 (mutant returns 3)
            "candidate(6) == 8",       # 4+2+0+2
            "candidate(7) == 14",      # 8+4+2+0
        ],
    ),
    TaskSpec(
        task_id="HE_055_fib",
        he_id="HumanEval/55",
        mutation_type="wrong_constant",
        faulty_region="base case for n == 1",
        mutation_description="base case `fib(1)` returns 0 instead of 1, collapsing the whole sequence to zero",
        mutate=lambda s: _replace_once(
            s,
            "if n == 1:\n        return 1",
            "if n == 1:\n        return 0",
        ),
        extra_tests=[
            "candidate(0) == 0",
            "candidate(1) == 1",       # mutant returns 0
            "candidate(2) == 1",       # mutant returns 0
            "candidate(3) == 2",
            "candidate(4) == 3",
            "candidate(5) == 5",
            "candidate(6) == 8",
            "candidate(7) == 13",
        ],
    ),
    TaskSpec(
        task_id="HE_063_fibfib",
        he_id="HumanEval/63",
        mutation_type="wrong_constant",
        faulty_region="base case for n == 2",
        mutation_description="base case `fibfib(2)` returns 0 instead of 1, so all recursive values are zero",
        mutate=lambda s: _replace_once(
            s,
            "if n == 2:\n        return 1",
            "if n == 2:\n        return 0",
        ),
        extra_tests=[
            "candidate(0) == 0",
            "candidate(1) == 0",
            "candidate(2) == 1",       # mutant returns 0
            "candidate(3) == 1",       # mutant returns 0
            "candidate(4) == 2",
            "candidate(5) == 4",
            "candidate(6) == 7",
            "candidate(7) == 13",
        ],
    ),
    TaskSpec(
        task_id="HE_011_string_xor",
        he_id="HumanEval/11",
        mutation_type="wrong_constant",
        faulty_region="XOR helper return",
        mutation_description="XOR helper returns '1' when the two bits match (should be '0'), inverting every bit",
        mutate=lambda s: _replace_once(
            s,
            "if i == j:\n            return '0'",
            "if i == j:\n            return '1'",
        ),
        extra_tests=[
            "candidate('0', '0') == '0'",       # mutant: '1'
            "candidate('1', '1') == '0'",       # mutant: '1'
            "candidate('0', '1') == '1'",
            "candidate('1', '0') == '1'",
            "candidate('11', '00') == '11'",
            "candidate('101', '010') == '111'",
            "candidate('111', '111') == '000'",
        ],
    ),

    # ---------------- logical_op (3) ----------------
    TaskSpec(
        task_id="HE_057_monotonic",
        he_id="HumanEval/57",
        mutation_type="logical_op",
        faulty_region="monotonic direction check",
        mutation_description="replaced `or` with `and`, so only lists that are simultaneously ascending and descending (i.e. all-equal) count as monotonic",
        mutate=lambda s: _replace_once(
            s,
            "if l == sorted(l) or l == sorted(l, reverse=True):",
            "if l == sorted(l) and l == sorted(l, reverse=True):",
        ),
        extra_tests=[
            "candidate([1, 2, 4, 20]) == True",       # ascending
            "candidate([1, 20, 4, 10]) == False",
            "candidate([4, 1, 0, -10]) == True",      # descending
            "candidate([1, 1, 1, 1]) == True",        # all-equal (mutant also True)
            "candidate([5]) == True",
            "candidate([3, 2, 1]) == True",           # mutant returns False
            "candidate([1, 2, 3]) == True",           # mutant returns False
        ],
    ),
    TaskSpec(
        task_id="HE_064_vowels_count",
        he_id="HumanEval/64",
        mutation_type="logical_op",
        faulty_region="trailing y/Y check",
        mutation_description="joined the two y-check disjuncts with `and`, making the y bonus unreachable",
        mutate=lambda s: _replace_once(
            s,
            "if s[-1] == 'y' or s[-1] == 'Y':",
            "if s[-1] == 'y' and s[-1] == 'Y':",
        ),
        extra_tests=[
            "candidate('hello') == 2",
            "candidate('sky') == 1",           # y at end counts; mutant returns 0
            "candidate('WHY') == 1",           # Y at end counts; mutant returns 0
            "candidate('a') == 1",
            "candidate('b') == 0",
            "candidate('bcd') == 0",
            "candidate('happy') == 2",         # y at end; mutant returns 1
            "candidate('AEIOU') == 5",
        ],
    ),
    TaskSpec(
        task_id="HE_118_get_closest_vowel",
        he_id="HumanEval/118",
        mutation_type="logical_op",
        faulty_region="consonants-on-both-sides check",
        mutation_description="replaced `and` with `or`, so a vowel with only one consonant neighbor now qualifies",
        mutate=lambda s: _replace_once(
            s,
            "if (word[i+1] not in vowels) and (word[i-1] not in vowels):",
            "if (word[i+1] not in vowels) or (word[i-1] not in vowels):",
        ),
        extra_tests=[
            "candidate('yogurt') == 'u'",
            "candidate('FULL') == 'U'",
            "candidate('quick') == ''",
            "candidate('ab') == ''",
            "candidate('') == ''",
            "candidate('easy') == ''",         # 'a' has 'e' vowel before it; mutant might return 'a'
            "candidate('Iain') == ''",
        ],
    ),

    # ---------------- invert (3) ----------------
    TaskSpec(
        task_id="HE_048_is_palindrome",
        he_id="HumanEval/48",
        mutation_type="invert",
        faulty_region="palindrome comparison",
        mutation_description="flipped `!=` to `==`, so the loop returns False on symmetric characters and True on asymmetric ones",
        mutate=lambda s: _replace_once(
            s,
            "if text[i] != text[len(text) - 1 - i]:",
            "if text[i] == text[len(text) - 1 - i]:",
        ),
        extra_tests=[
            "candidate('') == True",
            "candidate('a') == True",          # single char (mutant: False)
            "candidate('ab') == False",
            "candidate('aa') == True",         # mutant: returns False
            "candidate('racecar') == True",    # mutant: returns False
            "candidate('hello') == False",
            "candidate('level') == True",
            "candidate('abc') == False",
        ],
    ),
    TaskSpec(
        task_id="HE_040_triples_sum_to_zero",
        he_id="HumanEval/40",
        mutation_type="invert",
        faulty_region="zero-sum condition",
        mutation_description="checked `!= 0` instead of `== 0`, inverting the condition",
        mutate=lambda s: _replace_once(
            s,
            "if l[i] + l[j] + l[k] == 0:",
            "if l[i] + l[j] + l[k] != 0:",
        ),
        extra_tests=[
            "candidate([1, 3, 5, 0]) == False",
            "candidate([1, 3, 5, -8]) == True",
            "candidate([1, 3, -2, 1]) == True",
            "candidate([0, 0, 0]) == True",
            "candidate([1, 2, 3, 4]) == False",
            "candidate([1, 2, -3]) == True",
            "candidate([2, 4, 6]) == False",
        ],
    ),
    TaskSpec(
        task_id="HE_043_pairs_sum_to_zero",
        he_id="HumanEval/43",
        mutation_type="invert",
        faulty_region="pair-sum condition",
        mutation_description="replaced sum with product so it now returns True when either element is zero",
        mutate=lambda s: _replace_once(
            s, "if l1 + l[j] == 0:", "if l1 * l[j] == 0:"
        ),
        extra_tests=[
            "candidate([1, 3, 5, 0]) == False",         # mutant: True (has 0)
            "candidate([1, 3, -2, 1]) == False",
            "candidate([1, 2, 3, 7]) == False",
            "candidate([2, 4, -5, 3, 5]) == True",      # -5 + 5 == 0
            "candidate([1]) == False",
            "candidate([-1, 1]) == True",
            "candidate([]) == False",
        ],
    ),

    # ---------------- wrong_variable (3) ----------------
    TaskSpec(
        task_id="HE_005_intersperse",
        he_id="HumanEval/5",
        mutation_type="wrong_variable",
        faulty_region="final append",
        mutation_description="appended `numbers[0]` instead of `numbers[-1]`, so the last element becomes a duplicate of the first",
        mutate=lambda s: _replace_once(
            s, "result.append(numbers[-1])", "result.append(numbers[0])"
        ),
        extra_tests=[
            "candidate([], 4) == []",
            "candidate([1], 4) == [1]",
            "candidate([1, 2], 4) == [1, 4, 2]",           # mutant: [1, 4, 1]
            "candidate([1, 2, 3], 0) == [1, 0, 2, 0, 3]",  # mutant: [1, 0, 2, 0, 1]
            "candidate([5, 6, 7, 8], 9) == [5, 9, 6, 9, 7, 9, 8]",
            "candidate([1, 1], 0) == [1, 0, 1]",           # equal ends -- mutant accidentally right
            "candidate([-1, 0, 1], 100) == [-1, 100, 0, 100, 1]",
        ],
    ),
    TaskSpec(
        task_id="HE_009_rolling_max",
        he_id="HumanEval/9",
        mutation_type="wrong_variable",
        faulty_region="running comparison",
        mutation_description="used `min` instead of `max` when updating the running maximum",
        mutate=lambda s: _replace_once(
            s, "running_max = max(running_max, n)", "running_max = min(running_max, n)"
        ),
        extra_tests=[
            "candidate([]) == []",
            "candidate([1, 2, 3, 2, 3, 4, 2]) == [1, 2, 3, 3, 3, 4, 4]",
            "candidate([5, 4, 3, 2, 1]) == [5, 5, 5, 5, 5]",     # mutant: [5,4,3,2,1]
            "candidate([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]",
            "candidate([3, 3, 3]) == [3, 3, 3]",
            "candidate([-1, -2, 0, -3]) == [-1, -1, 0, 0]",
            "candidate([7]) == [7]",
        ],
    ),
    TaskSpec(
        task_id="HE_068_pluck",
        he_id="HumanEval/68",
        mutation_type="wrong_variable",
        faulty_region="filter predicate",
        mutation_description="filtered on `x%2 == 1` (odd) instead of `x%2 == 0` (even), so the result is the smallest odd instead of smallest even",
        mutate=lambda s: _replace_once(
            s, "filter(lambda x: x%2 == 0, arr)", "filter(lambda x: x%2 == 1, arr)"
        ),
        extra_tests=[
            "candidate([]) == []",
            "candidate([4, 2, 3]) == [2, 1]",         # mutant: [3, 2]
            "candidate([1, 2, 3]) == [2, 1]",         # mutant: [1, 0]
            "candidate([5, 0, 3, 0, 4, 2]) == [0, 1]",  # mutant: [3, 2]
            "candidate([1, 3, 5]) == []",             # mutant: [1, 0]
            "candidate([2, 4, 6]) == [2, 0]",         # mutant: []
            "candidate([1, 2, 4]) == [2, 1]",
        ],
    ),

    # ---------------- delete_check (2) ----------------
    TaskSpec(
        task_id="HE_026_remove_duplicates",
        he_id="HumanEval/26",
        mutation_type="delete_check",
        faulty_region="duplicate filter",
        mutation_description="flipped `<= 1` to `>= 1`, so every element (including duplicates) passes the filter",
        mutate=lambda s: _replace_once(
            s, "return [n for n in numbers if c[n] <= 1]",
            "return [n for n in numbers if c[n] >= 1]"
        ),
        extra_tests=[
            "candidate([]) == []",
            "candidate([1, 2, 3]) == [1, 2, 3]",
            "candidate([1, 2, 3, 2, 4]) == [1, 3, 4]",       # mutant: [1,2,3,2,4]
            "candidate([1, 1, 1, 1]) == []",                  # mutant: [1,1,1,1]
            "candidate([5, 5, 6]) == [6]",                    # mutant: [5,5,6]
            "candidate([1, 2, 1, 3, 2]) == [3]",              # mutant: full list
            "candidate([9]) == [9]",
        ],
    ),
    TaskSpec(
        task_id="HE_091_is_bored",
        he_id="HumanEval/91",
        mutation_type="delete_check",
        faulty_region="sentence-start match",
        mutation_description="lowercased the marker to `'i '`, breaking the requirement that sentences must begin with capital I",
        mutate=lambda s: _replace_once(
            s, "sentence[0:2] == 'I '", "sentence[0:2] == 'i '"
        ),
        extra_tests=[
            "candidate('Hello world') == 0",
            "candidate('I am at home. I love pizza.') == 2",   # mutant: 0
            "candidate('It is a nice day. I feel good.') == 1",  # mutant: 0
            "candidate('Is she here? I saw her.') == 1",       # mutant: 0
            "candidate('i am tired.') == 0",                    # mutant: 1 (wrongly matches)
            "candidate('I love apples.') == 1",                 # mutant: 0
            "candidate('') == 0",
        ],
    ),

    # ---------------- wrong_slice (1) ----------------
    TaskSpec(
        task_id="HE_033_sort_third",
        he_id="HumanEval/33",
        mutation_type="wrong_slice",
        faulty_region="stride of the sorted slice",
        mutation_description="sorted every second element instead of every third (`l[::2]` instead of `l[::3]`)",
        mutate=lambda s: _replace_once(
            s, "l[::3] = sorted(l[::3])", "l[::2] = sorted(l[::2])"
        ),
        extra_tests=[
            "candidate([1, 2, 3]) == [1, 2, 3]",           # both give same
            "candidate([5, 6, 3, 4, 8, 9, 2]) == [2, 6, 3, 4, 8, 9, 5]",
            "candidate([]) == []",
            "candidate([1]) == [1]",
            "candidate([10, 20, 30, 40, 50, 60, 70]) == [10, 20, 30, 40, 50, 60, 70]",
            "candidate([9, 1, 2, 6, 4, 5, 3]) == [3, 1, 2, 6, 4, 5, 9]",  # mutant sorts wrong indices
            "candidate([1, 2, 4, 3]) == [1, 2, 4, 3]",
            "candidate([7, 8, 9]) == [7, 8, 9]",
            "candidate([2, 1]) == [2, 1]",
            "candidate([3, 2, 1]) == [3, 2, 1]",
        ],
    ),
]
