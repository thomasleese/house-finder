import logging
from pathlib import Path
import webbrowser

from jinja2 import Environment, PackageLoader, select_autoescape


logger = logging.getLogger(__name__)


def output_html(evaluated_listings, objectives, filename):
    logger.info(f'Outputing {len(evaluated_listings)} listings to {filename}')

    env = Environment(
        loader=PackageLoader('house_finder', 'outputs'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open(filename, 'w') as file:
        file.write(template.render(
            evaluated_listings=evaluated_listings,
            objectives=objectives,
        ))

    webbrowser.open(Path(filename).resolve().as_uri())
