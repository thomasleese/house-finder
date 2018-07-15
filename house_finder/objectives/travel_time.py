import datetime
from enum import Enum
import json
import logging

from .objective import Objective

class Direction(Enum):
    to_listing = 'to'
    from_listing = 'from'

class TravelTimeObjective(Objective):

    def __init__(self, name, travel_time_calculator, direction, mode, arrival_time=None, departure_time=None):
        super().__init__(name)
        self.travel_time_calculator = travel_time_calculator
        self.direction = direction
        self.mode = mode
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def calculate(self, origin, destination):
        if self.direction == Direction.to_listing:
            origin, destination = destination, origin

        return self.travel_time_calculator(
            origin=origin,
            destination=destination,
            mode=self.mode,
            arrival_time=self.arrival_time,
            departure_time=self.departure_time
        )

    @staticmethod
    def from_dict(maps, travel_time_calculator, config):
        if 'to_any' in config['params']:
            return MultipleTravelTimeObjective.from_dict(
                maps, travel_time_calculator, config
            )
        else:
            return SingleTravelTimeObjective.from_dict(
                maps, travel_time_calculator, config
            )


class SingleTravelTimeObjective(TravelTimeObjective):

    def __init__(self, travel_time_calculator, name, location, direction, mode, arrival_time=None, departure_time=None):
        super().__init__(name, travel_time_calculator, direction, mode, arrival_time, departure_time)
        self.location = location

    def calculate(self, listing):
        return super().calculate(listing.location, self.location)

    @classmethod
    def from_dict(cls, maps, travel_time_calculator, config):
        if 'to' in config['params']:
            name = config['params']['to']
            direction = Direction.to_listing
        else:
            name = config['params']['from']
            direction = Direction.from_listing

        geocode_results = maps.geocode(name)
        location = geocode_results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])
        logging.info(f'Loaded {name} as {lat_long}')

        return cls(
            travel_time_calculator, config['name'], lat_long, direction,
            config['params']['via'], config['params'].get('arriving_at'),
            config['params'].get('leaving_at')
        )


class MultipleTravelTimeObjective(TravelTimeObjective):

    def __init__(self, name, travel_time_calculator, maps, place_type, mode, arrival_time=None, departure_time=None):
        super().__init__(name, travel_time_calculator, Direction.from_listing, mode, arrival_time, departure_time)
        self.maps = maps
        self.place_type = place_type

    def calculate(self, listing):
        results = self.maps.places_nearby(
            location=listing.location, type=self.place_type, rank_by='distance',
            keyword=self.place_type,
        )

        first_result = results['results'][0]
        location = first_result['geometry']['location']['lat'], first_result['geometry']['location']['lng']

        return super().calculate(listing.location, location)

    @classmethod
    def from_dict(cls, maps, travel_time_calculator, config):
        return cls(
            config['name'], travel_time_calculator, maps,
            config['params']['to_any'], config['params']['via'],
            config['params'].get('arriving_at'),
            config['params'].get('leaving_at'),
        )
