"""
Module: game
"""
from moneygather.server.exceptions import GameAlreadyStarted
from moneygather.server.exceptions import GameIsFull


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
    """

    GAME_NOT_STARTED = 0
    GAME_STARTING = 1
    GAME_STARTED = 2

    def __init__(self, server, num_players=4):
        self.status = self.GAME_NOT_STARTED
        self.players = []
        self.num_players = num_players
        self.server = server

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
        pass
