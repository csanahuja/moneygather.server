"""
Module: turn
"""
import asyncio


class Turn:
    """ A class to encapsulate the Turn of Player inside a Game

    Attributes
    ----------
    game : Game
        Game reference
    """

    THROWING_DICES = 0

    def __init__(self, game):
        self.game = game
        self.status = self.THROWING_DICES
        self.action_timeout = None
        self.action = -1
        self.actions = [
            self.throwing_dices,
            self.testing
        ]
        self.actions_duration = [
            10,
            5,
        ]

    def turn_start(self, player):
        self.player = player
        self.status = self.THROWING_DICES
        self.action = -1
        self.next_action()

    def next_action(self):
        """ Executes next action.
        """
        self.action += 1
        next_action = self.actions[self.action]
        next_action()

    def throwing_dices(self):
        timeout = self.actions_duration[self.action]
        action = self.player.throw_dices
        self.action_timeout = asyncio.ensure_future(
            self.timeout_action(timeout, action))

    def dices_end(self):
        print(self.action_timeout)
        if self.action_timeout:
            self.action_timeout.cancel()
        self.next_action()

    def testing(self):
        print('testtttting')

    async def timeout_action(self, timeout, action):
        try:
            await asyncio.sleep(timeout)
            self.action_timeout = None
            if action:
                action()
        except asyncio.CancelledError:
            self.action_timeout = None
