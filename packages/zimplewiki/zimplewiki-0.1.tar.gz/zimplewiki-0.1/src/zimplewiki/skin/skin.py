import z3c.formui.interfaces

import layer

class IZimpleBrowserSkin(z3c.formui.interfaces.IDivFormLayer,
                         layer.IZimpleBrowserLayer):
    """The Zimple browser skin using the div-based layout."""
