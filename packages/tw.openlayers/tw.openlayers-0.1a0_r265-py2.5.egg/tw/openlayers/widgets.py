from tw.api import Widget, JSLink, CSSLink, JSSource, js_function

__all__ = ["Map"]

# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before

ol_js = JSLink(modname=__name__, 
                filename='static/OpenLayers.js', javascript=[])

ol_css = CSSLink(modname=__name__, filename='static/theme/default/style.css')

class Map(Widget):
    params = ["id", "layers", "panZoomBar"]
    template = """<div id="${id}"></div>"""
    template_engine = "genshi"
    #template = "tw.openlayers.templates.openlayers"
    src = """
        var map = null;

        function showMap(options){

            map = new OpenLayers.Map(options.id);


            var layer = []
            for(i=0; i<options.layers.length; i++) {
                if (options.layers[i].layer_type == 'WMS') {
                    ol_layer = new OpenLayers.Layer.WMS(
                        options.layers[i].layer_name,
                        options.layers[i].layer_url,
                        options.layers[i].layer_opts,
                        options.layers[i].display_opts
                    );
                } else if (options.layers[i].layer_type == 'Google') {
                    ol_layer = new OpenLayers.Layer.Google(
                        options.layers[i].layer_name,
                        options.layers[i].layer_opts,
                        options.layers[i].display_opts
                    );
                } else if (options.layers[i].layer_type == 'Yahoo') {
                    ol_layer = new OpenLayers.Layer.Yahoo(
                        options.layers[i].layer_name,
                        options.layers[i].layer_opts,
                        options.layers[i].display_opts
                    );
                } else {}
                layer = layer.concat([ol_layer]);
            }

            map.addLayers(layer);
            map.addControl(new OpenLayers.Control.LayerSwitcher());
            if (options.panZoomBar) map.addControl(new OpenLayers.Control.PanZoomBar());
            map.zoomToMaxExtent();
        }
    """
    map_js = JSSource(src=src)
    include_dynamic_js_calls = True

    javascript = [ol_js]
    css = [ol_css]

    def __init__(self, id=None, parent=None, children=[], **kw):
        super(Map, self).__init__(id, parent, children, **kw)

        if 'Google' in [layer['layer_type'] for layer in self.layers]:
            google_js = JSLink(link='http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAA9XNhd8q0UdwNC7YSO4YZghSPUCi5aRYVveCcVYxzezM4iaj_gxQ9t-UajFL70jfcpquH5l1IJ-Zyyw')
            self.javascript.append(google_js)

        if 'Yahoo' in [layer['layer_type'] for layer in self.layers]:
            yahoo_js = JSLink(link='http://api.maps.yahoo.com/ajaxymap?v=3.0&amp;appid=euzuro-openlayers')
            self.javascript.append(yahoo_js)

        self.javascript.append(self.map_js)

    def update_params(self, d):
        super(Map, self).update_params(d)
        options = dict(id=d.id,
		       layers=self.layers,
		       panZoomBar=self.panZoomBar)
        call = js_function('showMap')(options)
        self.add_call(call)
