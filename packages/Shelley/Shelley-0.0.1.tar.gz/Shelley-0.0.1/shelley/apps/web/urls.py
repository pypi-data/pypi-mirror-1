from django.conf.urls.defaults import *
from django.conf import settings

from shelley.apps import osm
from shelley.apps.web import views
from shelley.mappers import mapnik


urlpatterns = patterns('django.views.generic.simple',
    (r'^$', 'direct_to_template', {'template': 'shelley/apps/web/viewer.html'}),
)


map = mapnik.parse_xml(settings.MAPNIK_XML)
if settings.OSM_PATCH:
    osm.patch_sql_filter(map)


urlpatterns += patterns('',
    (r'^wms/$', views.wms, {'map': map}),
)

