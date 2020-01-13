"""
Module: utils
"""
import re


NUMBER_STRING_DICT = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
}


def number_to_string(number):
    """ Returns the string number representation of an int
    """
    try:
        return NUMBER_STRING_DICT[number]
    except KeyError:
        return 'one'


def remove_html_tags(text):
    """ Remove html tags from a text
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
