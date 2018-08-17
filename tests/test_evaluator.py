from collections import OrderedDict
import unittest

from house_finder.evaluator import EvaluatedListing, ParetoFront


class TestParetoFront(unittest.TestCase):

    def test_works(self):
        in_pareto_1 = EvaluatedListing(None, OrderedDict(x=0, y=0), constraints={})
        in_pareto_2 = EvaluatedListing(None, OrderedDict(x=1, y=0), constraints={})
        in_pareto_3 = EvaluatedListing(None, OrderedDict(x=0, y=1), constraints={})
        not_in_pareto = EvaluatedListing(None, OrderedDict(x=1, y=1), constraints={})

        evaluated_listings = [
            in_pareto_1, in_pareto_2, in_pareto_3, not_in_pareto,
        ]

        results = ParetoFront(evaluated_listings)

        self.assertEqual(len(results), 3)
        self.assertIn(in_pareto_1, results)
        self.assertIn(in_pareto_2, results)
        self.assertIn(in_pareto_3, results)
        self.assertNotIn(not_in_pareto, results)
