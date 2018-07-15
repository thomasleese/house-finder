import datetime
import json
import logging


class TravelTimeObjective:

    def __init__(self, travel_time_calculator, location, mode, arrival_time=None, departure_time=None):
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

    @staticmethod
    def from_yaml(maps, travel_time_calculator, config):
        name = config['params']['to']

        geocode_results = maps.geocode(name)
        location = geocode_results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])
        logging.info(f'Loaded {name} as {lat_long}')

        return TravelTimeObjective(
            travel_time_calculator, lat_long, config['params']['via'],
            config['params'].get('arriving_at'), config['params'].get('leaving_at')
        )
