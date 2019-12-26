class Player:

    def __init__(self, index, name=None, colour=None, gender=None, credit=1000):
        self.name = self.assign_name(name, index)
        self.colour = self.assign_colour(colour)
        self.gender = self.assign_gender(gender)
        self.credit = credit

    def assign_name(self, name, index):
        if not name:
            return f"Player - {index}"
        return name

    def assign_colour(self, colour):
        if not colour:
            return '#9cfff6'
        return colour

    def assign_gender(self, gender):
        if not gender:
            return 'Man'
        return gender

    def toJSON(self):
        json = {
            'name': self.name,
            'colour': self.colour,
            'gender': self.gender,
        }
        return json