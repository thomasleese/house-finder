import logging

from .listing import Listing


logger = logging.getLogger(__name__)


class Zoopla:
    """Search various property sites to find listings."""

    def __init__(self, api_key, cache):
        self.api_key = api_key
        self.cache = cache

    def search(self, query):
        logger.info('Searching Zoopla...')

        session = self.cache.requests_session

        property_listings_url = 'http://api.zoopla.co.uk/api/v1/property_listings.json'
        params = {
            'area': query.area,
            'listing_status': query.type,
            'minimum_beds': query.no_bedrooms.min,
            'maximum_beds': query.no_bedrooms.max,
            'minimum_price': query.price.min,
            'maximum_price': query.price.max,

            'summarised': 'yes',

            'api_key': self.api_key,
            'page_size': 100,
            'page_number': 1,
        }

        while True:
            response = session.get(property_listings_url, params=params)

            logger.debug(f'Loading page #{params["page_number"]}')

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
