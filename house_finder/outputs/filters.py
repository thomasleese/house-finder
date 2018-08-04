from collections import UserList
import logging

from cached_property import cached_property
import numpy as np


logger = logging.getLogger(__name__)


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
        return np.array([
            [score.value for score in e.scores.values()]
            for e in self.evaluated_listings
        ])

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


class RankEvaluator(UserList):

    def __init__(self, evaluated_listings):
        logger.info("It's Pareto time!")

        evaluated_listings = list(evaluated_listings)  # make a copy

        self.data = []

        while evaluated_listings:
            pareto_front = ParetoFront(evaluated_listings)
            for e in pareto_front:
                evaluated_listings.remove(e)
            self.data.append(pareto_front)

        logger.info(f'Filtered down to {len(self.data)} pareto fronts.')
