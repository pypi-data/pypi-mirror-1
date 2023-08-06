from gibe.plugin import Plugin

import pkg_resources
        
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory
    
resource_dir = pkg_resources.resource_filename("gibe.prettify", "static")
from gibe.release import version
resource_name = "gibe.prettify-%s" % (version,)
register_static_directory(resource_name, resource_dir)

class PrettifyPlugin(Plugin):
    def blog_header_widgets(self, blog, widgets, context):
        widgets.append(CSSLink(resource_name, 'css/prettify.css'))
        pass

    def blog_bottom_widgets(self, blog, widgets, context):
        widgets.append(JSLink(resource_name, 'javascript/prettify.js'))
        pass
