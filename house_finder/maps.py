import datetime
import json
import logging

import googlemaps


logger = logging.getLogger(__name__)


class NoTravelTimeError(Exception):
    pass


class TravelTimeCalulator:

    def __init__(self, gmaps, cache):
        self.gmaps = gmaps
        self.cache = cache

    def __call__(self, **kwargs):
        cache_key = {'travel_time': kwargs}

        if cache_key in self.cache.data:
            return self.cache.data[cache_key]

        params = self._create_search_params(**kwargs)
        duration = self.calculate_time(params)
        self.cache.data[cache_key] = duration

        return duration

    def _format_time(self, string):
        hour, minute = [int(x) for x in string.split(':')]
        return int(
            datetime.datetime.utcnow() \
                .replace(hour=hour, minute=minute, second=0) \
                .timestamp()
        )

    def calculate_time(self, params):
        return self._extract_duration(
            self.gmaps.directions(**params)
        )

    def _extract_duration(self, results):
        try:
            leg = results[0]['legs'][0]
            return leg['duration']['value']
        except (KeyError, IndexError):
            raise NoTravelTimeError()

    def _create_search_params(self, origin, destination, mode, arrival_time, departure_time):
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
        }

        if arrival_time:
            params['arrival_time'] = self._format_time(arrival_time)
            params['traffic_model'] = 'pessimistic'

        if departure_time:
            params['departure_time'] = self._format_time(departure_time)
            params['traffic_model'] = 'pessimistic'

        return params


class LatitudeLongitudeFinder:

    def __init__(self, gmaps, cache):
        self.gmaps = gmaps
        self.cache = cache

    def __call__(self, query):
        query = query.strip()

        cache_key = {'latitude_longitude': query}
        if cache_key in self.cache.data:
            return self.cache.data[cache_key]

        results = self.gmaps.geocode(query)
        location = results[0]['geometry']['location']
        lat_long = (location['lat'], location['lng'])

        logger.debug(f'Loaded {query} as {lat_long}')

        self.cache.data[cache_key] = lat_long
        return lat_long


class NearbyPlacesFinder:

    def __init__(self, gmaps, cache):
        self.gmaps = gmaps
        self.cache = cache

    def __call__(self, location, place_type):
        place_type = place_type.strip()

        cache_key = {
            'nearby_place_finder': {
                'location': location, 'place_type': place_type
            }
        }

        if cache_key in self.cache.data:
            return self.cache.data[cache_key]

        results = self.gmaps.places_nearby(
            location=location, type=place_type, rank_by='distance',
            keyword=place_type,
        )

        results = results['results']

        logger.debug(f'Finding nearby {place_type} places to {location}')

        self.cache.data[cache_key] = results
        return results


class Maps:

    def __init__(self, api_key, cache):
        gmaps = googlemaps.Client(key=api_key)

        self.calculate_travel_time = TravelTimeCalulator(gmaps, cache)
        self.find_latitude_longitude = LatitudeLongitudeFinder(gmaps, cache)
        self.find_nearby_places = NearbyPlacesFinder(gmaps, cache)
