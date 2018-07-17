import logging

from .cache import Cache
from .evaluator import Evaluator, ParetoFront
from .maps import Maps
from .searcher import Searcher
from .objectives import Objective
from .output import output_html, output_plot


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def optimise(house, secrets, output):
    cache = Cache()
    maps = Maps(secrets['google']['api_key'], cache)

    searcher = Searcher(cache, secrets, house['search']) # zoopler api

    objectives = [
        Objective.from_dict(config, maps) for config in house['objectives']
    ]

    listings = list(searcher.search())
    logger.info('Found %i listings.', len(listings))

    evaluated_listings = Evaluator(listings, objectives)

    valid_evaluated_listings = [
        e for e in evaluated_listings if e.is_valid and e.satisfies_constaints
    ]

    logger.info("It's Pareto time!")

    pareto_front = ParetoFront(valid_evaluated_listings)

    logger.info(f'Filtered down to {len(pareto_front)} listings')

    output_html(pareto_front, objectives, output)
    # output_plot(pareto_front, objectives)
