import logging
import os

import shelley


DEBUG = True
TEMPLATE_DIRS = (os.path.dirname(os.path.dirname(shelley.__file__)),)
TEMPLATE_DEBUG = DEBUG
ROOT_URLCONF = 'shelley.apps.web.urls'

MAPNIK_XML = '/home/gcarlyle/data/osm/mapnik/osm.xml'
OSM_PATCH = True

logging.basicConfig(level=logging.DEBUG,)
