import datetime
from enum import Enum
import json
import logging

from .objective import Objective
from ..maps import NoTravelTimeError


class Direction(Enum):
    to_listing = 'to'
    from_listing = 'from'


class TravelTimeObjective(Objective):

    def __init__(self, name, maximum, maps, direction, mode, arrival_time=None, departure_time=None):
        super().__init__(name, maximum)
        self.maps = maps
        self.direction = direction
        self.mode = mode
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    def calculate(self, origin, destination):
        if self.direction == Direction.to_listing:
            origin, destination = destination, origin

        try:
            return self.maps.calculate_travel_time(
                origin=origin,
                destination=destination,
                mode=self.mode,
                arrival_time=self.arrival_time,
                departure_time=self.departure_time
            )
        except NoTravelTimeError:
            return None


    @staticmethod
    def from_dict(maps, config):
        if 'to_any' in config['params'] or 'from_any' in config['params']:
            return MultipleTravelTimeObjective.from_dict(maps, config)
        else:
            return SingleTravelTimeObjective.from_dict(maps, config)


class SingleTravelTimeObjective(TravelTimeObjective):

    def __init__(self, name, maximum, maps, location, direction, mode, arrival_time=None, departure_time=None):
        super().__init__(name, maximum, maps, direction, mode, arrival_time, departure_time)
        self.location = location

    def calculate(self, listing):
        return super().calculate(listing.location, self.location)

    @classmethod
    def from_dict(cls, maps, config):
        if 'to' in config['params']:
            name = config['params']['to']
            direction = Direction.from_listing
        else:
            name = config['params']['from']
            direction = Direction.to_listing

        lat_long = maps.find_latitude_longiture(name)

        return cls(
            config['name'], config.get('maximum'), maps,
            lat_long, direction, config['params']['via'],
            config['params'].get('arriving_at'),
            config['params'].get('leaving_at')
        )


class MultipleTravelTimeObjective(TravelTimeObjective):

    def __init__(self, name, maximum, maps, place_type, direction, mode, arrival_time=None, departure_time=None):
        super().__init__(name, maximum, maps, direction, mode, arrival_time, departure_time)
        self.place_type = place_type

    def calculate(self, listing):
        nearby_places = self.maps.find_nearby_places(listing.location, self.place_type)

        closest_place = nearby_places[0]
        location = closest_place['geometry']['location']['lat'], closest_place['geometry']['location']['lng']

        return super().calculate(listing.location, location)

    @classmethod
    def from_dict(cls, maps, config):
        if 'to_any' in config['params']:
            name = config['params']['to_any']
            direction = Direction.from_listing
        else:
            name = config['params']['from_any']
            direction = Direction.to_listing

        return cls(
            config['name'], config.get('maximum'), maps,
            name, direction, config['params']['via'],
            config['params'].get('arriving_at'),
            config['params'].get('leaving_at'),
        )
