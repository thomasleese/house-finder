from collections import namedtuple
import csv
import os
import shutil
import subprocess
import tempfile
import time
import urllib.parse

from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
import requests
import yaml


Listing = namedtuple('Listing', ['id', 'location', 'price', 'url', 'print_url', 'address', 'description', 'image'])
ConstraintResult = namedtuple('ConstraintResult',
                              ['constraint', 'score', 'weighted_score'])
_Constraint = namedtuple('Constraint',
                         ['name', 'type', 'closest_to', 'weight'])


class Constraint(_Constraint):
    def calculate(self, listing):
        if self.type == 'price':
            return listing.price - self.closest_to
        elif self.type == 'location':
            return vincenty(self.closest_to, listing.location).meters
        else:
            raise ValueError('Unsupported type: {}'.format(self.type))

    def calculate_weighted(self, listing):
        score = self.calculate(listing)
        return ConstraintResult(self, score, score * self.weight)


class Property:
    def __init__(self, listing):
        self.listing = listing
        self.results = []

    def __str__(self):
        return '{}: {}'.format(self.listing, self.value)

    def apply_constraints(self, constraints):
        for constraint in constraints:
            self.results.append(constraint.calculate_weighted(self.listing))

    @property
    def score(self):
        return sum(c.score for c in self.results)

    @property
    def weighted_score(self):
        return sum(c.weighted_score for c in self.results)


class Searcher:
    """Search various property sites to find listings."""

    def __init__(self, secrets, query):
        self.secrets = secrets
        self.query = query

    def search_zoopla(self):
        print('Searching Zoopla...')

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
        print('#{}'.format(i + 1), property.listing.address)
        filenames.append(generate_property_pdf(property))
        #filenames.append('1')  # only first page

    subprocess.check_call(['pdfunite'] + filenames + [filename])


def optimise(house, secrets, output):
    searcher = Searcher(secrets, house['search'])

    constraints = [Constraint(**c) for c in house['constraints']]

    listings = list(searcher.search())
    print('Found', len(listings), 'listings.')

    properties = []

    for listing in listings:
        property = Property(listing)
        property.apply_constraints(constraints)
        properties.append(property)

    properties.sort(key=lambda property: property.weighted_score)

    generate_output(output, properties, constraints)


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
