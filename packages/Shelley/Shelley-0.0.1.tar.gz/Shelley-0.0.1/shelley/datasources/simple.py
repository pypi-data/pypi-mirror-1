import shelley
from shelley import utils


class Geometry(object):

    def __init__(self, type, coordinates):
        self.__dict__.update(locals())

    def midpoint(self):
        if self.type == 'LineString':
            return utils.midpoint(self.coordinates)
        raise shelley.UnsuitableGeometry("can't determine midpoint of %s" %
                                         self.type)

    def centroid(self):
        if self.type == 'Polygon':
            return utils.centroid(self.coordinates[0])
        raise shelley.UnsuitableGeometry("can't determine centroid of %s" %
                                         self.type)


class Feature(object):

    def __init__(self, geometry=None, properties={}):
        self.__dict__.update(locals())


class TransformedGeometry(object):

    def __init__(self, geometry, transformer):
        self.__dict__.update(locals())
        self.type = geometry.type

    @property
    def coordinates(self):
        accessor = self.accessor[self.geometry.type]
        return accessor(self, self.geometry.coordinates)

    def point_coords(self, point):
        return self.transformer.transform(*point)

    def line_coords(self, coordinates):
        for point in coordinates:
            yield self.point_coords(point)

    def composite_coords(self, coordinates, part_callable):
        for part in coordinates:
            yield part_callable(part)

    def multi_point_coords(self, coordinates):
        return self.composite_coords(coordinates, self.point_coords)

    def polygon_coords(self, coordinates):
        return self.composite_coords(coordinates, self.line_coords)

    def multi_polygon_coords(self, coordinates):
        return self.composite_coords(coordinates, self.polygon_coords)

    accessor = {'Point': point_coords,
                'MultiPoint': multi_point_coords,
                'LineString': line_coords,
                'Polygon': polygon_coords,
                'MultiLineString': polygon_coords,
                'MultiPolygon': multi_polygon_coords}


class TransformedFeature(object):

    def __init__(self, feature, transformer):
        self.__dict__.update(locals())

    @property
    def geometry(self):
        return TransformedGeometry(self.feature.geometry, self.transformer)

    def __getattr__(self, attr_name):
        return getattr(self.feature, attr_name)


class FeatureSource(object):

    def __init__(self, features=[], srs=None):
        self._features = features
        self.srs = srs

    def _transformed_features(self, to_srs):
        transformer = self.srs.transformer(to_srs)
        for feature in self._features:
            yield TransformedFeature(feature, transformer)


    def features(self, srs=None, data_bounds=None):
        if srs is not None and self.srs is not None:
            return self._transformed_features(srs)
        else:
            return self._features
