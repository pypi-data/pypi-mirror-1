"""
tg_interface
"""
import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, \
                               register_static_directory
#import jquery.jquery
from turbogears.widgets import JSSource, CSSSource, WidgetDescription
from turbogears.widgets import js_location, set_with_self

js_dir = pkg_resources.resource_filename("tg_interface", "static")
register_static_directory("tg_interface", js_dir)
tg_interface_js = JSLink("tg_interface", "interface.js")

#import tg_interface only
tg_interface = tg_interface_js

