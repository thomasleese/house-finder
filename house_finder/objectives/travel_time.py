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

        geocode_results = maps.gmaps.geocode(name)
        location = geocode_results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])
        logging.info(f'Loaded {name} as {lat_long}')

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
        results = self.maps.gmaps.places_nearby(
            location=listing.location, type=self.place_type, rank_by='distance',
            keyword=self.place_type,
        )

        first_result = results['results'][0]
        location = first_result['geometry']['location']['lat'], first_result['geometry']['location']['lng']

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
