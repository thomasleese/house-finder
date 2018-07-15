from collections import abc
import json
import logging
from pathlib import Path
import shelve

import requests_cache


logger = logging.getLogger(__name__)


class DictCache(abc.MutableMapping):
    """
    A cache that looks like a dictionary. Uses 'shelve' underneath but allows
    dict keys.
    """

    def __init__(self, filename):
        self.shelf = shelve.open(filename)

    def __del__(self):
        self.shelf.close()

    def _make_key(self, key):
        if isinstance(key, dict):
            return json.dumps(key, sort_keys=True)
        else:
            return key

    def __getitem__(self, key):
        return self.shelf[self._make_key(key)]

    def __setitem__(self, key, value):
        self.shelf[self._make_key(key)] = value
        self.shelf.sync()

    def __delitem__(self, key):
        del self.shelf[self._make_key(key)]

    def __contains__(self, key):
        return self._make_key(key) in self.shelf

    def __iter__(self):
        return iter(self.shelf)

    def __len__(self):
        return len(self.shelf)


class Cache:
    """
    An application wide cache, it provides a dict cache as a 'data' attribute
    and a requests session cache as a 'requests_session' attribute.
    """

    expiration = 24 * 60 * 60  # 1 day

    def __init__(self, directory: str = 'caches'):
        directory = Path(directory)

        directory.mkdir(parents=True, exist_ok=True)

        logger.debug(f'Loading caches from {directory}')

        self.requests_session = requests_cache.CachedSession(
            cache_name=str(directory / 'requests'),
            backend='sqlite',
            expire_after=self.expiration,
        )

        self.data = DictCache(str(directory / 'data.db'))
