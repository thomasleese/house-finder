import logging
from typing import NamedTuple, Tuple

import requests_cache

logger = logging.getLogger(__name__)


class Listing(NamedTuple):
    id: str
    location: Tuple[float, float]
    price: int
    url: str
    print_url: str
    address: str
    description: str
    image: str


class Searcher:
    """Search various property sites to find listings."""

    def __init__(self, cache, secrets, query):
        self.cache = cache
        self.secrets = secrets
        self.query = query

    def search_zoopla(self):
        logger.info('Searching Zoopla...')

        session = self.cache.requests_session

        property_listings_url = 'http://api.zoopla.co.uk/api/v1/property_listings.json'
        params = {
            'area': self.query['area'],
            'listing_status': self.query['type'],
            'minimum_beds': self.query['bedrooms'][0],
            'maximum_beds': self.query['bedrooms'][1],
            'minimum_price': self.query['price'][0],
            'maximum_price': self.query['price'][1],

            'summarised': 'yes',

            'api_key': self.secrets['zoopla']['api_key'],
            'page_size': 100,
            'page_number': 1,
        }

        while True:
            response = session.get(property_listings_url, params=params)

            logger.info(f'Loading page #{params["page_number"]}')

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
                listing_url = listing['details_url']
                print_url = 'http://www.zoopla.co.uk/to-rent/details/print/{}'.format(id)
                address = listing['displayable_address']
                image = listing['image_url']
                description = listing['description']
                yield Listing(id, location, price, listing_url, print_url, address, description, image)

            params['page_number'] += 1

    def search(self):
        yield from self.search_zoopla()
