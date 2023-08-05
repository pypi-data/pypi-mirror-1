import pkg_resources
from turbogears.widgets import Widget
from turbogears.widgets import CSSLink, JSLink, register_static_directory
from TGYUI import widgets as YUI

__all__ = ['ExtJSTabber',
           ]

pkg_path = pkg_resources.resource_filename(__name__, "static")
register_static_directory("TGExtJS", pkg_path)

class ExtJSTabber(Widget):
    css             = [CSSLink("TGExtJS", "resources/css/ext-all.css")]
    javascript      = [JSLink("TGYUI.yui", "utilities/utilities.js"),
                       JSLink("TGExtJS", "adapter/yui/ext-yui-adapter.js"),
                       JSLink("TGExtJS", "ext-all.js"),
                       JSLink("TGExtJS", "thirdparty.js"),
                       ]
