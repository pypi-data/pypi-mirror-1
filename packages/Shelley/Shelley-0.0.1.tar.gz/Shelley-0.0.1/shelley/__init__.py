import pyproj
import re

import shelley.namedcolors


class Error(Exception):
    pass


class InvalidDataSourceError(Error):
    pass


class UnrecognisedGeometry(Error):
    pass


class UnsuitableGeometry(Error):
    pass


class InvalidProjection(Error):
    pass


class FailedProjectionError(Error):
    pass


class Color(object):

    hexrgb_re = re.compile(
        '^#?([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$'
    )

    def __init__(self, red, green, blue):
        self.__dict__.update(locals())

    def __repr__(self):
         return ('Color(red=%d, green=%d, blue=%d)' %
                 (self.red, self.green, self.blue))

    @classmethod
    def hexrgb(cls, hexstr):
        match = cls.hexrgb_re.match(hexstr)
        if not match:
            raise ValueError(match)
        hexstr = match.groups()[0]
        len_hexpart = len(hexstr) / 3
        parts = []
        for i in range(0, len(hexstr), len_hexpart):
            hexpart = hexstr[i:i + len_hexpart]
            if len_hexpart == 1:
                hexpart *= 2
            parts.append(int(hexpart, 16))
        return Color(*parts)

    @classmethod
    def names(cls):
        return shelley.namedcolors.named_rgbs.keys()

    @classmethod
    def name(cls, name):
        return Color(*shelley.namedcolors.named_rgbs[name])

    @classmethod
    def parse(cls, colstr):
        try:
            return cls.hexrgb(colstr)
        except ValueError:
            try:
                return cls.name(colstr)
            except KeyError:
                raise Error("Can't parse colour string: %r" % colstr)

    @classmethod
    def coerce(cls, obj):
        if isinstance(obj, basestring):
            return cls.parse(obj)
        else:
            return obj


class SRS(object):

    def __init__(self, value):
        # we only support proj4 at the moment
        self.value = value

    def get_value(self):
        return self._value

    def set_value(self, value):
        if isinstance(value, pyproj.Proj):
            self._pypj = value
            self._value = value.srs
        else:
            try:
                self._pypj = pyproj.Proj(value)
            except RuntimeError, e:
                raise InvalidProjection('%s: %r' % (', '.join(e.args), value))
            self._value = value

    value = property(get_value, set_value)

    def __repr__(self):
        return 'SRS.proj4(%r)' % self.value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not (self == other)

    def visit(self, visitor):
        return visitor.proj4(self.value)

    @classmethod
    def proj4(self, value):
        return SRS(value)

    @classmethod
    def pyproj(self, instance):
        return SRS(instance)

    def transform(self, to_srs, x, y):
        try:
            return pyproj.transform(self._pypj, to_srs._pypj, x, y)
        except RuntimeError, e:
            raise FailedProjectionError(*e.args)

    def transformer(self, to_srs):
        return Transformer(self, to_srs)

    @classmethod
    def coerce(cls, obj):
        if isinstance(obj, basestring):
            return cls.proj4(obj)
        elif isinstance(obj, pyproj.Proj):
            return cls.pyproj(obj)
        else:
            return obj


class Transformer(object):

    def __init__(self, from_srs, to_srs):
        self.__dict__.update(locals())

    def transform(self, x, y):
        return self.from_srs.transform(self.to_srs, x, y)


class Box(object):

    def __init__(self, min_x, min_y, max_x, max_y, srs=None):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.srs = srs

    def get_srs(self):
        return self._srs

    def set_srs(self, srs):
        if srs is not None:
            self._srs = SRS.coerce(srs)
        else:
            self._srs = None

    srs = property(get_srs, set_srs)

    def __repr__(self):
        if self.srs is not None:
            srs_str = ', srs=%r' % self.srs
        else:
            srs_str = ''
        return ('Box(%r, %r, %r, %r%s)' %
                (self.min_x, self.min_y, self.max_x, self.max_y, srs_str))

    def __add__(self, other):
        if self.srs != other.srs:
            raise ValueError("can't add boxs with differing srs: %r, %r" %
                             (self.srs, other.srs))
        return Box(min(self.min_x, other.min_x),
                   min(self.min_y, other.min_y),
                   max(self.max_x, other.max_x),
                   max(self.max_y, other.max_y),
                   self.srs)

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y

    @property
    def center(self):
        return (self.min_x + self.width / 2.0, self.min_y + self.height / 2.0)

    @property
    def ratio(self):
        return float(self.width) / self.height

    def with_ratio(self, ratio):
        if self.ratio < ratio:
            new_width = ratio / self.ratio * self.width
            width_delta = new_width - self.width
            box = Box(self.min_x - width_delta / 2,
                      self.min_y,
                      self.max_x + width_delta / 2,
                      self.max_y,
                      self.srs)
        elif self.ratio > ratio:
            new_height = self.ratio / ratio * self.height
            height_delta = new_height - self.height
            box = Box(self.min_x,
                      self.min_y - height_delta / 2,
                      self.max_x,
                      self.max_y + height_delta / 2,
                      self.srs)
        else:
            box = Box(self.min_x, self.min_y, self.max_x, self.max_y, self.srs)
        return box

    def transform(self, to_srs):
        if self.srs is None:
            raise Error('box has no srs to transform from')
        x = (self.min_x, self.max_x)
        y = (self.min_y, self.max_y)
        t_x, t_y = self.srs.transform(to_srs, x, y)
        return Box(t_x[0], t_y[0], t_x[1], t_y[1], to_srs)


class FromView():

    def __repr__(self):
        return '(from view)'


from_view = FromView()


def draw(mapper, view, drawable, preserve_ratio=True, data_bounds=from_view):
    if preserve_ratio:
        view = view.with_ratio(drawable.ratio)
    if data_bounds is from_view:
        data_bounds = view
    drawable.src(view)
    mapper(drawable, view.srs, data_bounds=data_bounds)


def render(mapper, view, format, preserve_ratio=True, data_bounds=from_view):
    target = format()
    draw(mapper,
         view,
         target.get_drawable(),
         preserve_ratio,
         data_bounds=data_bounds)
    target.finish()
