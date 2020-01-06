"""
Module: turn
"""
import asyncio


class Turn:
    """ A class to control the turn duration

    Attributes
    ----------
    game : Game
        Game reference
    duration : int
        Number of seconds of turn duration
    """

    def __init__(self, game, duration):
        self.game = game
        self.duration = duration
        self.task = None

    def turn_start(self):
        task = asyncio.ensure_future(self.turn_timeout())
        self.task = task

    async def turn_timeout(self):
        try:
            await asyncio.sleep(self.duration)
        except asyncio.CancelledError:
            self.task = None
            return
        else:
            self.task = None
            self.game.next_turn()

    def cancel_turn(self):
        if self.task:
            self.task.cancel()
