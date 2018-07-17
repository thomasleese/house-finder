import logging


logger = logging.getLogger(__name__)


def output_html(evaluated_listings, objectives, filename):
    logger.info(f'Outputing {len(evaluated_listings)} listings to {filename}')
