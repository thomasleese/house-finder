from collections import OrderedDict, UserList
import logging
from typing import Dict, NamedTuple

from cached_property import cached_property
import numpy as np

from .objectives import Objective
from .searcher import Listing


logger = logging.getLogger(__name__)


class EvaluatedListing(NamedTuple):
    listing: Listing
    scores: Dict[Objective, float]

    @property
    def total_score(self):
        return sum(self.scores.values())

    @property
    def is_valid(self):
        return all(self.scores.values())


class Evaluator(UserList):

    def __init__(self, listings, objectives):
        self.data = self.evaluated_listings(listings, objectives)

    def evaluate_listing(self, listing, objectives):
        logger.info(f'Evaluating {listing.address}')

        scores = OrderedDict([
            (objective.name, objective.calculate(listing))
            for objective in objectives
        ])

        return EvaluatedListing(
            listing, scores
        )

    def evaluated_listings(self, listings, objectives):
        return [
            self.evaluate_listing(listing, objectives)
            for listing in listings
        ]


class ParetoFront(UserList):

    def __init__(self, evaluated_listings):
        self.evaluated_listings = evaluated_listings
        self.data = [
            evaluated_listing
            for i, evaluated_listing in enumerate(evaluated_listings)
            if self._pareto_front[i]
        ]

    @cached_property
    def score_table(self):
        return np.array([list(e.scores.values()) for e in self.evaluated_listings])

    @cached_property
    def _pareto_front(self):
        """
        :param costs: An (n_points, n_costs) array
        :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
        """
        is_pareto = np.ones(self.score_table.shape[0], dtype = bool)
        for i, c in enumerate(self.score_table):
            if is_pareto[i]:
                is_pareto[is_pareto] = np.any(self.score_table[is_pareto]<=c, axis=1)  # Remove dominated points
        return is_pareto


def rank(evaluated_listings):
    return evaluated_listings
