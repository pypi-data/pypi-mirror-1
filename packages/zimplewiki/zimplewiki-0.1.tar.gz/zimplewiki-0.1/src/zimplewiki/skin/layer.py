from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer

class IZimpleBrowserLayer(IFormLayer, IPageletBrowserLayer):
    """Zimple browser layer with form support."""
