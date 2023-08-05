from __future__ import division

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import re
import bisect
from cStringIO import StringIO

from paste.request import construct_url, parse_dict_querystring
from paste.httpexceptions import HTTPBadRequest
import Image, ImageDraw, ImageColor
import numpy
from numpy import ma

from dap.lib import __dap__
from dap.dtypes import *

from dap.responses.wms import templess
from dap.responses.wms.palette import jet


def build(self, constraints=None):
    # Parse query string.
    query = parse_dict_querystring(self.environ)

    # Grab full dataset.
    dataset = self._parseconstraints(constraints)
    
    # Get request type.
    request = query.get('REQUEST', 'GetMap')
    if request == 'GetCapabilities':
        return _capabilities(dataset, self.description, self.environ)
    elif request != 'GetMap':
        raise HTTPBadRequest('You need to specify a REQUEST type')

    # Filter sequences by constraint. This is importante because it avoids
    # building a complete sequence from the database just to filter it later.
    seqs = [var for var in dataset if isinstance(var, SequenceType)]
    for seq in seqs:
        # Grab lat & lon variables from the sequence.
        lat = lon = None
        for var in seq.walk():
            if getattr(var, "axis", None) == 'X': lon = var
            if getattr(var, "axis", None) == 'Y': lat = var

        # Get requested boundaries.
        bbox = [float(v) for v in query.get('BBOX', '-180,-90,180,90').split(',')]
        minlon, minlat, maxlon, maxlat = bbox

        # Put coordinates in same range as the data. For this the sequence
        # should have a ``lon_range`` attributes (as the dapper spec requires).
        try: lon_range = dataset.attributes['NC_GLOBAL']['lon_range']
        except: lon_range = -360.0, 360.0
        query['lon_range'] = lon_range
        minlon = lon_range[0] - (lon_range[0] % 360.0) + (minlon % 360.0)
        maxlon = lon_range[0] - (lon_range[0] % 360.0) + (maxlon % 360.0)
        
        # Filter data accordingly. We can only filter data when ``minlon`` is 
        # less than ``maxlon`` -- this is not always the case because longitudes
        # wrap. Since the DAP does not allow OR in the constraint expression
        # we can't do two separate requests.
        if minlon < maxlon:
            filters = ['%s>=%s' % (lon.id, minlon), '%s<=%s' % (lon.id, maxlon),
                       '%s>=%s' % (lat.id, minlat), '%s<=%s' % (lat.id, maxlat)]
            constraints += '&' + '&'.join(filters)

    # Re-request dataset with the new constraints.
    if seqs: dataset = self._parseconstraints(constraints)

    headers = [('Content-description', 'dods_wms'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
              ]

    format = query.get('FORMAT', 'image/png')
    headers.append(('Content-type', format))
    format = format.split('/')[1]

    im = _dispatch(dataset, query)
    buf = StringIO()
    im.save(buf, format)
    output = buf.getvalue()

    return headers, output


def _capabilities(dapvar, description, environ):
    headers = [('Content-type', 'text/xml'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__])),
              ]

    xml = """<?xml version='1.0' encoding="UTF-8" standalone="no" ?>
<WMT_MS_Capabilities version="1.1.1" xmlns:t="http://johnnydebris.net/xmlns/templess">

<Service>
  <Name t:content="name" />
  <Title t:content="title" />
  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" t:attr="xlink:href location" />
</Service>

<Capability>
  <Request>
    <GetCapabilities>
      <Format>application/vnd.ogc.wms_xml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" t:attr="xlink:href location" /></Get>
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <GetMap>
      <Format>image/jpeg</Format>
      <Format>image/png</Format>
      <Format>image/gif</Format>
      <Format>image/tiff</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" t:attr="xlink:href location" /></Get>
        </HTTP>
      </DCPType>
    </GetMap>
  </Request>
  <Exception>
    <Format>application/vnd.ogc.se_blank</Format>
  </Exception>
  <VendorSpecificCapabilities />
  <UserDefinedSymbolization SupportSLD="1" UserLayer="0" UserStyle="1" RemoteWFS="0"/>
  <Layer>
    <Title t:content="title" />
    <SRS>EPSG:4326</SRS>
    <LatLonBoundingBox t:attr="minx minx; miny miny; maxx maxx; maxy maxy" />
    <Layer t:content="layer">
      <Name t:content="name" />
      <Title t:content="title" />
      <Abstract t:content="abstract" />
    </Layer>
  </Layer>
</Capability>
</WMT_MS_Capabilities>"""

    # Get lat/lon range for the dataset, if available.
    try: lon_range = dapvar.attributes['NC_GLOBAL']['lon_range']
    except: lon_range = -180.0, 180.0
    try: lat_range = dapvar.attributes['NC_GLOBAL']['lat_range']
    except: lat_range = -90.0, 90.0

    # Build location using query_string but removing WMS variables.
    # We assume the request is done at the url::
    #
    #     http://server/dataset.wms?var1,var2,var3&CE&REQUEST=GetCapabilities
    #     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^
    #                        DODS                               WMS
    #
    # ie, with a DODS part and a WMS part.
    location = construct_url(environ, with_query_string=True)
    location = re.sub("(&|\?)REQUEST=[^&]*", "", location)

    context = {'name': dapvar.name,
               'title': description,
               'location': location,
               'minx': str(lon_range[0]),
               'maxx': str(lon_range[1]),
               'miny': str(lat_range[0]),
               'maxy': str(lat_range[1]),
               'layer': [{'name': var.id,
                          'title': getattr(var, 'long_name', var.name),
                          'abstract': getattr(var, 'history', '')}
                         for var in dapvar.walk() if _islayer(var)]}
    t = templess.template(xml)
    output = ["""<?xml version='1.0' encoding="ISO-8859-1" standalone="no" ?>
<!DOCTYPE WMT_MS_Capabilities SYSTEM "http://schemas.opengis.net/wms/1.1.1/WMS_MS_Capabilities.dtd"
 [
 <!ELEMENT VendorSpecificCapabilities EMPTY>
 ]>
<!-- end of DOCTYPE declaration -->

""", t.unicode(context).encode('utf-8')]

    return headers, output


