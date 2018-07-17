from argparse import ArgumentParser
import logging

import yaml

from .cache import Cache
from .evaluator import Evaluator, ParetoFront
from .maps import Maps
from .searcher import Searcher
from .objectives import Objective
from .outputs import output_html, output_plot


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('--input', '-i', help='input yaml file with search specifications')
    parser.add_argument('--secrets', '-s', help='yaml file containing passcodes and keys')
    parser.add_argument('--output', '-o', help='output file path')
    args = parser.parse_args()

    return load_yaml(args.input), load_yaml(args.secrets), args.output


def load_yaml(file_path):
    with open(file_path) as file:
        return yaml.load(file)


def main():
    input, secrets, output = parse_arguments()

    cache = Cache()
    maps = Maps(secrets['google']['api_key'], cache)

    searcher = Searcher(cache, secrets, input['search']) # zoopler api

    objectives = [
        Objective.from_dict(config, maps) for config in input['objectives']
    ]

    listings = list(searcher.search())
    logger.info('Found %i listings.', len(listings))

    # listings = listings[:1000]

    evaluated_listings = Evaluator(listings, objectives)

    valid_evaluated_listings = [
        e for e in evaluated_listings if e.is_valid and e.satisfies_constaints
    ]

    logger.info("It's Pareto time!")

    pareto_front = ParetoFront(valid_evaluated_listings)

    logger.info(f'Filtered down to {len(pareto_front)} listings')

    output_html(pareto_front, objectives, output)
    # output_plot(pareto_front, objectives)
