import shelley

from django.contrib.gis import gdal
from django.contrib.gis import geos


class ProjectionFactory(object):

    def adapt(self, srs):
        return srs.visit(self)

    def proj4(self, srs_str):
        return gdal.SpatialReference(srs_str)


sr_factory = ProjectionFactory()


class Geometry(object):

    def __init__(self, django_geometry, target_srs=None):
        self.__dict__.update(locals())

    @property
    def type(self):
        return self.django_geometry.geom_type

    @property
    def coordinates(self):
        if self.target_srs is not None:
            geom_sr = self.django_geometry.srs
            if geom_sr is not None:
                target_sr = sr_factory.adapt(self.target_srs)
                if target_sr != geom_sr:
                    self.django_geometry.transform(target_sr)
        return self.django_geometry.tuple


class Feature(object):

    def __init__(self, obj, geometry_field, target_srs=None):
        self.__dict__.update(locals())

    @property
    def properties(self):
        return self

    def __getitem__(self, key):
        return getattr(self.obj, key)

    @property
    def geometry(self):
        if self.geometry_field is None:
            raise shelley.Error('No field name for default geometry provided')
        return Geometry(getattr(self.obj, self.geometry_field), self.target_srs)


class FeatureSource(object):

    def __init__(self, queryset, geometry_field=None):
        self.__dict__.update(locals())

    def extent(self):
        min_x, min_y, max_x, max_y = self.queryset.extent()
        first_feature = self.queryset[0]
        if self.geometry_field is None:
            raise shelley.Error('No field name for default geometry provided')
        gdal_srs = getattr(first_feature, self.geometry_field).srs
        srs = shelley.SRS.proj4(gdal_srs.proj4)
        return shelley.Box(min_x, min_y, max_x, max_y, srs)
    
    def features(self, srs=None, data_bounds=None):
        qs = self.queryset
        if data_bounds is not None:
            if self.geometry_field is None:
                raise shelley.Error('No geometry field name provided to apply bounds constraint to')
            bounds_geom = geos.Polygon(((data_bounds.min_x, data_bounds.min_y),
                                        (data_bounds.max_x, data_bounds.min_y),
                                        (data_bounds.max_x, data_bounds.max_y),
                                        (data_bounds.min_x, data_bounds.max_y),
                                        (data_bounds.min_x, data_bounds.min_y)))
            kwargs = {'%s__within' % self.geometry_field: bounds_geom}
            qs = qs.filter(**kwargs)
        for obj in qs:
            yield Feature(obj, self.geometry_field, srs)
