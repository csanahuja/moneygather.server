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
        player.set_money(-30)

    def goes_in(self, player):
        """ Implements what happens when you go in this box.
        """

    def to_json(self):
        """ Returns a json dict with basic attributes
        """
        box = {
            'name': self.name,
            'position': self.position
        }
        return box


class PaymentBox(Box):
    """ Payment Box
    """

    def __init__(self, payment, **kwargs):
        super().__init__(**kwargs)
        self.payment = payment

    def goes_throught(self, player):
        """ Gets paid
        """
        # raise NotImplementedError

    def to_json(self):
        box = super().to_json()
        box['payment'] = self.payment
        return box


class BuyableBox(Box):
    """ Buyable Box
    """

    def __init__(self, price, **kwargs):
        super().__init__(**kwargs)
        self.price = price
        self.owner = None

    def buy(self, player):
        raise NotImplementedError

    def to_json(self):
        box = super().to_json()
        box['price'] = self.price
        box['owner'] = self.owner
        return box


class TownBox(BuyableBox):
    """ Town Box
    """
