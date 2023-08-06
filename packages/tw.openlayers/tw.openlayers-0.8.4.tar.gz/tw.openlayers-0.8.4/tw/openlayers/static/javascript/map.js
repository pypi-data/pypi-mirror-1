function showMap(options){

    map = new OpenLayers.Map(options.id, {controls:[]});
    this.tw_map = map;
    this.tw_layers = options.layers;

    map.addLayers(options.layers);

    if (options.controls) {
        for(control in options.controls) {
          try {
            map.addControl(options.controls[control]);
          }
          catch(err) {
            layer = getLayerByName(options.layers, options.controls[control].layer_name);
            select = new OpenLayers.Control.SelectFeature(layer, options.controls[control].options);
            map.addControl(select);
            select.activate();
            }
        }
    }

    try {
      if (options.centerX != null && options.centerY != null && options.zoom != null) {
          map.setCenter(new OpenLayers.LonLat(options.centerX, options.centerY), options.zoom);
      }
      else {
          map.zoomToMaxExtent();
      }
    } catch (err) {}
}

function getLayerByName(layers, layer_name) {
    var theLayer = null;
    for (layer in layers) {
        if (layers[layer].name == layer_name) {
            theLayer = layers[layer];
        }
    }
    return theLayer;
}
