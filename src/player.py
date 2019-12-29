import uuid

DEFAULT_COLOUR = '#007bff'
DEFAULT_GENDER = 'ghost'


class Player:

    def __init__(self, index, name=None, colour=None, gender=None, credit=1000):
        self.UID = str(uuid.uuid4())
        self.name = self.assign_name(name, index)
        self.colour = self.assign_colour(colour)
        self.gender = self.assign_gender(gender)
        self.credit = credit
        self.position = 0

    def assign_name(self, name, index):
        if not name:
            return f"Player - {index}"
        return name

    def assign_colour(self, colour):
        if not colour:
            return DEFAULT_COLOUR
        return colour

    def assign_gender(self, gender):
        if not gender:
            return DEFAULT_GENDER
        return gender

    def toJSON(self):
        json = {
            'name': self.name,
            'colour': self.colour,
            'gender': self.gender,
        }
        return json