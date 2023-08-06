import os.path
import itertools
import pkg_resources
from turbogears.widgets import Widget, TextField
from turbogears.widgets import CSSSource, JSSource, register_static_directory
from turbogears import config
from turbojson import jsonify
from util import CSSLink, JSLink

__all__ = ['TGIXEDIT',
          ]

ixedit_path = pkg_resources.resource_filename(__name__, os.path.join("static", "ixedit"))
jquery_path = pkg_resources.resource_filename(__name__, os.path.join("static", "jquery"))
sample_path = pkg_resources.resource_filename(__name__, os.path.join("static", "sample-style"))
register_static_directory("TGIXEDIT", ixedit_path)
register_static_directory("TGIXEDITJQUERY", jquery_path)
register_static_directory("TGIXEDITSAMPLE", sample_path)

class TGIXEDIT(Widget):
    css             = ([CSSLink("TGIXEDIT", "ixedit.css"),
                        CSSLink("TGIXEDITSAMPLE", "ui-sui.css"),
                       ])
    javascript      =  [JSLink("TGIXEDIT", "ixedit.packed.js"),
                        JSLink("TGIXEDITJQUERY", "jquery-plus-jquery-ui.js"),
                       ]
