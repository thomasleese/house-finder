class Objective:

    def __init__(self, name, maximum=None):
        self.name = name
        self.maximum = maximum

    @property
    def constraint_function(self):
        if self.maximum:
            return lambda x: x < self.maximum
        else:
            return lambda x: True

    @staticmethod
    def from_dict(config, maps):
        from .rent import RentObjective
        from .travel_time import TravelTimeObjective

        if config['type'] == 'travel_time':
            return TravelTimeObjective.from_dict(maps, config)
        elif config['type'] == 'rent':
            return RentObjective.from_dict(config)
