from enum import Enum
from typing import NamedTuple, Optional


class Range(NamedTuple):
    min: int
    max: int

    @classmethod
    def from_config(cls, config):
        if isinstance(config, list):
            return cls(config[0], config[1])
        elif isinstance(config, int):
            return cls(config, config)
        else:
            raise TypeError('Must be a list or an int.')


class Query(NamedTuple):
    area: str
    listing: str
    no_bedrooms: Range
    price: Range
    shared: bool
    furnished: Optional[bool]
    property: Optional[str]
    new: Optional[bool]

    @classmethod
    def from_config(cls, config):
        return Query(
            config['area'],
            config['listing'],
            Range.from_config(config['bedrooms']),
            Range.from_config(config['price']),
            config.get('shared', False),
            config.get('furnished', None),
            config.get('property', None),
            config.get('new', None),
        )
