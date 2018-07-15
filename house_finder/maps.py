import datetime
import json

import googlemaps


class NoTravelTimeError(Exception):
    pass


class TravelTimeCalulator:

    def __init__(self, gmaps, cache):
        self.gmaps = gmaps
        self.cache = cache

    def __call__(self, **kwargs):
        params = self._create_search_params(**kwargs)
        return self.calculate_time(**params)

    def _format_time(self, string):
        hour, minute = [int(x) for x in string.split(':')]
        return int(
            datetime.datetime.utcnow() \
                .replace(hour=hour, minute=minute, second=0) \
                .timestamp()
        )

    def calculate_time(self, **params):
        if params in self.cache.data:
            duration = self.cache.data[params]
        else:
            duration = self._extract_duration(
                self.gmaps.directions(**params)
            )

            self.cache.data[params] = duration

        return duration

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


class Maps:

    def __init__(self, api_key, cache):
        self.gmaps = gmaps = googlemaps.Client(key=api_key)

        self.calculate_travel_time = TravelTimeCalulator(gmaps, cache)