def _islayer(dapvar):
    if isinstance(dapvar, GridType):
        # Grids need lat and lon maps with coards units.
        lat = lon = None
        for var in dapvar.maps.values():
            if re.match("degrees?_n", var.units, re.IGNORECASE): lat = True
            elif re.match("degrees?_e", var.units, re.IGNORECASE): lon = True
        return lat and lon
    elif isinstance(dapvar, SequenceType):
        # Sequences also need lat and lon, following dapper spec.
        lat = lon = None
        for var in dapvar.walk():
            if getattr(var, "axis", None) == 'X': lon = True
            elif getattr(var, "axis", None) == 'Y': lat = True
        return lat and lon
    elif isinstance(dapvar, StructureType):
        # Structures need at least a valid variable.
        for var in dapvar.walk():
            if _islayer(var): return True
    
    return False


def _dispatch(dapvar, query):
    func = {DatasetType  : _dataset,
            StructureType: _structure,
            SequenceType : _sequence,
            BaseType     : _base,
            ArrayType    : _array,
            GridType     : _grid,
           }[type(dapvar)]

    return func(dapvar, query)


def _dataset(dapvar, query):
    """
    Join images together.
    """
    # Build base image and paste other over it.
    size = int(query.get('WIDTH', 256)), int(query.get('HEIGHT', 256))
    layers = query.get('LAYERS', '').split(',')

    # Transparent image? We need to set only the base image, all
    # others are transparent where there's no data.
    transparent = query.get('TRANSPARENT', 'FALSE')
    if transparent == 'TRUE': alpha = 0
    else: alpha = 255

    # Background color.
    bgcolor = query.get('BGCOLOR', '0xFFFFFF').replace('0x', '#')
    red, green, blue = ImageColor.getrgb(bgcolor)
    
    im = Image.new('RGBA', size, (red, green, blue, alpha))
    for var in dapvar.walk():
        if var.id in layers:
            try:
                layer = _dispatch(var, query)
                if layer: im.paste(layer, None, layer)
            except:
                pass
    return im


def _structure(dapvar, query):
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    for var in dapvar.walk():
        if var.id in layers:
            try:
                layer = _dispatch(var, query)
                if layer: im.paste(layer, None, layer)
            except:
                pass
    return im


