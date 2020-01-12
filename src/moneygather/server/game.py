"""
Module: game
"""
from moneygather.server.exceptions import GameAlreadyStarted
from moneygather.server.exceptions import GameIsFull
from moneygather.server.log import logger
from moneygather.server.board import Board
from moneygather.server.turn import Turn

import random


class Game:
    """ A class to encapsulate the logic of the game.

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
    player_order: list
        List of players indicating the turn order
    player_turn: Player
        Player that has the turn
    """

    GAME_NOT_STARTED = 0
    GAME_STARTING = 1
    GAME_STARTED = 2

    def __init__(self, server, num_players=2):
        self.num_players = num_players
        self.board = Board()
        self.turn = Turn(self)
        self.positions = 40
        self.server = server
        self.initialize_game()

    def initialize_game(self):
        """ Initializes the game.
        """
        self.status = self.GAME_NOT_STARTED
        self.players = []
        self.player_order = []
        self.player_turn = None
        self.turn.end_turn()

    def add_player(self, player):
        """ Adds the player to the list of players.
        """
        if self.has_started():
            raise GameAlreadyStarted
        if len(self.players) == self.num_players:
            raise GameIsFull

        self.players.append(player)

    def remove_player(self, player):
        """ Sets the player as bankrupted and ends the turn if his turn
        was the current turn.
        """
        if self.has_started():
            player.set_bankrupt()
        else:
            self.players.remove(player)

    def has_started(self):
        """ Returns True if the game has started.
        """
        if self.status == self.GAME_NOT_STARTED:
            return False
        return True

    def player_is_ready(self):
        """ Invoked by the players when set to ready.
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
        logger.info('GAME ==> Starting game')

        self.status = self.GAME_STARTED
        for player in self.players:
            player.set_awaiting_turn()

        self.player_order = random.sample(self.players, len(self.players))
        self.server.start_game()
        self.next_turn()

    def get_next_player_turn(self):
        """ Sets next player.
        """
        if not self.player_turn:
            return self.player_order[0]

        current_turn = self.player_order.index(self.player_turn)
        next_turn = (current_turn + 1) % len(self.player_order)
        next_player = self.player_order[next_turn]
        return next_player

    def next_turn(self):
        """ Sets next turn.
        """
        logger.info('GAME ==> Next turn')

        if self.player_turn:
            self.player_turn.set_awaiting_turn()

        self.player_turn = self.get_next_player_turn()
        self.player_turn.set_turn()
        self.turn.turn_start(self.player_turn)

    def player_rolled_dices(self, dices):
        """ Invoked by the player when they roll dices.
        Informs the server about the dices result
        """
        self.turn.dices_end(dices)
        self.server.send_dices_result(dices)

    def player_moved(self, player):
        """ Invoked by the players when they move.
        Informs the server about the movement
        """
        self.server.send_player_movement(player)

    def player_bankrupted(self, player):
        """ Invoked by the players when they bankrupt or by game when
        player disconnects.
        Informs the server the player bannkrupted and performs end of game
        if required
        """
        self.server.send_player_bankrupt(player)
        players_bankrupted = self.num_players_bankrupt()

        if players_bankrupted == len(self.players):
            self.initialize_game()
            return

        if players_bankrupted == len(self.players) - 1:
            self.turn.end_turn()
            winner = self.get_winner()
            self.server.send_player_winner(winner)
            return

        if self.player_turn == player:
            self.turn.end_turn()
            self.next_turn()

    def num_players_bankrupt(self):
        num_players = 0
        for player in self.players:
            if player.is_bankrupted():
                num_players += 1
        return num_players

    def get_winner(self):
        """ Returns first player non bankrupted which is the winner.
        This funcion will only be called when the rest of players have
        bankrupted.
        """
        for player in self.players:
            if not player.is_bankrupted():
                return player
        return None
