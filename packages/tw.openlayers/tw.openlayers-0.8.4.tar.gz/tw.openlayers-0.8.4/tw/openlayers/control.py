# An OpenLayers Layer Widget and subclasses
# Author: Sanjiv Singh <SinghSanjivK@gmail.com>
# License: MIT

from tw.api import Widget, JSLink, js_symbol

__all__ = ["LayerSwitcher", "OverviewMap", "Permalink", "PanZoomBar",
 	   "MouseToolbar", "MousePosition", "SelectFeature"]

class ControlBase(Widget):
    """ Base class for Control Widgets. """
    params = []

    @property
    def all_params(self):
        d = {}
        for param in self.params:
            d[param] = getattr(self, param)
        return d

    def update_params(self, d):
        super(ControlBase, self).update_params(d)

class LayerSwitcher(ControlBase):
    """ An OpenLayers Layer Switcher Control Widget.

    Creates a standard layer switcher control which displays
    all baselayers and overlays for selection. The control
    can be conviniently hidden and displayed using a hide button.

    For detailed documentation on the OpenLayers API, visit the OpenLayers
    homepage: http://www.openlayers.org/
    """
    template = """
    """
    params = ["ascending"]

    ascending = False
    ascending_doc = ("Whether the layers should be displayed in ascending order.")

    def update_params(self, d):
        super(LayerSwitcher, self).update_params(d)

class OverviewMap(ControlBase):
    """Creates an overview map to show the area currently covered
    in the map within the total extent.
    """
    params = []

    def update_params(self, d):
        super(OverviewMap, self).update_params(d)

class Navigation(ControlBase):
    """Adds navigation control using mouse events like dragging, double
    clicking and scrolling the mouse wheel.
    """
    params = []

    def update_params(self, d):
        super(Navigation, self).update_params(d)


class PanZoomBar(ControlBase):
    """Adds a pan and zoom control with paning arrows and a zoom
    bar with graduations for differnt zoom levels.
    """
    params = []

    def update_params(self, d):
        super(PanZoomBar, self).update_params(d)

class Permalink(ControlBase):
    """Adds a permalink control for the current map center position
    and zoom level.
    """
    params = ["base"]

    base = "Permalink"
    base_doc = ("The base string to be displayed.")

    def update_params(self, d):
        super(Permalink, self).update_params(d)

class MouseToolbar(ControlBase):
    params = []

    def update_params(self, d):
        super(MouseToolbar, self).update_params(d)

class MousePosition(ControlBase):
    """This control shifs the map center to the current mouse double
    click position.
    """
    params = []

    def update_params(self, d):
        super(MousePosition, self).update_params(d)

class SelectFeature(ControlBase):
    """Selects vector features from a given layer on click or hover.
    """
    params = []

    def update_params(self, d):
        super(SelectFeature, self).update_params(d)

