from cached_property import cached_property

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
        return int(datetime.datetime.utcnow().replace(hour=hour, minute=minute, second=0).timestamp())

    def get_travel_time(self, location):
        search_params = {
            'origin': location,
            'destination': self.name,
            'mode': self.mode,
            'traffic_model': 'pessimistic',
        }

        if self.arrival_time:
            search_params['arrival_time'] = self.format_time(self.arrival_time)

        if self.departure_time:
            search_params['departure_time'] = self.format_time(self.departure_time)

        cache_key = json.dumps(search_params, sort_keys=True)

        if cache_key in cache:
            return cache[cache_key]

        results = self.gmaps.directions(**search_params)

        try:
            leg = results[0]['legs'][0]
            duration = leg['duration']['value']
        except (KeyError, IndexError):
            duration = 1000

        cache[cache_key] = duration
        cache.sync()

        return duration

    def calculate(self, listing):
        return self.get_travel_time(listing.location)
