from .objective import Objective


class RentObjective(Objective):

    def __init__(self, name):
        super().__init__(name)

    def calculate(self, listing):
        return listing.price

    @classmethod
    def from_dict(cls, config):
        return cls(config['name'])