def _grid(dapvar, query):
    # Get lat & lon.
    lat = lon = None
    for var in dapvar.maps.values():
        if re.match("degrees?_n", var.units, re.IGNORECASE):
            lat = numpy.array(dapvar.maps[var.name][:])
        elif re.match("degrees?_e", var.units, re.IGNORECASE):
            lon = numpy.array(dapvar.maps[var.name][:])

    # Make lon monotonic.
    for i in range(1, lon.shape[0]):
        if lon[i] < lon[i-1]: lon[i] += 360.

    # Get boundaries.
    bbox = [float(v) for v in query.get('BBOX', '-180,-90,180,90').split(',')]
    minlon, minlat, maxlon, maxlat = bbox

    # Create base image.
    width, height = size = int(query.get('WIDTH', 256)), int(query.get('HEIGHT', 256))
    im = Image.new('RGBA', size, (0, 0, 0, 0))

    # Draw image. We need to offset since lon can be in a different range.
    offset = numpy.ceil((lon[0] - maxlon)/360.0) * 360.0
    while (minlon + offset) < lon[-1]:
        x, y = lon - offset, lat

        i0 = bisect.bisect_right(x, minlon) - 1
        i1 = bisect.bisect_left(x, maxlon) + 1
        if y[1] > y[0]:
            j0 = bisect.bisect_right(y, minlat) - 1
            j1 = bisect.bisect_left(y, maxlat) + 1
        else:
            j0 = bisect.bisect_right(-y, -maxlat) - 1
            j1 = bisect.bisect_left(-y, -minlat) + 1
        i0 = max(0, i0)
        j0 = max(0, j0)

        # Get step. Since the image has at most width x height pixels, we can subsample
        # the data accordingly -- there's no need to retrieve data with higher resolution.
        dy = (maxlat - minlat) / height
        dlat = y[1] - y[0]
        jstep = max(int(dy/dlat), 1)

        dx = (maxlon - minlon) / width
        dlon = x[1] - x[0]
        istep = max(int(dx/dlon), 1)

        # Retrieve data.
        y = y[j0:j1:jstep]
        if i0 < i1:
            x = x[i0:i1:istep]
            data = dapvar[...,j0:j1:jstep,i0:i1:istep]
        else:
            # Cyclic boundary.
            x = numpy.concatenate((x[i0:], x[:i1]))
            data = numpy.concatenate((dapvar[...,j0:j1:jstep,i0::istep],
                                      dapvar[...,j0:j1:jstep,:i1:istep]), len(dapvar.shape)-1)

        data = numpy.array(data)
        data = data * getattr(dapvar, 'scale_factor', 1) + getattr(dapvar, 'add_offset', 0)
        data = ma.masked_equal(data, getattr(dapvar, 'missing_value', -1e33))
        mask = data.mask

        # Make data 2D and in range 0-255.
        while len(data.shape) > 2:
            data = ma.average(data, axis=0)
        if hasattr(dapvar, 'actual_range'):
            actual_range = dapvar.actual_range
        else:
            alldata = dapvar[:]
            if hasattr(dapvar, 'missing_value'):
                alldata = ma.masked_equal(alldata, dapvar.missing_value)
            actual_range = numpy.min(alldata), numpy.max(alldata)
        data = data - actual_range[0]
        data = data / (actual_range[1] - actual_range[0])
        data = data * 255.
        data = data.filled(255)
        data = data.astype('b')

        # Make mask 2D -- mask is lost with ma.average (remember to file bug).
        mask = mask.astype('b')
        mask.shape = (-1, mask.shape[-2], mask.shape[-1])
        mask = 1 - mask[0]
        ##mask = mask * 255.  # add some transparency 
        mask = mask * 200.
        mask = mask.astype('b')

        # Create image with gray palette.
        mix = numpy.concatenate((numpy.reshape(data, (-1, 1)), numpy.reshape(mask, (-1, 1))), 1)
        layer = Image.fromstring("LA", (data.shape[1], data.shape[0]), mix.tostring())

        # Put palette into colored layer. We need to convert 
        # it to mode "F" first, and then finally to "RGBA".
        clayer = layer.convert("L")
        clayer.putpalette(jet)
        layer = layer.convert("RGBA")
        layer.paste(clayer, None, layer)

        # Paste image. Here we map the image from the data boundaries,
        # defined by lon0, lon1, lat0, lat1 to the BBOX limits.
        lon0, lon1 = x[0], 2*x[-1] - x[-2]
        lat0, lat1 = y[0], 2*y[-1] - y[-2]
        x0 = layer.size[0] * (minlon - lon0) / (lon1 - lon0)
        x1 = layer.size[0] * (maxlon - lon0) / (lon1 - lon0)
        y0 = layer.size[1] * (maxlat - lat0) / (lat1 - lat0)
        y1 = layer.size[1] * (minlat - lat0) / (lat1 - lat0)
        layer = layer.transform(size, Image.EXTENT, (x0, y0, x1, y1))

        im.paste(layer, None, layer)
        offset += 360.0
    
    return im


def _sequence(dapvar, query):
    # Find lat & lon.
    lat = lon = None
    for i, var in enumerate(dapvar.walk()):
        if getattr(var, "axis", None) == 'X': lon = i
        elif getattr(var, "axis", None) == 'Y': lat = i

    # Get boundaries.
    bbox = [float(v) for v in query.get('BBOX', '-180,-90,180,90').split(',')]
    minlon, minlat, maxlon, maxlat = bbox

    # Create image.
    width, height = size = int(query.get('WIDTH', 256)), int(query.get('HEIGHT', 256))
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # Draw point for each record. Since the bbox can be much larger than
    # the lon range (say, -360 to 360) we create an offset and change the
    # lon values at 360 degress increments.
    data = list(dapvar.data)
    offset = numpy.ceil((query['lon_range'][1] - maxlon)/360.0) * 360.0
    while (minlon + offset) < query['lon_range'][1]:
        for values in data:
            x, y = values[lon] - offset, values[lat]
        
            # Convert coords.
            x = width * (x - minlon) / (maxlon - minlon)
            y = height * (1 - (y - minlat) / (maxlat - minlat))
            draw.ellipse((x-2, y-2, x+2, y+2), fill=(255, 0, 0), outline=(100, 0, 0))

        offset += 360.0

    del draw
    return im
        

def _array(dapvar, query):
    pass

_base = _array
