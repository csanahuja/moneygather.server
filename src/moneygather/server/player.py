"""
Module: player
"""
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
        Game instance
    client : client class
        Client reference
    name: str
        Name of the player
    colour: str
        Colour of the player
    gender: str
        Gender of the player
    credit: int
        Credit of the player
    position: int
        Position of the player in the board
    """

    DEFAULT_COLOUR = '#007bff'
    DEFAULT_GENDER = 'ghost'
    # STATUS
    PLAYER_NOT_READY = 0
    PLAYER_READY = 1

    def __init__(
        self,
        client,
        name=None,
        colour=None,
        gender=None,
        credit=1000,
    ):
        self.UID = str(uuid.uuid4())
        self.status = self.PLAYER_NOT_READY
        self.game = None
        self.client = client
        self.name = self.assign_name(name)
        self.colour = self.assign_colour(colour)
        self.gender = self.assign_gender(gender)
        self.credit = credit
        self.position = 0

    def assign_name(self, name):
        if not name:
            return f"Player {self.UID.split('-')[0]}"
        return name

    def assign_colour(self, colour):
        if not colour:
            return self.DEFAULT_COLOUR
        return colour

    def assign_gender(self, gender):
        if not gender:
            return self.DEFAULT_GENDER
        return gender

    def set_ready(self):
        if self.game.has_started() or self.status == self.PLAYER_READY:
            return
        self.status = self.PLAYER_READY
        self.game.player_is_ready()

    def set_not_ready(self):
        if self.game.has_started() or self.status == self.PLAYER_NOT_READY:
            return
        self.status = self.PLAYER_NOT_READY
