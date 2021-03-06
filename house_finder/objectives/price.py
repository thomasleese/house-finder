from .objective import Objective


class PriceObjective(Objective):

    def calculate(self, listing):
        return listing.price

    def present(self, score):
        return f'£{score}'

    @classmethod
    def from_dict(cls, config):
        return cls(config['name'])
