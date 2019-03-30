class Objective:

    def __init__(self, name, maximum=None):
        self.name = name
        self.maximum = maximum

    def calculate(self, listing):
        raise NotImplementedError('calculate must be implemented')

    def present(self, score):
        raise NotImplementedError('present must be implemented')

    @property
    def constraint_function(self):
        if self.maximum:
            return lambda x: x < self.maximum
        else:
            return lambda x: True

    @staticmethod
    def from_dict(config, maps):
        from .price import PriceObjective
        from .travel_time import TravelTimeObjective

        if config['type'] == 'travel_time':
            return TravelTimeObjective.from_dict(maps, config)
        elif config['type'] == 'price':
            return PriceObjective.from_dict(config)
