import logging

import shelley
from shelley.mappers.mapnik import expression


module_logger = logging.getLogger("shelley.mappers.mapnik")


class Map(object):

    PIXEL_SIZE = 0.00028
    
    def __init__(self, layers, background=None, srs=None):
        self.__dict__.update(locals())

    def extent(self):
        layers = iter(self.layers)
        acc_ext = layers.next().extent()
        for layer in layers:
            acc_ext += layer.extent()
        return acc_ext

    def scale(self, drawable):
        width, height = drawable.size()
        return drawable.view_bounds.width / width

    def scale_denominator(self, drawable):
        return self.scale(drawable) / self.PIXEL_SIZE

    def __call__(self, drawable, srs, data_bounds):
        module_logger.info("draw map %r, srs %r, data bounds %r" %
                           (self, srs, data_bounds))
        srs = shelley.SRS.coerce(srs)
        if self.background:
            drawable.background(self.background)
        scale_denominator = self.scale_denominator(drawable)
        for layer in self.layers:
            layer.draw(drawable, srs, scale_denominator, data_bounds)


class Layer(object):

    def __init__(self, name, data_source, styles):
        self.name = name
        self.data_source = data_source
        self.styles = styles

    def __repr__(self):
        return '<Layer 0x%x %s>' % (id(self), self.name)

    def extent(self):
        return self.data_source.extent()
    
    def draw(self, drawable, srs, scale_denominator, data_bounds):
        module_logger.info("draw layer %r" % self.name)
        srs = shelley.SRS.coerce(srs)
        for style in self.styles:
            for feature in self.data_source.features(srs, data_bounds):
                style.draw(feature, drawable, scale_denominator)


class Style(object):

    def __init__(self, name=None, rules=[]):
        self.name = name
        self.rules = rules

    def __repr__(self):
        return 'FeatureStyle(name=%s, rules=%r)' % (self.name, self.rules)

    def draw(self, feature, drawable, scale_denominator):
        rule_applied = False
        for rule in self.rules:
            if (not rule.has_else_filter() and
                rule.matches_scale(scale_denominator) and
                rule.filter.passes(feature)):
                rule_applied = True
                rule.draw(feature, drawable)
        if not rule_applied:
            for rule in self.rules:
                if (rule.has_else_filter() and
                    rule.matches_scale(scale_denominator)):
                    rule.draw(feature, drawable)


class PassingFilter(object):

    def passes(self, feature):
        return True

    def is_else(self):
        return False


passing_filter = PassingFilter()


class Filter(object):

    def __init__(self, expr_str):
        self.expr_str = expr_str
        self.expr = expression.parse(expr_str)

    def __repr__(self):
        return 'Filter(%r)' % self.expr_str

    def passes(self, feature):
        try:
            return self.expr.eval(feature.properties)
        except KeyError:
            return False

    def is_else(self):
        return False


class ElseFilter(object):

    def is_else(self):
        return True


class Rule(object):

    def __init__(self, symbolizers, filter=passing_filter, min_scale_denom=None,
                 max_scale_denom=None):
        self.__dict__.update(locals())

    def __repr__(self):
        return 'Rule(%s, filter=%s, min_scale_denom=%s, max_scale_denom=%s)' % (
            ', '.join(repr(s) for s in self.symbolizers),
            self.filter,
            self.min_scale_denom,
            self.max_scale_denom
        )

    def matches_scale(self, scale_denominator):
        if self.min_scale_denom is not None or self.max_scale_denom is not None:
            return ((self.min_scale_denom is None or
                     scale_denominator >= self.min_scale_denom) and
                    (self.max_scale_denom is None or
                     scale_denominator < self.max_scale_denom))
        else:
            return True

    def draw(self, feature, drawable):
        for symbolizer in self.symbolizers:
            symbolizer.draw(feature, drawable)

    def has_else_filter(self):
        return self.filter.is_else()
