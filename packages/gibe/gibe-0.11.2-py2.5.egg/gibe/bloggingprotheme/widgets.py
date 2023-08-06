import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

from gibe import release
resource_name = "gibebloggingpro-%s" % (release.version,)
resource_dir = pkg_resources.resource_filename('gibe.bloggingprotheme', "static")
register_static_directory(resource_name, resource_dir)

class BloggingProTheme(Widget): 
    version = release.version
    css = [
        CSSLink(resource_name, 'css/style.css'),
    ]
    javascript = [
        JSLink(resource_name, 'javascript/imghover.js'),
    ]

BloggingProTheme = BloggingProTheme()
