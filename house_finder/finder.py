import logging
import os
import subprocess
import time
import urllib.parse

from .cache import Cache
from .evaluator import Evaluator, ParetoFront
from .maps import Maps
from .searcher import Searcher
from .objectives import Objective
from .plot import objective_plotter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def clean_url(url):
#     o = urllib.parse.urlparse(url)
#     return o.scheme + '://' + o.netloc + o.path
#
#
# def generate_property_pdf(property):
#     filename = 'outputs/{}.pdf'.format(property.listing.id)
#
#     if not os.path.exists(filename):
#         args = ['wkhtmltopdf',
#                 '--footer-center', clean_url(property.listing.url),
#                 '-q',
#                 property.listing.print_url,
#                 filename]
#
#         try:
#             subprocess.check_call(args)
#         except subprocess.CalledProcessError:
#             if not os.path.exists(filename):
#                 raise
#
#     return filename
#
#
# def generate_output(filename, properties, constraints):
#     filenames = []
#
#     for i, property in enumerate(properties):
#         logger.info(f'#{i} -> {property.listing.address} : {property.listing.url}')
#         filenames.append(generate_property_pdf(property))
#
#     subprocess.check_call(['pdfunite'] + filenames + [filename])


def optimise(house, secrets, output):
    cache = Cache()
    maps = Maps(secrets['google']['api_key'], cache)

    searcher = Searcher(cache, secrets, house['search']) # zoopler api

    objectives = [
        Objective.from_dict(config, maps) for config in house['objectives']
    ]

    listings = list(searcher.search())
    logger.info('Found %i listings.', len(listings))

    listings = listings[:500]

    evaluated_listings = Evaluator(listings, objectives)

    valid_evaluated_listings = [e for e in evaluated_listings if e.is_valid and e.satisfies_constaints]

    logger.info("It's Pareto time!")

    pareto_front = ParetoFront(valid_evaluated_listings)

    objective_plotter(pareto_front, objectives[-1].name, objectives[2].name)

    # generate_output(output, pareto_front, objectives)
