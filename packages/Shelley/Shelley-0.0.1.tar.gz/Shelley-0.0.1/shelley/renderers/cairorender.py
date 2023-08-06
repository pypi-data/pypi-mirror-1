import functools
import math

import cairo
import pango
import pangocairo


def line_metrics(coordinates):
    lengths = []
    angles = []
    last_pos = coordinates[0]
    for pos in coordinates[1:]:
        length = math.sqrt((pos[1] - last_pos[1]) ** 2 + (pos[0] - last_pos[0]) ** 2)
        lengths.append(length)
        angles.append(math.atan2(pos[1] - last_pos[1], pos[0] - last_pos[0]))
        last_pos = pos
    return lengths, angles


def text_line_positions(coordinates, width, height, spacing):
    lengths, angles = line_metrics(coordinates)
    total_length = sum(lengths)
    if total_length < width:
        return
    offset = total_length / 2.0 - width / 2.0
    segment = 0
    text_length = len(spacing) + 1
    for i in range(text_length):
        while offset >= lengths[segment]:
            offset -= lengths[segment]
            segment += 1
        x = math.cos(angles[segment]) * offset + coordinates[segment][0]
        y = math.sin(angles[segment]) * offset + coordinates[segment][1]
        x_delta = math.cos(angles[segment] - math.pi / 2) * height / 2
        y_delta = math.sin(angles[segment] - math.pi / 2) * height / 2
        yield x - x_delta, y - y_delta, angles[segment]
        if i < len(spacing):
            offset += spacing[i]



class SurfaceTarget(object):

    def __init__(self, surface):
        self.surface = surface
        self.context = cairo.Context(self.surface)
        self.pango_context = pangocairo.CairoContext(self.context)

    def get_drawable(self):
        return Drawable(self.pango_context, self.width, self.height)

    def finish(self):
        pass


def Image(width, height, path):
    return functools.partial(ImageTarget, width, height, path)


class ImageTarget(SurfaceTarget):

    def __init__(self, width, height, path):
        self.path = path
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        super(ImageTarget, self).__init__(surface)

    @property
    def width(self):
        return self.surface.get_width()

    @property
    def height(self):
        return self.surface.get_height()

    def finish(self):
        self.surface.flush()
        self.surface.write_to_png(self.path)
        self.surface.finish()


class SimplePathTarget(SurfaceTarget):

    def __init__(self, surface_class_, width, height, path):
        surface = surface_class_(path, width, height)
        super(SimplePathTarget, self).__init__(surface)
        self.width = width
        self.height = height

    def finish(self):
        self.surface.flush()
        self.surface.finish()


def SVG(width, height, path):
    return functools.partial(SimplePathTarget, 
                             cairo.SVGSurface,
                             width,
                             height,
                             path)


def PDF(width, height, path):
    return functools.partial(SimplePathTarget,
                             cairo.PDFSurface,
                             width,
                             height,
                             path)


def Postscript(width, height, path):
    return functools.partial(SimplePathTarget,
                             cairo.PSSurface,
                             width,
                             height,
                             path)


def line_path(context, line, is_closed):
    points = iter(line)
    x, y = points.next()
    context.move_to(x, y)
    for x, y in points:
        context.line_to(x, y)
    if is_closed:
        context.close_path()


def line_cap_style(name):
    return getattr(cairo, 'LINE_CAP_%s' % name.upper())


def line_join_style(name):
    return getattr(cairo, 'LINE_JOIN_%s' % name.upper())


