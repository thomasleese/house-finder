from .rent import RentObjective
from .travel_time import TravelTimeObjective

class Objective:

    @staticmethod
    def from_dict(config, maps, travel_time_calculator):
        if config['type'] == 'travel_time':
            return TravelTimeObjective.from_dict(maps, travel_time_calculator, config)
        elif config['type'] == 'rent':
            return RentObjective.from_dict(config)
