

class RentObjective:

    def __init__(self):
        pass

    def calculate(self, listing):
        return listing.price

    @classmethod
    def from_dict(cls, config):
        return cls()
