from collections import UserList
from typing import Dict, NamedTuple

from .objectives import Objective
from .searcher import Listing


class EvaluatedListing:
    listing: Listing
    scores: Dict[Objective, float]

    @property
    def total_score(self):
        return sum(scores.values())


class Evaluator(UserList):

    def __init__(self, listings, objectives):
        self.data = [
            self.evaluate_listing(listing, objectives)
            for listing in listings
        ]

    def evaluate_listing(self, listing, objectives):
        scores = {
            objective: objective.calculate(listing)
            for objective in objectives
        }

        return EvaluatedListing(
            listing, scores
        )


def pareto_front(evaluated_listings):
    return evaluated_listings


def rank(evaluated_listings):
    return evaluated_listings
