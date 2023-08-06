from django import http

import shelley
from shelley.renderers import cairorender


def wms(request, map):
    bbox = request.GET['BBOX']
    x1, y1, x2, y2 = (float(v) for v in bbox.split(','))
    width = int(request.GET['WIDTH'])
    height = int(request.GET['HEIGHT'])
    view = shelley.Box(x1, y1, x2, y2, map.srs)
    response = http.HttpResponse(mimetype='image/png')
    format = cairorender.Image(width=width, height=height, path=response)
    shelley.render(map, view, format)
    return response



