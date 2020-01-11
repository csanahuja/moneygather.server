"""
Module: board
"""
from moneygather.server.boxes import Box
from moneygather.server.boxes import PaymentBox
from moneygather.server.boxes import TownBox
from moneygather.server.config import BOARD_BOXES


class Board:
    """ A class to represent a board.
    """

    def __init__(self, board_boxes=BOARD_BOXES):
        self.boxes = self.construct_board(board_boxes)

    def construct_board(self, board_boxes):
        """ Creates a list dict all the boxes the board have.
        """

        boxes = dict()

        for box in board_boxes:
            position = box.get('position')
            boxes[position] = self.construct_box(box)

        return boxes

    def construct_box(self, box):
        box_type = box.pop('type')

        if box_type == 'PaymentBox':
            return PaymentBox(**box)

        if box_type == 'TownBox':
            return TownBox(**box)

        if box_type == 'Box':
            return Box(**box)

    def to_json(self):
        board = dict()
        for position, box in self.boxes.items():
            board[position] = box.to_json()
        return board
