"""
Module: player
"""
from moneygather.server.exceptions import PlayerNoUpdatableAttribute

import random
import uuid


class Player:
    """ A class to encapsulate the logic of a player.

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
    money: int
        Money of the player
    position: int
        Position of the player in the board
    random: boolean
        Indicates if some attributes are randomized or default
    """

    # Personal attributes
    DEFAULT_COLOUR = '#007bff'
    DEFAULT_GENDER = 'ghost'
    UPDATABLE_ATTRIBUTES = [
        'name',
        'colour',
        'gender',
    ]
    GENDERS = [
        'ghost',
        'male',
        'female',
    ]
    # STATUS
    PLAYER_NOT_READY = 0
    PLAYER_READY = 1
    PLAYER_AWAITING_TURN = 2
    PLAYER_TURN = 3
    PLAYER_FREEZED = 4
    PLAYER_BANKRUPT = 5

    def __init__(
        self,
        client,
        game,
        money=1000,
        random=True,
    ):
        self.UID = str(uuid.uuid4())
        self.status = self.PLAYER_NOT_READY
        self.game = game
        self.client = client
        self.money = money
        self.position = 0
        self.name = self.default_name()
        if random:
            self.colour = self.random_colour()
            self.gender = self.random_gender()
        else:
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

    def random_colour(self):
        c1 = format(random.randint(0, 255), '2x')
        c2 = format(random.randint(0, 255), '2x')
        c3 = format(random.randint(0, 255), '2x')
        colour = f'#{c1}{c2}{c3}'.replace(' ', '0')
        return colour

    def random_gender(self):
        gender = random.choice(self.GENDERS)
        return gender

    def to_json(self):
        """ Returns a json dict with basic attributes
        """
        player = {
            'name': self.name,
            'colour': self.colour,
            'gender': self.gender,
            'uid': self.UID,
            'position': self.position,
            'money': self.money,
            'ready': self.is_ready(),
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
        if self.game.has_started():
            return True
        return self.status == self.PLAYER_READY

    def is_bankrupted(self):
        """ Returns if the player is bankrupted.
        """
        return self.status == self.PLAYER_BANKRUPT

    def set_ready(self):
        """ Changes the player status to ready.
        """
        if self.game.has_started() or self.status == self.PLAYER_READY:
            return
        self.status = self.PLAYER_READY
        self.game.player_is_ready()

    def set_not_ready(self):
        """ Changes the player status to not ready.
        """
        if self.game.has_started() or self.status == self.PLAYER_NOT_READY:
            return
        self.status = self.PLAYER_NOT_READY

    def set_awaiting_turn(self):
        """ Changes the player status to awaiting turn.
        """
        if self.status == self.PLAYER_BANKRUPT:
            return
        if self.status == self.PLAYER_AWAITING_TURN:
            return
        self.status = self.PLAYER_AWAITING_TURN
        # self.client.send_player_turn_end()

    def set_turn(self):
        """ Changes the player status to turn.
        """
        if self.status == self.PLAYER_TURN:
            return
        self.status = self.PLAYER_TURN
        self.client.send_player_turn(10)

    def set_bankrupt(self):
        """ Changes the player status to bankrupt.
        """
        if self.status == self.PLAYER_BANKRUPT:
            return
        self.status = self.PLAYER_BANKRUPT
        self.game.player_bankrupted(self)

    def roll_dices(self):
        """ Rolls dices. Generates two random numbers from 1-6.
        """
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)

        self.client.send_player_end_dices()
        self.game.player_rolled_dices([dice1, dice2])
        self.move(dice1 + dice2)

    def move(self, movement):
        """ Moves the player from current position to `position + movement`
        position.
        """
        next_position = self.position

        for mov in range(movement):
            next_position += 1
            if next_position == self.game.positions:
                next_position = 0

            box = self.game.board.get_box(next_position)
            box.goes_throught(self)

        self.position = next_position
        self.game.player_money(self)
        self.game.player_moved(self)

    def set_money(self, money):
        self.money += money
        if self.money < 0:
            self.set_bankrupt()
