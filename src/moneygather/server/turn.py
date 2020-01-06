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
        self.turns = []

    def turn_start(self):
        turn = asyncio.ensure_future(self.turn_timeout())
        self.turns.append(turn)

    async def turn_timeout(self):
        try:
            await asyncio.sleep(self.duration)
        except asyncio.CancelledError:
            return
        else:
            self.turns.pop(0)
            self.game.next_turn()

    def cancel_turn(self):
        if self.turns:
            turn = self.turns.pop(0)
            turn.cancel()
