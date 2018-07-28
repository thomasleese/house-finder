import logging
from pathlib import Path
import webbrowser

from jinja2 import Environment, PackageLoader, select_autoescape


logger = logging.getLogger(__name__)


def average(things):
    return sum(things) / len(things)


def calculate_centre(evaluated_listings):
    return (
        average([e.listing.location[0] for e in evaluated_listings]),
        average([e.listing.location[1] for e in evaluated_listings]),
    )


def output_html(secrets, evaluated_listings, objectives, filename):
    logger.info(f'Outputing {len(evaluated_listings)} listings to {filename}')

    env = Environment(
        loader=PackageLoader('house_finder', 'outputs'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open(filename, 'w') as file:
        file.write(template.render(
            secrets=secrets,
            evaluated_listings=evaluated_listings,
            objectives=objectives,
            centre=calculate_centre(evaluated_listings),
        ))

    webbrowser.open(Path(filename).resolve().as_uri())
