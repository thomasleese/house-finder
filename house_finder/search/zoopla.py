import logging

from .listing import Listing


logger = logging.getLogger(__name__)


class Zoopla:
    """Search various property sites to find listings."""

    url = 'http://api.zoopla.co.uk/api/v1/property_listings.json'

    def __init__(self, api_key, cache):
        self.api_key = api_key
        self.cache = cache

    def params_for_query(self, query):
        return {
            'area': query.area,
            'listing_status': query.type,
            'minimum_beds': query.no_bedrooms.min,
            'maximum_beds': query.no_bedrooms.max,
            'minimum_price': query.price.min,
            'maximum_price': query.price.max,

            'api_key': self.api_key,
            'page_size': 100,
            'page_number': 1,
        }

    def build_listing(self, listing):
        id = listing['listing_id']
        location = (listing['latitude'], listing['longitude'])
        price = int(listing['price'])
        listing_url = listing['details_url']
        print_url = 'http://www.zoopla.co.uk/to-rent/details/print/{}'.format(id)
        address = listing['displayable_address']
        image = listing['image_url']
        description = listing['description']

        return Listing(
            id, location, price, listing_url, print_url, address, description, image
        )

    def filter_listings(self, query, listings):
        for listing in listings:
            if listing['rental_prices']['shared_occupancy'] == 'Y' and not query.shared:
                continue

            if query.furnished and listing['furnished_state'] == 'unfurnished':
                continue

            if query.furnished is False and listing['furnished_state'] == 'furnished':
                continue

            if not listing['image_url']:
                continue

            yield listing

    def _search(self, query):
        logger.info('Searching Zoopla...')

        session = self.cache.requests_session

        params = self.params_for_query(query)

        while True:
            logger.debug(f'Loading page #{params["page_number"]}')

            response = session.get(self.url, params=params)
            json = response.json()

            if not json['listing']:
                break

            for listing in self.filter_listings(query, json['listing']):
                yield self.build_listing(listing)

            params['page_number'] += 1

    def search(self, query):
        return list(set(self._search(query)))
