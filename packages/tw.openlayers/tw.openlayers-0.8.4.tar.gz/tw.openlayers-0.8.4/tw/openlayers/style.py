# An OpenLayers Style and StyleMap Widgets
# Author: Sanjiv Singh <SinghSanjivK@gmail.com>
# License: MIT

from tw.api import Widget, JSLink

__all__ = ["Style", "StyleMap"]

class StyleBase(Widget):
    """ Base class for Style Widgets. """
    params = []

    config = None
    def __init__(self, id=None, parent=None, children=[], **kw):
        super(Widget, self).__init__(id, parent, children, **kw)
        self.config = kw
        self.config["_style_type"] = self.__class__.__name__

    @property
    def all_params(self):
        d = {}
        for param in self.params:
            d[param] = getattr(self, param)
        return d

    def update_params(self, d):
        super(StyleBase, self).update_params(d)

class Style(StyleBase):
    """ An OpenLayers Style widget.

    This widget can be used ti create a style object for OpenLayers.
    This style is created based on use defined SDL (Styled Layer
    Descriptor) Document. The style is then applied to a Vector layer
    or its subclasses.

    For detailed documentation on the OpenLayers API, visit the OpenLayers
    homepage: http://www.openlayers.org/
    """
    template = """
    """
    params = []

    def update_params(self, d):
        super(Style, self).update_params(d)

class StyleMap(StyleBase):
    """The StyleMap Widget creates a style map object from either a set
    of style options or an OGC Styled Layer Descriptor (SLD) document.
    """
    params = []

    def update_params(self, d):
        super(StyleMap, self).update_params(d)
