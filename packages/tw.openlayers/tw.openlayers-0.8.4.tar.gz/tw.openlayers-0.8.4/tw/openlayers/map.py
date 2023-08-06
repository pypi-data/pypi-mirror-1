# OpenLayers Map Widgets
# Author: Sanjiv Singh <SinghSanjivK@gmail.com>
# License: MIT

from tw.api import Widget, JSLink, CSSLink, js_function
from tw.openlayers.util import prepare_layers, inject_apis, \
			prepare_controls

__all__ = ["Map"]

# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before

ol_js = JSLink(modname=__name__, 
                filename='static/javascript/OpenLayers.js', javascript=[])
map_js = JSLink(modname=__name__, 
                filename='static/javascript/map.js', javascript=[])
ol_css = CSSLink(modname=__name__,
		filename='static/javascript/theme/default/style.css')

class Map(Widget):
    """This creates a div with an OpenLayers Map object. The map is
    a container for several layers within their own respective divs
    contained within the map div. The map could also contain several
    map controls like layer switcher, pan zoom bar, etc.
    """
    params = ["id", "layers", "controls", "center", "zoom"]
    template = """<div id="${id}"></div>"""
    template_engine = "genshi"

    javascript = [ol_js, map_js]
    css = [ol_css]

    def update_params(self, d):
        super(Map, self).update_params(d)
        inject_apis(self.layers)
        layers = controls = []
        if self.layers: layers = prepare_layers(self.layers)
        if self.controls: controls = prepare_controls(self.controls, self.layers)
        options = dict(id=d.id,
         		layers = layers,
			controls=controls)
        if self.center:
            options["centerX"], options["centerY"] = self.center
        if self.zoom:
            options["zoom"] = self.zoom
        call = js_function('showMap')(options)
        self.add_call(call)

