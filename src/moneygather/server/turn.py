"""
Module: turn
"""
import asyncio


class Turn:
    """ A class to encapsulate the Turn of Player inside a Game.

    Attributes
    ----------
    game : Game
        Game reference
    """

    ROLLING_DICES = 0
    DUMMY_ACTION = 1

    def __init__(self, game):
        self.game = game
        self.status = self.ROLLING_DICES
        self.action_timeout = None
        self.action = -1
        self.actions = [
            self.rolling_dices,
            self.dummy_action,
        ]
        self.actions_duration = [
            5,
            5,
        ]

    def turn_start(self, player):
        self.player = player
        self.status = self.ROLLING_DICES
        self.action = -1
        self.next_action()

    def next_action(self):
        """ Executes next action.
        """
        self.action += 1
        next_action = self.actions[self.action]
        next_action()

    def rolling_dices(self):
        timeout = self.actions_duration[self.action]
        action = self.player.roll_dices
        self.action_timeout = self.start_timeout_task(timeout, action)

    def dices_end(self):
        self.end_timeout_task()
        self.next_action()

    def dummy_action(self):
        self.status = self.DUMMY_ACTION
        timeout = self.actions_duration[self.action]
        action = self.game.next_turn
        self.action_timeout = self.start_timeout_task(timeout, action)

    def end_turn(self):
        self.end_timeout_task()

    def start_timeout_task(self, timeout, action):
        task = asyncio.ensure_future(
            self.timeout_action(timeout, action))
        return task

    def end_timeout_task(self):
        if self.action_timeout:
            self.action_timeout.cancel()
            self.action_timeout = None

    async def timeout_action(self, timeout, action):
        try:
            await asyncio.sleep(timeout)
            self.action_timeout = None
            if action:
                action()
        except asyncio.CancelledError:
            return
