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
    MOVEMENT = 1

    def __init__(self, game):
        self.game = game
        self.status = self.ROLLING_DICES
        self.action_timeout = None
        self.action = -1
        self.actions = [
            self.rolling_dices_step,
            self.movement_step,
        ]
        self.dices_timeout = 5
        self.movement_timeout = 7

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

    def rolling_dices_step(self):
        timeout = self.dices_timeout
        action = self.player.roll_dices
        self.action_timeout = self.start_timeout_task(timeout, action)

    def dices_end(self, dices):
        self.end_timeout_task()
        self.movement_timeout = (dices[0] + dices[1]) * 0.5 + 1
        self.next_action()

    def movement_step(self):
        self.status = self.MOVEMENT
        timeout = self.movement_timeout
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
