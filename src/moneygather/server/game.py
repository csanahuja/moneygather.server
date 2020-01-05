"""
Module: game
"""
from moneygather.server.exceptions import GameAlreadyStarted
from moneygather.server.exceptions import GameIsFull

import random


class Game:
    """ A class to encapsulate the logic of the game

    Attributes
    ----------
    status : int
        Status of the game
    players : list<Player>
        List of players instances
    server : server class
        Server reference
    num_players: int
        Numbers of players the game needs
    turn_length: int
        Number of seconds of turn duration
    player_order: list
        List of players indicating the turn order
    player_turn: Player
        Player that has the turn
    """

    GAME_NOT_STARTED = 0
    GAME_STARTING = 1
    GAME_STARTED = 2

    def __init__(self, server, num_players=4, turn_duration=30):
        self.num_players = num_players
        self.turn_duration = turn_duration
        self.server = server
        self.initialize_game()

    def initialize_game(self):
        """ Initializes the game.
        """
        self.status = self.GAME_NOT_STARTED
        self.players = []
        self.player_order = []
        self.player_turn = None

    def add_player(self, player):
        """ Adds the player to the list of players and sets a back reference
        in the player.
        """
        if self.has_started():
            raise GameAlreadyStarted
        if len(self.players) == 4:
            raise GameIsFull

        self.players.append(player)
        player.game = self

    def remove_player(self, player):
        """ Removes the player from the list of players and unsets the back
        reference.
        """
        self.players.remove(player)
        player.game = None
        if not self.players:
            self.initialize_game()

    def has_started(self):
        """ Returns True if the game has started.
        """
        if self.status == self.GAME_NOT_STARTED:
            return False
        return True

    def player_is_ready(self):
        """ Method invoked by the players when set to ready.
        Checks if all players are ready and the criterias to start
        the game are meet.
        """
        if len(self.players) != self.num_players:
            return

        if all(map(lambda player: player.is_ready(), self.players)):
            self.start_game()

    def start_game(self):
        """ Starts the game.
        """
        self.status = self.GAME_STARTED
        for player in self.players:
            player.set_awaiting_turn()

        self.player_order = random.sample(self.players, self.num_players)
        self.server.start_game()
        self.next_turn()

    def get_next_player_turn(self):
        """ Sets next player turn.
        """
        if not self.player_turn:
            return self.player_order[0]

        current_turn = self.player_order.index(self.player_turn)
        next_turn = (current_turn + 1) % self.num_players
        next_player = self.player_order[next_turn]
        return next_player

    def next_turn(self):
        """ Sets next turn
        """
        if self.player_turn:
            self.player_turn.set_awaiting_turn()
        self.player_turn = self.get_next_player_turn()
        self.player_turn.set_turn()
