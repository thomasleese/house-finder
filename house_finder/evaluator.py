from collections import OrderedDict, UserList
import logging
from typing import Callable, Dict, NamedTuple, Optional

from cached_property import cached_property
import progressbar

from .objectives import Objective
from .search import Listing


logger = logging.getLogger(__name__)


class Score(NamedTuple):
    value: int
    presented_value: str

    def __str__(self):
        return self.presented_value


class EvaluatedListing(NamedTuple):
    listing: Listing
    scores: Dict[str, Optional[Score]]
    constraints: Dict[str, Callable[[float], bool]]

    @property
    def total_score(self):
        return sum(self.scores.values())

    @property
    def is_valid(self):
        return all(self.scores.values())

    @property
    def satisfies_constaints(self):
        return all(f(self.scores[obj].value) for obj, f in self.constraints.items())


class Evaluator(UserList):

    def __init__(self, listings, objectives):
        self.data = [
            self.evaluate_listing(listing, objectives)
            for listing in progressbar.progressbar(listings)
        ]

    def evaluate_listing(self, listing, objectives):
        logger.debug(f'Evaluating {listing.address}')

        scores = OrderedDict()

        for objective in objectives:
            value = objective.calculate(listing)
            if value is None:
                scores[objective.name] = None
            else:
                scores[objective.name] = Score(value, objective.present(value))

        constraints = {
            objective.name: objective.constraint_function
            for objective in objectives
        }

        return EvaluatedListing(
            listing, scores, constraints
        )
