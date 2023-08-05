import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, \
                               register_static_directory
from turbogears.widgets import JSSource, CSSSource, WidgetDescription
from turbogears.widgets import js_location, set_with_self

js_dir = pkg_resources.resource_filename("jquery", "static")

register_static_directory("jquery", js_dir)

jquery_js = JSLink("jquery", "jquery.pack.js")
jqwebext_js = JSLink("jquery", "jqwebext.pack.js")
zebratable_js = JSLink("jquery", "jqwebext.zebratable.js")
tabs_js = JSLink("jquery", "jqwebext.tabs.js")
tabs_css = CSSLink("jquery/css", "tabs.css",
                    media = "print, projection, screen")
tabs_pack_js = JSLink("jquery/plugins", "jquery.tabs.pack.js")

#import jquery only
jquery = jquery_js

class jqzebra(Widget):
    javascript = [jquery_js, jqwebext_js, zebratable_js]
    
class jqtabs(Widget):
    javascript = [jquery_js, jqwebext_js, tabs_js, tabs_pack_js]
    css = [tabs_css]

class jqtabsDesc(WidgetDescription):
    """
    http://jqwebext.googlepages.com/test-tabs.html
    """
    name = "jQuery Tabs"
    template = """
    <div id="tabs-container">
        <ul class="anchors">
            <li><a href="#section-1" tabindex="1">Section 1</a></li>
            <li><a href="#section-2" tabindex="2">Section 2</a></li>
    
            <li><a href="#section-3" tabindex="3">Section 3</a></li>
        </ul>
        <div id="section-1" class="fragment">
                    <h3>Section 1</h3>
                    <p>
    
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
                    <p>
    
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
        </div>
        <div id="section-2" class="fragment">
                    <h3>Section 2</h3>
                    <p>
    
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
        </div>
    
        <div id="section-3" class="fragment">
                    <h3>Section 3</h3>
                    <p>
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
                    <p>
    
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
                    <p>
    
                        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
                    </p>
        </div>
    </div>    
    """
    for_widget = jqtabs()
