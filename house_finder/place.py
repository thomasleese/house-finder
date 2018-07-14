import datetime
import json
import logging
import shelve

from cached_property import cached_property

cache = shelve.open('cache.db')

class Place:

    def __init__(self, travel_time_calculator, gmaps, name, mode, arrival_time=None, departure_time=None):
        self.travel_time_calculator = travel_time_calculator
        self.gmaps = gmaps
        self.name = name
        self.mode = mode
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    @cached_property
    def location(self):
        geocode_results = self.gmaps.geocode(self.name)
        location = geocode_results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])
        logging.info(f'Loaded {self.name} as {lat_long}')
        return lat_long

    def get_travel_time(self, location):
        return self.travel_time_calculator(
            origin=self.location,
            destination=location,
            mode=self.mode, 
            arrival_time=self.arrival_time,
            departure_time=self.departure_time
        )

    def calculate(self, listing):
        return self.get_travel_time(listing.location)
