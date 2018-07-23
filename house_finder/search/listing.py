from typing import NamedTuple, Tuple


class Listing(NamedTuple):
    id: str
    location: Tuple[float, float]
    price: int
    url: str
    print_url: str
    address: str
    description: str
    image: str
