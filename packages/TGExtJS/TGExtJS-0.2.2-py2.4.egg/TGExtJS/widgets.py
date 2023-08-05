import pkg_resources
from turbogears.widgets import Widget, CompoundWidget
from turbogears.widgets import CSSLink, JSLink, register_static_directory
from scriptaculous.widgets import prototype_js, scriptaculous_js

__all__ = ['ExtJSTabber', 'Tabber', 'ExtJS',
           'GridFromMarkup', 'PagingJSONGrid',
           ]

pkg_path = pkg_resources.resource_filename(__name__, "static")
register_static_directory("TGExtJS", pkg_path)

adapter_js = JSLink("TGExtJS", "adapter/prototype/ext-prototype-adapter.js")

class ExtJSTabber(Widget):
    css             = [CSSLink("TGExtJS", "resources/css/ext-all.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       adapter_js,
                       JSLink("TGExtJS", "ext-all.js"),
                       JSLink("TGExtJS", "thirdparty.js"),
                       ]

Tabber = ExtJSTabber
ExtJS = ExtJSTabber

class GridFromMarkup(Widget):
    """This widget won't render anything but is a dummy as well."""
    css             = [CSSLink("TGExtJS", "resources/css/ext-all.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       adapter_js,
                       JSLink("TGExtJS", "ext-all.js"),
                       JSLink("TGExtJS", "thirdparty.js"),
                       ]

class PagingJSONGrid(CompoundWidget):
    """Will render a nice ExtJS grid with paging options. The properties are
    fetched by JSON from the property_url. See the homepage for what data the
    latter is expected to contain."""
    template        = 'TGExtJS.templates.PagingJSONGrid'
    params          = ['id', 'width', 'height',
                       'data_url', 'limit', 'property_url']
    width           = '695px'
    height          = '300px'
    limit           = 25
    id              = 'paging_grid'
    css             = [CSSLink("TGExtJS", "resources/css/ext-all.css")]
    javascript      = [prototype_js, scriptaculous_js,
                       adapter_js,
                       JSLink("TGExtJS", "ext-all.js"),
                       JSLink("TGExtJS", "thirdparty.js"),
                       ]
