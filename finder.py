from collections import namedtuple
import csv
import datetime
import logging
import os
import shutil
import subprocess
import tempfile
import time
import urllib.parse

from cached_property import cached_property
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
import googlemaps
import requests
import yaml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


Listing = namedtuple('Listing', ['id', 'location', 'price', 'url', 'print_url',
                                 'address', 'description', 'image'])


class Place:

    def __init__(self, gmaps, name, mode, arrival_time=None, departure_time=None):
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

    def format_time(self, string):
        hour, minute = [int(x) for x in string.split(':')]
        return datetime.datetime.utcnow().replace(hour=hour, minute=minute)

    def get_travel_time(self, location):
        search_params = {
            'mode': self.mode,
            'traffic_model': 'pessimistic',
        }

        if self.arrival_time:
            search_params['arrival_time'] = self.format_time(self.arrival_time)

        if self.departure_time:
            search_params['departure_time'] = self.format_time(self.departure_time)

        results = self.gmaps.directions(
            self.name, location,
            **search_params,
        )

        leg = results[0]['legs'][0]

        return leg['duration']['value']

    def calculate(self, listing):
        return self.get_travel_time(listing.location)


class Property:

    def __init__(self, listing):
        self.listing = listing
        self.results = []

    def __str__(self):
        return f'{self.listing}: {self.value}'

    def apply_constraints(self, constraints):
        for constraint in constraints:
            self.results.append(constraint.calculate(self.listing))

    @property
    def score(self):
        return sum(self.results)


class Searcher:
    """Search various property sites to find listings."""

    def __init__(self, secrets, query):
        self.secrets = secrets
        self.query = query

    def search_zoopla(self):
        logger.info('Searching Zoopla...')

        url = 'http://api.zoopla.co.uk/api/v1/property_listings.json'
        params = {
            'area': self.query['area'],
            'listing_status': self.query['type'],
            'minimum_beds': self.query['bedrooms'][0],
            'maximum_beds': self.query['bedrooms'][1],
            'maximum_price': self.query['budget'],

            'summarised': 'yes',

            'api_key': self.secrets['zoopla']['api_key'],
            'page_size': 100,
            'page_number': 1,
        }

        while True:
            response = requests.get(url, params=params)

            try:
                json = response.json()
            except ValueError:
                break

            if not json['listing']:
                break

            for listing in json['listing']:
                id = listing['listing_id']
                location = (listing['latitude'], listing['longitude'])
                price = int(listing['price'])
                url = listing['details_url']
                print_url = 'http://www.zoopla.co.uk/to-rent/details/print/{}'.format(id)
                address = listing['displayable_address']
                image = listing['image_url']
                description = listing['description']
                yield Listing(id, location, price, url, print_url, address, description, image)

            params['page_number'] += 1

    def search(self):
        yield from self.search_zoopla()


def clean_url(url):
    o = urllib.parse.urlparse(url)
    return o.scheme + '://' + o.netloc + o.path


def generate_property_pdf(property):
    filename = 'outputs/{}.pdf'.format(property.listing.id)

    if not os.path.exists(filename):
        args = ['wkhtmltopdf',
                '--footer-center', clean_url(property.listing.url),
                '-q',
                property.listing.print_url,
                filename]

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            if not os.path.exists(filename):
                raise

    return filename

def generate_output(filename, properties, constraints):
    filenames = []

    for i, property in enumerate(properties):
        logger.info(f'#{i} #{property.listing.address}')
        filenames.append(generate_property_pdf(property))

    subprocess.check_call(['pdfunite'] + filenames + [filename])


def optimise(house, secrets, output):
    gmaps = googlemaps.Client(key=secrets['google']['api_key'])

    searcher = Searcher(secrets, house['search'])

    places = [Place(gmaps, **c) for c in house['places']]

    listings = list(searcher.search())
    logger.info('Found', len(listings), 'listings.')

    properties = []

    for listing in listings:
        logger.info(f'Applying constraints for {listing.address}')
        property = Property(listing)
        property.apply_constraints(places)
        properties.append(property)

    properties.sort(key=lambda property: property.score)

    generate_output(output, properties, places)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('house')
    parser.add_argument('secrets')
    parser.add_argument('output')
    args = parser.parse_args()

    with open(args.house) as file:
        house = yaml.load(file)

    with open(args.secrets) as file:
        secrets = yaml.load(file)

    optimise(house, secrets, args.output)


if __name__ == '__main__':
    main()
