from xml.etree import ElementTree as ET

import shelley
from shelley.datasources import gdal
from shelley.mappers.mapnik import defn
from shelley import utils, symbolizers as syms


def parse_xml(stream):
    tree = ET.parse(stream)
    return parse_map(tree.getroot())


def parse_map(map_element):
    styles = {}
    for style_element in map_element.findall('Style'):
        style = parse_style(style_element)
        styles[style.name] = style
    layers = []
    for layer_element in map_element.findall('Layer'):
        layer = parse_layer(layer_element, styles)
        layers.append(layer)
    srs = shelley.SRS.proj4(map_element.attrib['srs'])
    bgcolor = parse_rgb(map_element.attrib['bgcolor'])
    map = defn.Map(layers=layers, srs=srs, background=bgcolor)
    return map


def parse_rgb(rgb):
    rgb = rgb.lstrip('#')
    from_hex = lambda x : int(x, 16)
    return shelley.Color(from_hex(rgb[0:2]),
                         from_hex(rgb[2:4]),
                         from_hex(rgb[4:6]))


def parse_style(style_element):
    name = style_element.attrib['name']
    rules = []
    for rule_element in style_element.findall('Rule'):
        rules.append(parse_rule(rule_element))
    return defn.Style(name=name, rules=rules)


def parse_layer(layer_element, styles):
    named_styles = []
    for style_name_element in layer_element.findall('StyleName'):
        named_styles.append(styles[style_name_element.text])
    data_source = parse_data_source(layer_element.find('Datasource'))
    return defn.Layer(layer_element.attrib['name'], data_source, named_styles)


def parse_data_source(data_source_element):
    params = {}
    for param_element in data_source_element.findall('Parameter'):
        params[param_element.attrib['name']] = param_element.text
    if params['type'] == 'shape':
        return gdal.FeatureSource(params['file'] + '.shp', driver='ESRI Shapefile')
    elif params['type'] == 'postgis':
        open_params = [
            '%s=%s' % (name, params[name])
            for name in ['host', 'port', 'user', 'password', 'dbname']
            if params.get(name)
        ]
        sql = 'select * from ' + params.get('table')
        return gdal.FeatureSource('PG:' + ' '.join(open_params),
                                  driver='PostgreSQL',
                                  sql=sql)


CssConversion = utils.namedtuple('CssConversion', 'name converter')


def convert_color(c):
    return shelley.Color.parse(c)


def convert_dash_array(da):
    return [float(item) for item in da.split(',')]


def parse_css_symbolizer(symbolizer_element, class_, css_conversions, default_args):
    kwargs = default_args.copy()
    for css_element in symbolizer_element.findall('CssParameter'):
        try:
            conversion = css_conversions[css_element.attrib['name']]
            kwargs[conversion.name] = conversion.converter(css_element.text)
        except KeyError:
            pass
    return class_(**kwargs)


line_css_conversions = {
    'stroke': CssConversion('color', convert_color),
    'stroke-width': CssConversion('width', float),
    'stroke-linecap': CssConversion('cap', str),
    'stroke-linejoin': CssConversion('join', str),
    'stroke-dasharray': CssConversion('dash', convert_dash_array),
}


line_default_args = {'color': shelley.Color.name('black'),
                     'width': 1.0,
                     'cap': 'butt',
                     'join': 'miter',
                     'dash': []}


def parse_line_symbolizer(element):
    return parse_css_symbolizer(element,
                                syms.LineSymbolizer,
                                line_css_conversions,
                                line_default_args)


polygon_css_conversions = {
    'fill': CssConversion('color', convert_color)
}

polygon_default_args = {'color': shelley.Color.name('grey')}


def parse_polygon_symbolizer(element):
    return parse_css_symbolizer(element,
                                syms.PolygonSymbolizer,
                                polygon_css_conversions,
                                polygon_default_args)


def parse_text_symbolizer(element):
    return syms.TextSymbolizer(
        property_name=element.get('name'),
        face_name=element.get('face_name'),
        size=float(element.get('size', '10')),
        color=convert_color(element.get('fill', 'black')),
        placement=element.get('placement', 'point'),
        halo_radius=float(element.get('halo_radius', '0')),
        halo_color=convert_color(element.get('halo_fill', 'white'))
    )


def parse_rule(rule_element):
    kwargs = {}
    filter_ = parse_filter(rule_element)
    if filter_ is not None:
        kwargs['filter'] = filter_
    symbolizer_parsers = {
        'LineSymbolizer': parse_line_symbolizer,
        'PolygonSymbolizer': parse_polygon_symbolizer,
        'TextSymbolizer': parse_text_symbolizer,
    }
    symbolizers = []
    for child_element in list(rule_element):
        try:
            parser = symbolizer_parsers[child_element.tag]
            symbolizers.append(parser(child_element))
        except KeyError:
            pass
    min_scale_element = rule_element.find('MinScaleDenominator')
    if min_scale_element is not None:
        kwargs['min_scale_denom'] = float(min_scale_element.text)
    max_scale_element = rule_element.find('MaxScaleDenominator')
    if max_scale_element is not None:
        kwargs['max_scale_denom'] = float(max_scale_element.text)
    return defn.Rule(symbolizers=symbolizers, **kwargs)


def parse_filter(rule_element):
    filter_element = rule_element.find('Filter')
    if filter_element is not None:
        filter_ = defn.Filter(filter_element.text)
    else:
        else_filter_element = rule_element.find('ElseFilter')
        if else_filter_element is not None:
            filter_ = defn.ElseFilter()
        else:
            filter_ = None
    return filter_

