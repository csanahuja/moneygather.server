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
    BOX = 2

    def __init__(self, game):
        self.game = game
        self.player = None
        self.status = self.ROLLING_DICES
        self.action_timeout = None
        self.action = -1
        self.actions = [
            self.rolling_dices_step,
            self.movement_step,
            self.box_step,
        ]
        self.dices_timeout = 10
        self.movement_timeout = 7
        self.box_timeout = 1

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

    def movement_step(self):
        self.status = self.MOVEMENT
        timeout = self.movement_timeout
        action = self.next_action
        self.action_timeout = self.start_timeout_task(timeout, action)

    def box_step(self):
        self.status = self.BOX
        timeout = self.box_timeout
        action = self.game.next_turn
        self.action_timeout = self.start_timeout_task(timeout, action)

    def dices_end(self, dices):
        self.end_timeout_task()
        self.movement_timeout = (dices[0] + dices[1]) * 0.5 + 1
        self.next_action()

    def end_turn(self):
        self.end_timeout_task()
        if self.player:
            self.player.client.send_player_end_dices()

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
