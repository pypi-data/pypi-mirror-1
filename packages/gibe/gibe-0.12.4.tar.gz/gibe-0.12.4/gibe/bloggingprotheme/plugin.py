from gibe.plugin import Plugin

from gibe.bloggingprotheme.widgets import *
import cherrypy

class BloggingProPlugin(Plugin):
    def enabled(self):
        theme = cherrypy.config.get('gibe.theme', None)
        if not theme:
            return True
        if theme == "bloggingpro":
            return True
        return False

    def template_search_path(self, blog, search_path):
        import gibe.bloggingprotheme.templates
        search_path.insert(0, gibe.bloggingprotheme.templates.__path__[0])

    def template_data(self, blog, template_data):
        td = {
            'gibebloggingpro_theme': BloggingProTheme,
            'google_custom_search': cherrypy.config.get('gibe.google_custom_search', None),
        }
        template_data.update(td)

    def template_replacements(self, blog, template_replacements):
        template_replacements['genshi:gibe.templates.frontpage'] = 'genshi:gibe.bloggingprotheme.templates.frontpage'
        template_replacements['genshi:gibe.templates.post'] = 'genshi:gibe.bloggingprotheme.templates.post'
        template_replacements['genshi:gibe.templates.archives'] = 'genshi:gibe.bloggingprotheme.templates.archives'
        pass
