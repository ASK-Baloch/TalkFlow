from __future__ import annotations

_DIGITS = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}


_SMALL = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}


_TENS = {
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}


def digits_to_words(
    value: str,
) -> str:
    return " ".join(_DIGITS[digit] for digit in value if digit in _DIGITS)


def integer_to_words(
    value: int,
) -> str:
    if value < 0:
        return "minus " + integer_to_words(abs(value))

    if value < 20:
        return _SMALL[value]

    if value < 100:
        tens = (value // 10) * 10

        remainder = value % 10

        if remainder == 0:
            return _TENS[tens]

        return f"{_TENS[tens]} {_SMALL[remainder]}"

    if value < 1000:
        hundreds = value // 100

        remainder = value % 100

        result = f"{_SMALL[hundreds]} hundred"

        if remainder:
            result += " " + integer_to_words(remainder)

        return result

    if value < 1_000_000:
        thousands = value // 1000

        remainder = value % 1000

        result = integer_to_words(thousands) + " thousand"

        if remainder:
            result += " " + integer_to_words(remainder)

        return result

    return str(value)
