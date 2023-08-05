from __future__ import division

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import urlparse

from paste.request import construct_url, parse_dict_querystring

from dap.lib import __dap__
from dap.responses.wms import templess, _islayer


xml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0" xmlns:t="http://johnnydebris.net/xmlns/templess">
<Document>
<name t:content="name" />
<description t:content="description" />
<visibility>1</visibility>
<open>1</open>
<NetworkLink t:content="layer">
  <name t:content="name" />
  <flyToView>0</flyToView>
  <visibility>0</visibility>
  <Url>
    <href t:content="location" />
    <viewRefreshMode>onStop</viewRefreshMode>
    <viewRefreshTime>1</viewRefreshTime>
    <ViewFormat>BBOX=[bboxWest],[bboxSouth],[bboxEast],[bboxNorth]</ViewFormat>
  </Url>
<refreshVisibility>1</refreshVisibility>
</NetworkLink>
</Document>
</kml>"""

overlay = """<?xml version="1.0" encoding="UTF-8"?>
<GroundOverlay xmlns:t="http://johnnydebris.net/xmlns/templess">
  <Name t:content="name" />
  <Icon>
    <href t:content="location" />
  </Icon>
  <LatLonBox>
    <north t:content="north" />
    <south t:content="south" />
    <east t:content="east" />
    <west t:content="west" />
  </LatLonBox>
</GroundOverlay>"""
    
    
def build(self, constraints=None):
    headers = [('Content-type', 'application/keyhole'),
               ('XDODS-Server', 'dods/%s' % '.'.join([str(i) for i in __dap__]))]

    # Parse query string.
    query = parse_dict_querystring(self.environ)
    layers = query.get('LAYERS')

    # Get our location.
    location = construct_url(self.environ, with_query_string=True)
    scheme, netloc, path, queries, fragment = urlparse.urlsplit(location)
    queries = queries.split('&')
    queries = [q for q in queries if q]

    # "Reflector" for Google Earth
    # If LAYERS is not specified GE is requesting the "static" KML. This KML
    # described the NetworkLinks, pointing back to this location. GE will
    # connect to these NetworkLinks passing a LAYERS var and possibly a BBOX;
    # in this case we return a ground overlay pointing to the WMS server.
    if layers:
        # Return overlay. Although LAYERS can request more than one layer,
        # the default behaviour for GE is requesting a single layer due to 
        # the KML file.
        format = self.environ.get('dap.responses.kml.format', 'image/png')

        path = '%s.wms' % path[:-4]
        queries.append('SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&SRS=EPSG:4326&WIDTH=512&HEIGHT=512&TRANSPARENT=TRUE&FORMAT=%s' % format)
        location = urlparse.urlunsplit((scheme, netloc, path, '&'.join(queries), fragment))
        location = templess.cdatanode(location, None)

        bbox = query.get('BBOX', '-180,-90,180,90')
        bbox = bbox.split(',')
        context = {'name': layers,
                   'location': location,
                   'north': bbox[3],
                   'south': bbox[1],
                   'east': bbox[2],
                   'west': bbox[0]}
        t = templess.template(overlay)
    else:
        # Return a NetworkLink element for each layer, pointing back to this
        # file with a LAYERS variable.
        layers = []
        dataset = self._parseconstraints(constraints)
        for var in dataset.walk():
            if _islayer(var):
                location = urlparse.urlunsplit((scheme, netloc, path, '&'.join(queries + ['LAYERS=%s' % var.id]), fragment))
                c = {'name': getattr(var, 'long_name', var.name), 'location': location}
                layers.append(c)
        context = {'description': self.description,
                   'name': dataset.name,
                   'layer': layers}
        t = templess.template(xml)

    output = ["""<?xml version="1.0" encoding="UTF-8"?>\n""", t.unicode(context).encode('utf-8')]

    return headers, output
