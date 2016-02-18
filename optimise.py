from collections import namedtuple

from geopy.distance import vincenty
import requests
import yaml


Listing = namedtuple('Listing', ['location', 'price', 'url'])

_Constraint = namedtuple('Constraint', ['type', 'closest_to', 'weight'])


class Constraint(_Constraint):
    def calculate(self, listing):
        if self.type == 'price':
            return listing.price - self.closest_to
        elif self.type == 'location':
            return vincenty(self.closest_to, listing.location).meters
        else:
            raise ValueError('Unsupported type: {}'.format(self.type))

    def calculate_weighted(self, listing):
        return self.calculate(listing) * self.weight


class Property:
    def __init__(self, listing):
        self.listing = listing
        self.values = []

    def __str__(self):
        return '{}: {}'.format(self.listing, self.value)

    def apply_constraints(self, constraints):
        for constraint in constraints:
            self.values.append(constraint.calculate_weighted(self.listing))

    @property
    def value(self):
        return sum(self.values)


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

            'summarised': 'yes',

            'api_key': self.secrets['zoopla']['api_key'],
            'page_size': 100,
            'page_number': 1
        }

        while True:
            response = requests.get(url, params=params)
            json = response.json()

            if not json['listing']:
                break

            for listing in json['listing']:
                location = (listing['latitude'], listing['longitude'])
                price = int(listing['price'])
                url = listing['details_url']
                yield Listing(location, price, url)

            params['page_number'] += 1

    def search(self):
        yield from self.search_zoopla()


def optimise(house, secrets):
    searcher = Searcher(secrets, house['search'])

    constraints = [Constraint(**c) for c in house['constraints']]

    listings = list(searcher.search())
    print('Found', len(listings), 'listings.')

    properties = []

    for listing in listings:
        property = Property(listing)
        property.apply_constraints(constraints)
        properties.append(property)

    properties.sort(key=lambda property: property.value)

    for property in properties:
        print(property)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('house')
    parser.add_argument('secrets')
    args = parser.parse_args()

    with open(args.house) as file:
        house = yaml.load(file)

    with open(args.secrets) as file:
        secrets = yaml.load(file)

    optimise(house, secrets)


if __name__ == '__main__':
    main()
