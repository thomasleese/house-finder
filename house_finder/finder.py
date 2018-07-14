import csv
import logging
import os
import shutil
import subprocess
import tempfile
import time
import urllib.parse

from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
import googlemaps
import requests

from .place import Place
from .property import Property
from .searcher import Searcher
from .calculator import TravelTimeCalulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_url(url):
    o = urllib.parse.urlparse(url)
    return o.scheme + '://' + o.netloc + o.path


def generate_property_pdf(property):
    filename = 'outputs/{}.pdf'.format(property.listing.id)

    if not os.path.exists(filename):
        args = ['wkhtmltopdf',
                '--footer-center', clean_url(property.listing.url),
                '-q',
                property.listing.print_url,
                filename]

        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            if not os.path.exists(filename):
                raise

    return filename

def generate_output(filename, properties, constraints):
    filenames = []

    for i, property in enumerate(properties):
        logger.info(f'#{i} -> {property.listing.address} : {property.listing.url}')
        filenames.append(generate_property_pdf(property))

    subprocess.check_call(['pdfunite'] + filenames + [filename])


def optimise(house, secrets, output):
    gmaps = googlemaps.Client(key=secrets['google']['api_key'])
    travel_time_calculator = TravelTimeCalulator(secrets['google']['api_key'])
    searcher = Searcher(secrets, house['search']) # zoopler api

    places = [Place(travel_time_calculator, gmaps, **c) for c in house['places']]

    listings = list(searcher.search())
    logger.info('Found %i listings.', len(listings))

    properties = []

    for i, listing in enumerate(listings):
        property = Property(listing)
        property.apply_constraints(places)
        properties.append(property)
        logger.info(f'#{i} -> {listing.address} : {property.score}')

    properties.sort(key=lambda property: property.score)

    properties = properties[:100]

    generate_output(output, properties, places)
