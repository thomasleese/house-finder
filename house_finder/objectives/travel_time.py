import datetime
import json
import logging

from .objective import Objective


class TravelTimeObjective(Objective):

    @staticmethod
    def from_dict(maps, travel_time_calculator, config):
        return SingleTravelTimeObjective.from_dict(maps, travel_time_calculator, config)


class SingleTravelTimeObjective(TravelTimeObjective):

    def __init__(self, travel_time_calculator, name, location, mode, arrival_time=None, departure_time=None):
        super().__init__(name)
        self.travel_time_calculator = travel_time_calculator
        self.location = location
        self.mode = mode
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def calculate(self, listing):
        return self.travel_time_calculator(
            origin=self.location,
            destination=listing.location,
            mode=self.mode,
            arrival_time=self.arrival_time,
            departure_time=self.departure_time
        )

    @classmethod
    def from_dict(cls, maps, travel_time_calculator, config):
        name = config['params']['to']

        geocode_results = maps.geocode(name)
        location = geocode_results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])
        logging.info(f'Loaded {name} as {lat_long}')

        return cls(
            travel_time_calculator, config['name'], lat_long,
            config['params']['via'], config['params'].get('arriving_at'),
            config['params'].get('leaving_at')
        )
