from collections import namedtuple
import csv
import time

from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
import lxml.html
import requests
import yaml


Listing = namedtuple('Listing', ['location', 'price', 'url', 'address'])
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

            'summarised': 'yes',

            'api_key': self.secrets['zoopla']['api_key'],
            'page_size': 100,
            'page_number': 1
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
                location = (listing['latitude'], listing['longitude'])
                price = int(listing['price'])
                listing_url = listing['details_url']
                address = listing['displayable_address']
                yield Listing(location, price, listing_url, address)

            params['page_number'] += 1

    def search_rightmove(self):
        print('Searching RightMove...')

        type_ahead = [self.query['area'][:2].upper(),
                      self.query['area'][2:4].upper()]
        url = 'http://www.rightmove.co.uk/typeAhead/uknostreet/{}/{}' \
            .format(type_ahead[0], type_ahead[1])

        response = requests.get(url)
        location = response.json()['typeAheadLocations'][0] \
            ['locationIdentifier']

        url = 'http://www.rightmove.co.uk/property-to-rent/find.html'
        params = {
            'searchType': self.query['type'].upper(),
            'locationIdentifier': location,
            'insId': 1,
            'radius': 0.0,
            'minBedrooms': self.query['bedrooms'][0],
            'maxBedrooms': self.query['bedrooms'][1],
            'houseFlatShare': 'false',
            'numberOfPropertiesPerPage': 50,
            'index': 0
        }

        """
        http://www.rightmove.co.uk/property-to-rent/find.html?
        searchType=RENT
        &locationIdentifier=REGION%5E418
        &insId=1
        &radius=0.0
        &minPrice=
        &maxPrice=
        &minBedrooms=3
        &maxBedrooms=3
        &displayPropertyType=
        &maxDaysSinceAdded=
        &sortByPriceDescending=
        &_includeLetAgreed=on
        &primaryDisplayPropertyType=
        &secondaryDisplayPropertyType=
        &oldDisplayPropertyType=
        &oldPrimaryDisplayPropertyType=
        &letType=&letFurnishType=
        &houseFlatShare=false
        """

        total = None

        while total is None or params['index'] <= total:
            response = requests.get(url, params=params)
            print(response.url)

            tree = lxml.html.fromstring(response.content)
            tree.make_links_absolute(url)

            listings = tree.cssselect('#summaries .summary-list-item')
            for listing in listings:
                address = listing.cssselect('.displayaddress')[0] \
                    .text_content()

                geolocator = GoogleV3(self.secrets['geo']['api_key'])
                location = geolocator.geocode(address)
                if location is None:
                    continue

                location = (location.latitude, location.longitude)

                price = int(listing.cssselect('.price')[0].text_content().strip().replace(',', '').split(' ')[0][1:])

                listing_url = listing.cssselect('.price-new a')[0].get('href')

                yield Listing(location, price, listing_url, address)

            if total is None:
                total = int(tree.cssselect('#resultcount')[0].text_content())

            params['index'] += params['numberOfPropertiesPerPage']

    def search(self):
        yield from self.search_zoopla()
        yield from self.search_rightmove()


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

    headings = ['Address', 'URL']
    for constraint in constraints:
        headings.append(constraint.name)
        headings.append('Weighted Score')
    headings.append('Score')
    headings.append('Weighted Score')

    with open(output, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(headings)

        for property in properties:
            row = [property.listing.address, property.listing.url]
            for i, _ in enumerate(constraints):
                row.append(property.results[i].score)
                row.append(property.results[i].weighted_score)
            row.append(property.score)
            row.append(property.weighted_score)
            writer.writerow(row)


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
