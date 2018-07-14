import datetime
import json
import shelve

import googlemaps


class TravelTimeCalulator:

    def __init__(self, api_key):
        self.cache = shelve.open('travel_times.db')
        self.maps = googlemaps.Client(key=api_key)

    def __call__(self, **kwargs):
        params = self._create_search_params(**kwargs)
        return self.calculate_time(**params)

    def __del__(self):
        self.cache.close()

    def _format_time(self, string):
        hour, minute = [int(x) for x in string.split(':')]
        return int(
            datetime.datetime.utcnow() \
                .replace(hour=hour, minute=minute, second=0) \
                .timestamp()
        )

    def calculate_time(self, **params):
        cache_key = json.dumps(params, sort_keys=True)

        if cache_key in self.cache:
            duration = self.cache[cache_key]
        else:
            duration = self._extract_duration(
                self.maps.directions(**params)
            )

            self.cache[cache_key] = duration
            self.cache.sync()

        return duration

    def _extract_duration(self, result):
        try:
            leg = results[0]['legs'][0]
            return leg['duration']['value']
        except (KeyError, IndexError):
            return 1000


    def _create_search_params(self, origin, destination, mode, arrival_time, departure_time):
        params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'traffic_model': 'pessimistic',
        }

        if arrival_time:
            params['arrival_time'] = self._format_time(arrival_time)

        if departure_time:
            params['departure_time'] = self._format_time(departure_time)

        return params
