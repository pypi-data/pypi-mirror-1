from osgeo import ogr, osr

import shelley
from shelley import utils


class OSRProjectionFactory(object):

    def adapt(self, srs):
        return srs.visit(self)

    def proj4(self, srs_str):
        sr = osr.SpatialReference()
        sr.ImportFromProj4(srs_str)
        return sr


sr_factory = OSRProjectionFactory()


def point_coords(geometry, point_index=0):
    return (geometry.GetX(point_index), geometry.GetY(point_index))


def line_coords(ogr_geometry):
    for i in range(ogr_geometry.GetPointCount()):
        yield point_coords(ogr_geometry, i)


def composite_coords(geometry, geom_ref_callable):
    for i in range(geometry.GetGeometryCount()):
        geom_ref = geometry.GetGeometryRef(i)
        yield geom_ref_callable(geom_ref)


def multi_point_coords(geometry):
    return composite_coords(geometry, point_coords)
            

def polygon_coords(geometry):
    return composite_coords(geometry, line_coords)


def multi_polygon_coords(geometry):
    return composite_coords(geometry, polygon_coords)


class Transformer(object):

    # python osr bindings don't make the destination sr of a
    # CoordinateTransformation available so need a wrapper to detect a failed
    # transformation

    def __init__(self, src_sr, dst_sr):
        self.__dict__.update(locals())

    def transform(self, ogr_geometry):
        transformation = osr.CoordinateTransformation(self.src_sr, self.dst_sr)
        ogr_geometry.Transform(transformation)
        # ogr may fail to transform if some points can be projected
        return (ogr_geometry.GetSpatialReference().ExportToWkt() ==
                self.dst_sr.ExportToWkt())


class Geometry(object):

    _geometries = {ogr.wkbPoint: ('Point', point_coords),
                   ogr.wkbMultiPoint: ('MultiPoint', multi_point_coords),
                   ogr.wkbLineString: ('LineString', line_coords),
                   ogr.wkbPolygon: ('Polygon', polygon_coords),
                   ogr.wkbMultiLineString: ('MultiLineString', polygon_coords),
                   ogr.wkbMultiPolygon: ('MultiPolygon', multi_polygon_coords)}
    
    def __init__(self, ogr_geometry, transformer):
        self.ogr_geometry = ogr_geometry
        self.transformer = transformer

    def get_geometry(self):
        return self._ogr_geometry

    def set_geometry(self, ogr_geometry):
        self._ogr_geometry = ogr_geometry
        ogr_type = ogr_geometry.GetGeometryType()
        self.type, coords_callable = self._geometries[ogr_type]
        self._coords_callable = coords_callable
    
    ogr_geometry = property(get_geometry, set_geometry)

    @property
    def coordinates(self):
        if self.transformer is not None:
            if not self.transformer.transform(self.ogr_geometry):
                return []
        return self._coords_callable(self.ogr_geometry)

    def midpoint(self):
        if self.type == 'LineString':
            # python binding doesn't seem to support get_Length & Value
            return utils.midpoint(self.coordinates)
        raise shelley.UnsuitableGeometry("can't determine midpoint of %s" %
                                         self.type)

    def centroid(self):
        if self.type == 'Polygon':
            self.ogr_geometry.CloseRings()
            point = self.ogr_geometry.Centroid()
            return [point.GetX(), point.GetY()]
        raise shelley.UnsuitableGeometry("can't determine centroid of %s" %
                                         self.type)


class Feature(object):

    def __init__(self, ogr_feature, transformer=None):
        self.ogr_feature = ogr_feature
        self.transformer = transformer

    @property
    def properties(self):
        return self

    def __getitem__(self, name):
        try:
            return self.ogr_feature.GetField(name)
        except ValueError:
            raise KeyError(name)

    @property
    def geometry(self):
        ogr_geometry = self.ogr_feature.GetGeometryRef()
        return Geometry(ogr_geometry, self.transformer)


