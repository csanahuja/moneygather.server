"""
Module: utils
"""


NUMBER_STRING_DICT = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
}


def number_to_string(number):
    try:
        return NUMBER_STRING_DICT[number]
    except KeyError:
        return 'one'
