"""
Module: boxes
"""


class Box:
    """ Generic class to represent a box.
    """

    def __init__(self, name, position):
        self.name = name
        self.position = position

    def goes_throught(self, player):
        """ Implements what happens when you go throught this box.
        """

    def goes_in(self, player):
        """ Implements what happens when you go in this box.
        """


class BuyableBox(Box):
    """ Buyable Box
    """

    def __init__(self, price, **kwargs):
        super().__init__(**kwargs)
        self.price = price
        self.owner = None

    def buy(self, player):
        raise NotImplementedError


class TownBox(BuyableBox):
    """ Town Box
    """
