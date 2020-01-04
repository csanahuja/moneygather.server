"""
Module: exceptions
"""


class GameAlreadyStarted(Exception):
    """ Game already started """


class GameIsFull(Exception):
    """ Game is full, no more players allowed """


class PlayerNoUpdatableAttribute(Exception):
    """ This attribute cannot be updated by this method """
