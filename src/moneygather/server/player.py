"""
Module: player
"""
from moneygather.server.exceptions import PlayerNoUpdatableAttribute

import uuid


class Player:
    """ A class to encapsulate the logic of a player

    Attributes
    ----------
    UID : str
        Player identifier
    status : int
        Status of the player
    game : Game
        Game reference
    client : client class
        Client reference
    credit: int
        Credit of the player
    position: int
        Position of the player in the board
    """

    # Personal attributes
    DEFAULT_COLOUR = '#007bff'
    DEFAULT_GENDER = 'ghost'
    UPDATABLE_ATTRIBUTES = [
        'name',
        'colour',
        'gender',
    ]
    # STATUS
    PLAYER_NOT_READY = 0
    PLAYER_READY = 1

    def __init__(
        self,
        client,
        credit=1000,
    ):
        self.UID = str(uuid.uuid4())
        self.status = self.PLAYER_NOT_READY
        self.game = None
        self.client = client
        self.credit = credit
        self.position = 0
        self.name = self.default_name()
        self.colour = self.default_colour()
        self.gender = self.default_gender()

    def default_name(self):
        """ Returns the default name of the player, part of its UID.
        """
        name = f"Player {self.UID.split('-')[0]}"
        return name

    def default_colour(self):
        """ Returns the default colour of the player, DEFAULT_COLOR attribute.
        """
        colour = self.DEFAULT_COLOUR
        return colour

    def default_gender(self):
        """ Returns the default gender of the player, DEFAULT_GENDER attribute.
        """
        gender = self.DEFAULT_GENDER
        return gender

    def to_json(self):
        """ Returns a json dict with basic attributes
        """
        player = {
            'name': self.name,
            'colour': self.colour,
            'gender': self.gender,
        }
        return player

    def update_player_attribute(self, attribute, value):
        """ Updates a personal player attribute. Only attributes inside
        UPDATABLE_ATTRIBUTES are allowed to be updated by this function.
        Returns true if the value changes.
        """
        if attribute not in self.UPDATABLE_ATTRIBUTES:
            raise PlayerNoUpdatableAttribute

        if not value:
            return False

        attr_value = getattr(self, attribute)
        if attr_value == value:
            return False

        setattr(self, attribute, value)
        return True

    def is_ready(self):
        """ Returns if the player is ready.
        """
        return self.status == self.PLAYER_READY

    def set_ready(self):
        """ Changes the player status to ready.
        """
        if self.game.has_started() or self.status == self.PLAYER_READY:
            return
        self.status = self.PLAYER_READY
        self.game.player_is_ready()

    def set_not_ready(self):
        """ Changes the playe rstatus to not ready.
        """
        if self.game.has_started() or self.status == self.PLAYER_NOT_READY:
            return
        self.status = self.PLAYER_NOT_READY