class Drawable(object):

    pixel_width = 0.00028
    dpi = 96.0
    
    def __init__(self, context, width, height):
        self.context = context
        self.width = width
        self.height = height
        self.view_bounds = None

    @property
    def ratio(self):
        return float(self.width) / self.height
    
    def src(self, view_bounds):
        self.view_bounds = view_bounds
        width_scale = self.width / float(view_bounds.width)
        height_scale = self.height / float(view_bounds.height)
        self.context.translate(
            -view_bounds.min_x * width_scale,
            view_bounds.max_y * height_scale
        )
        self.context.scale(width_scale, -height_scale)

    def map_distance(self, dus):
        x, y = self.context.device_to_user_distance(dus, dus)
        return x, y

    def map_length(self, dus):
        x, y = self.map_distance(dus)
        return float(abs(x) + abs(y)) / 2

    def size(self):
        return self.width, self.height

    def scale(self):
        return float(self.view_bounds.width) / self.width / self.pixel_width

    def _rgb_tuple(self, color):
        return tuple(float(part) / 255
                     for part in (color.red, color.green, color.blue))

    def background(self, color):
        self.context.save()
        self.context.rectangle(self.view_bounds.min_x, self.view_bounds.min_y,
                               self.view_bounds.width, self.view_bounds.height)
        self.context.set_source_rgb(*self._rgb_tuple(color))
        self.context.fill()
        self.context.restore()

    def draw_line(self, line, symbolizer, is_closed=False):
        self.context.save()
        self.context.set_source_rgb(*self._rgb_tuple(symbolizer.color))
        self.context.set_line_width(self.map_length(symbolizer.width))
        self.context.set_line_cap(line_cap_style(symbolizer.cap))
        self.context.set_line_join(line_join_style(symbolizer.join))
        map_dash = [self.map_length(value) for value in symbolizer.dash]
        self.context.set_dash(map_dash)
        line_path(self.context, line, is_closed)
        self.context.stroke()
        self.context.restore()

    def draw_polygon(self, polygon, symbolizer):
        self.context.save()
        self.context.set_source_rgb(*self._rgb_tuple(symbolizer.color))
        self.context.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        rings = iter(polygon)
        outer_ring = rings.next()
        line_path(self.context, outer_ring, is_closed=True)
        for inner_ring in rings:
            self.context.new_sub_path()
            line_path(self.context, inner_ring, is_closed=True)
        self.context.fill()
        self.context.restore()

    def _prepare_layout(self, text, symbolizer):
        layout = self.context.create_layout()
        font_desc = pango.FontDescription(symbolizer.face_name)
        font_desc.set_size(int(round(self.map_length(symbolizer.size) * 1024)))
        layout.set_font_description(font_desc)
        layout.set_text(text)
        p_w, p_h = layout.get_size()
        width = float(p_w) / pango.SCALE
        height = float(p_h) / pango.SCALE
        return width, height, layout

    def _draw_layout(self, layout, x, y, angle, symbolizer):
        self.context.save()
        self.context.move_to(x, y)
        matrix = self.context.get_matrix()
        matrix.scale(1, -1)
        matrix.rotate(-angle)
        self.context.set_matrix(matrix)
        self.context.layout_path(layout)
        if symbolizer.halo_radius:
            self.context.set_line_width(self.map_length(symbolizer.halo_radius))
            self.context.set_line_join(line_join_style('round'))
            self.context.set_source_rgb(*self._rgb_tuple(symbolizer.halo_color))
            self.context.stroke_preserve()
        self.context.set_source_rgb(*self._rgb_tuple(symbolizer.color))
        self.context.fill()
        self.context.restore()

    def draw_point_text(self, text, point, symbolizer):
        self.context.save()
        width, height, layout = self._prepare_layout(text, symbolizer)
        x = point[0] - width / 2.0
        y = point[1] + height / 2.0
        self._draw_layout(layout, x, y, 0, symbolizer)
        self.context.restore()

    def _get_layout_char_spacing(self, layout):
        spacing = []
        p_iter = layout.get_iter()
        c_x, c_y, c_width, c_height = p_iter.get_char_extents()
        last_x = c_x
        more_chars = p_iter.next_char()
        while more_chars:
            c_x, c_y, c_width, c_height = p_iter.get_char_extents()
            spacing.append(float(c_x - last_x) / pango.SCALE)
            last_x = c_x
            more_chars = p_iter.next_char()
        return spacing

    def draw_line_text(self, text, line, symbolizer):
        self.context.save()
        width, height, layout = self._prepare_layout(text, symbolizer)
        spacing = self._get_layout_char_spacing(layout)
        for i, position in \
        enumerate(text_line_positions(line, width, height, spacing)):
            x, y, angle = position
            layout.set_text(text[i])
            self._draw_layout(layout, x, y, angle, symbolizer)
        self.context.restore()

    def draw_image(self, path, bounds):
        surface = cairo.ImageSurface.create_from_png(path)
        self.context.set_source_surface(surface)
        self.context.rectangle(bounds.min_x,
                               bounds.min_y,
                               bounds.width,
                               bounds.height)
        self.context.paint()