def box_to_geometry(box):
    ll = '%f %f' % (box.min_x, box.min_y)
    ul = '%f %f' % (box.min_x, box.max_y)
    ur = '%f %f' % (box.max_x, box.max_y)
    lr = '%f %f' % (box.max_x, box.min_y)
    geometry = ogr.CreateGeometryFromWkt('POLYGON ((%s,%s,%s,%s,%s))' %
                                         (ll, ul, ur, lr, ll))
    if box.srs:
        box_sr = sr_factory.adapt(box.srs)
        geometry.AssignSpatialReference(box_sr)
    return geometry


class FeatureSource(object):

    def __init__(self, name, driver=None, layer_name=None, sql=None,
                 sql_filter=None):
        self.__dict__.update(locals())

    def __repr__(self):
        params = ['%s=%r' % (p, getattr(self, p))
                  for p in ['name', 'driver', 'layer_name', 'sql', 'sql_filter']
                  if getattr(self, p)]
        return 'FeatureSource(%s)' % ', '.join(params)

    def _open(self):
        if self.driver is not None:
            driver = ogr.GetDriverByName(self.driver)
            if driver is None:
                raise shelley.InvalidDataSourceError('Unknown driver, %r' %
                                                     self)
            ds = driver.Open(self.name)
        else:
            ds = ogr.Open(self.name)
        if ds is None:
            raise shelley.InvalidDataSourceError("Can't open %r" % self)
        return ds

    def _retrieve_sql_layer(self, ds, data_bounds):
        # ExecuteSQL often ignores spatial filter parameter so rely on callback
        # to change sql to filter by view
        sql = self.sql
        if self.sql_filter:
            sql = self.sql_filter(sql, data_bounds)
        layer = ds.ExecuteSQL(sql)
        if layer is None:
            raise shelley.InvalidDataSourceError(
                'Failed to retrieve layer from sql: %r' % sql
            )
        return layer

    def _retrieve_name_layer(self, ds, data_bounds):
        if self.layer_name is None:
            layer_count = ds.GetLayerCount()
            if layer_count > 1:
                raise shelley.InvalidDataSourceError(
                    'data source contains %d layers but no layer name provided'
                    ', %r' % (layer_count, self)
                )
            layer = ds.GetLayer()
        else:
            layer = ds.GetLayerByName(self.layer_name)
        if layer is None:
            raise shelley.InvalidDataSourceError("Can't access layer, %r" %
                                                 self)
        if data_bounds is not None:
            bounds_geometry = box_to_geometry(data_bounds)
            if data_bounds.srs is not None:
                layer_sr = layer.GetSpatialRef()
                if layer_sr is not None:
                    bounds_geometry.TransformTo(layer_sr)
            layer.SetSpatialFilter(bounds_geometry)
        return layer

    def _retrieve_layer(self, data_bounds=None):
        ds = self._open()
        if self.sql is not None:
            layer = self._retrieve_sql_layer(ds, data_bounds)
        else:
            layer = self._retrieve_name_layer(ds, data_bounds)
        return ds, layer

    def _close_layer(self, ds, layer):
        if self.sql:
            ds.ReleaseResultSet(layer)
        ds.Destroy()

    def extent(self):
        ds, layer = self._retrieve_layer()
        layer_sr = layer.GetSpatialRef()
        min_x, max_x, min_y, max_y = layer.GetExtent()
        if layer_sr is not None:
            srs = shelley.SRS.proj4(layer_sr.ExportToProj4())
        else:
            srs = None
        self._close_layer(ds, layer)
        return shelley.Box(min_x, min_y, max_x, max_y, srs)

    def features(self, srs=None, data_bounds=None):
        ds, layer = self._retrieve_layer(data_bounds)
        transformer = None
        if srs is not None:
            layer_sr = layer.GetSpatialRef()
            if layer_sr is not None:
                view_sr = sr_factory.adapt(srs)
                transformer = Transformer(layer_sr, view_sr)
        ogr_feature = layer.GetNextFeature()
        while ogr_feature is not None:
            yield Feature(ogr_feature, transformer)
            ogr_feature.Destroy()
            ogr_feature = layer.GetNextFeature()
        self._close_layer(ds, layer)
