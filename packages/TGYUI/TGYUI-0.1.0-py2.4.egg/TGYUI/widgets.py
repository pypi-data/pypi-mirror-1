import os.path
import pkg_resources
from turbogears.widgets import Widget, CompoundWidget, TextField
from turbogears.widgets import CSSLink, JSLink, register_static_directory

__all__ = ['YUIResetCSS', 'YUIFontsCSS', 'YUIGrids', 'YUIResetFontsGrids',
           'YUIAnimation', 'YUIMenuBar', 'YUIAutoComplete',
          ]

pkg_path = pkg_resources.resource_filename(__name__, os.path.join("static", "yui"))
register_static_directory("TGYUI.yui", pkg_path)

class YUIResetCSS(Widget):
    css             = [CSSLink("TGYUI.yui", "reset/reset-min.css")]

class YUIFontsCSS(Widget):
    css             = [CSSLink("TGYUI.yui", "fonts/fonts-min.css")]

class YUIGrids(Widget):
    css             = [CSSLink("TGYUI.yui", "grids/grids-min.css")]

class YUIResetFontsGrids(Widget):
    """Use this in place of using all the three YUIResetCSS, YUIFontsCSS,
    YUIGrids."""
    css             = [CSSLink("TGYUI.yui", "reset-fonts-grids/reset-fonts-grids.css")]

class YUIAnimation(Widget):
    javascript      = [JSLink("TGYUI.yui", "utilities/utilities.js"),
                       JSLink("TGYUI.yui", "thirdparty/effects-min.js"),
                      ]

class YUIMenuBar(CompoundWidget):
    template        = 'TGYUI.templates.menubar'
    params          = ['id', 'entries']
    css             = [CSSLink("TGYUI.yui", "reset-fonts-grids/reset-fonts-grids.css"),
                       CSSLink("TGYUI.yui", "menu/assets/menu.css"),
                      ]
    javascript      = [JSLink("TGYUI.yui", "utilities/utilities.js"),
                       JSLink("TGYUI.yui", "thirdparty/controls.js"),
                      ]
    member_widgets  = ['yui_animation']
    yui_animation   = YUIAnimation()
    id              = 'mbar'
    entries         = [('Companies', '/companies', [
                            ('add new', '/companies/add_new', []),
                            ('browse', '/companies/browse', [
                                ('by name', '/companies/browse/by_name'),
                                ('by date', '/companies/browse/by_date'),
                                ]),
                            ('list', '/companies/list', []),
                            ]),
                       ('Contacts', '/contacts', []),
                       ('Queries', '/queries', []),
                       ('Mailings', '/mailings', []),
                       ('Search', '/search', []),
                      ]

class YUIAutoComplete(TextField):
    "A standard, single-line text field with YUI AutoComplete enhancements."
    template        = 'TGYUI.templates.autocomplete'
    params = ["attrs", "id", "search_controller", "result_schema", "search_param"]
    params_doc = {'attrs' : 'Dictionary containing extra (X)HTML attributes for'
                            ' the input tag',
                  'id'    : 'ID for the entire AutoComplete construct.'}
    attrs = {}
    id = 'noid'
    search_param = 'input'
    javascript      = [JSLink("TGYUI.yui", "utilities/utilities.js"),
                       JSLink("TGYUI.yui", "thirdparty/json.js"),
                       JSLink("TGYUI.yui", "thirdparty/controls.js"),
                      ]
