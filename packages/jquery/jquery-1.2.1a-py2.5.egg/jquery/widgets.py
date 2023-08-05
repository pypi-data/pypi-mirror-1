"""
jquery and jqwebext
"""
import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, \
                               register_static_directory
from turbogears.widgets import JSSource, CSSSource, WidgetDescription
from turbogears.widgets import js_location, set_with_self

js_dir = pkg_resources.resource_filename("jquery", "static")

register_static_directory("jquery", js_dir)

jquery_js = JSLink("jquery", "jquery-1.2.1.pack.js")
#import jquery only
jquery = jquery_js
