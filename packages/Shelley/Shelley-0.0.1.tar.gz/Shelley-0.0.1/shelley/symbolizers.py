import shelley


def iter_lines(geometry):
    if geometry.type == 'LineString':
        yield geometry.coordinates
    elif geometry.type in ['Polygon', 'MultiLineString']:
        for line in geometry.coordinates:
            yield line
    elif geometry.type == 'MultiPolygon':
        for polygon in geometry.coordinates:
             for line in polygon:
                  yield line
    elif geometry.type in ['Point', 'MultiPoint']:
        return
    else:
         raise shelley.UnrecognisedGeometry(geometry.type)


def iter_polygons(geometry):
    if geometry.type == 'Polygon':
        yield geometry.coordinates
    elif geometry.type == 'MultiPolygon':
        for polygon in geometry.coordinates:
            yield polygon


def is_closed(geometry):
    return geometry.type in ['Polygon', 'MultiPolygon']


class LineSymbolizer(object):

    def __init__(self,
                 color='black',
                 width=1.0,
                 cap='butt',
                 join='miter',
                 dash=[]):
        self.color = color
        self.width = width
        self.cap = cap
        self.join = join
        self.dash = dash

    def __repr__(self):
        return (
            '%s(color=%r, width=%r, cap=%r, join=%r, dash=%r)' %
            (self.__class__.__name__, 
             self.color,
             self.width,
             self.cap,
             self.join,
             self.dash)
        )

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = shelley.Color.coerce(color)

    color = property(get_color, set_color)

    def draw(self, feature, drawable):
        for line in iter_lines(feature.geometry):
            drawable.draw_line(line, self, is_closed(feature.geometry))


class PolygonSymbolizer(object):

    def __init__(self, color='black'):
        self.color = color

    def __repr__(self):
        return '%s(color=%r)' % (self.__class__.__name__, self.color)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = shelley.Color.coerce(color)

    color = property(get_color, set_color)

    def draw(self, feature, drawable):
        for polygon in iter_polygons(feature.geometry):
            drawable.draw_polygon(polygon, self)


class TextSymbolizer(object):

    def __init__(self, property_name, face_name, size,
                 color='black',
                 placement='point',
                 halo_radius=None,
                 halo_color='white'):
        self.property_name = property_name
        self.face_name = face_name
        self.size = size
        self.color = color
        self.placement = placement
        self.halo_radius = halo_radius
        self.halo_color = halo_color

    def __repr__(self):
        return (
            '%s(property_name=%r, face_name=%r, size=%r, color=%r, '
               'placement=%r, halo_radius=%r, halo_color=%r)' %
            (self.__class__.__name__,
             self.property_name,
             self.face_name,
             self.size,
             self.color,
             self.placement,
             self.halo_radius,
             self.halo_color)
        )
    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = shelley.Color.coerce(color)

    color = property(get_color, set_color)

    def get_halo_color(self):
        return self._halo_color

    def set_halo_color(self, color):
        self._halo_color = shelley.Color.coerce(color)

    halo_color = property(get_halo_color, set_halo_color)

    def draw(self, feature, drawable):
        value = feature.properties[self.property_name]
        if value is None:
            return
        else:
            value = unicode(value)
        if self.placement == 'line':
            if feature.geometry.type == 'LineString':
                line = list(feature.geometry.coordinates) # TODO remove list here, if needed do in called
                drawable.draw_line_text(value, line, self)
        else:
            point = None
            if feature.geometry.type == 'Point':
                point = list(feature.geometry.coordinates)
            elif feature.geometry.type == 'LineString':
                point = feature.geometry.midpoint()
            if feature.geometry.type == 'Polygon':
                point = feature.geometry.centroid()
            if point is not None:
                drawable.draw_point_text(value, point, self)

