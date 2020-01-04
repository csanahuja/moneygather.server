"""
Module: exceptions
"""


class GameAlreadyStartedException(Exception):
    """ Game has already started """


class MaxPlayersException(Exception):
    """ Game has reached max players allowed """
