# An OpenLayers ToscaWidgets Utilities
# Author: Sanjiv Singh <SinghSanjivK@gmail.com>
# License: MIT

from tw.api import JSLink, js_symbol, encode

def get_layer(layer_name, layers):
    for layer in layers:
        if layer.name == layer_name:
            return layer_name
        
def prepare_layers(layers):
    prepared_layers = []
    for layer in layers:
        l = " new OpenLayers.Layer"
        if (layer.__class__.__name__ == 'OSMMapnik'):
            l += '.OSM.Mapnik'
        elif (layer.__class__.__name__ == 'OSMRenderer'):
            l += '.OSM.Osmarender'
        else:
            l += ".%s" % layer.__class__.__name__
        l += "("
        if layer.name:
            l += "'%s'" % layer.name
        if layer.url:
            if (isinstance(layer.url, str)):
                l += ",'%s'" % layer.url
            else:
                l += ",%s" % layer.url
        if layer.options:
            l += ",%s" % encode(layer.options)
        if layer.display:
            l += ",%s" % encode(layer.display)
        l += ")"
        prepared_layers.append(js_symbol(l))
    return prepared_layers

def inject_apis(layers):
    if not layers: return
    for layer in layers:
        if (layer.__class__.__name__ == "Google"):
            JSLink(link='http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s'
                    % layer.apikey).inject()
        if (layer.__class__.__name__ == "Yahoo"):
            JSLink(link='http://api.maps.yahoo.com/ajaxymap?v=3.0&amp;appid=%s'
                    % layer.apikey).inject()
        if (layer.__class__.__name__ == "VirtualEarth"):
            JSLink(link='http://dev.virtualearth.net/mapcontrol/v3/mapcontrol.js%s'
                    % layer.apikey).inject()
        if (layer.__class__.__name__ in ['OSMMapnik', 'OSMRenderer']):
            JSLink(modname=__name__,
                filename='static/javascript/OpenStreetMap.js').inject()


def prepare_controls(controls, layers):
    prepared_controls = []
    for control in controls:
        if hasattr(control, "layer_name"):
            c = "{'layer_name': '%s', 'options': %s}" % (control.layer_name, encode(control.options))
        else:
            c = " new OpenLayers.Control"
            c += ".%s" % control.__class__.__name__
            c += "("
            if hasattr(control, "name"):
                c += "'%s'" % control.name
            if hasattr(control, "layer_name"):
                c += "'%s'" % get_layer(control.layer_name, layers)
            if hasattr(control, "base"):
                c += "'%s'" % control.base
            if hasattr(control, "options"):
                c += ",%s" % encode(control.options)
            c += ")"
        prepared_controls.append(js_symbol(c))
    return prepared_controls

