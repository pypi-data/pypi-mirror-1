import pkg_resources
from turbogears.widgets.base import CSSLink, JSLink, CSSSource, JSSource, \
    Widget, CoreWD, static, js_location, register_static_directory


register_static_directory('gibe.static',
                          pkg_resources.resource_filename(__name__,
                                                          "static")
                         )

# This is a copy of the base TurboGears SyntaxHighlighter, except for the
# marked addition of shTag.js

class SyntaxHighlighter(Widget):
    """This widget includes the syntax highlighter js and css into your 
    rendered page to syntax-hightlight textareas named 'code'. The supported
    languages can be listed at the 'languages' __init__ parameter.
    """
    available_langs = set([
        'CSharp',
        'Css',
        'Delphi',
        'Java',
        'JScript',
        'Php',
        'Python',
        'Ruby',
        'Sql',
        'Vb',
        'Xml',
        ])
    css = [CSSLink(static,"sh/SyntaxHighlighter.css")]
    
    def __init__(self, languages=['Python', 'Xml', 'JScript', 'Php', 'Css']):
        javascript = [ 
            JSLink(static, 'sh/shCore.js', location=js_location.bodybottom)
            ]
        for lang in languages:
            if lang not in self.available_langs:
                raise ValueError, ("Unsupported language %s. Available "
                                   "languages: '%s'" % 
                                   (lang, ', '.join(self.available_langs)))
            source = "sh/shBrush%s.js" % lang
            javascript.append(
                JSLink(static, source, location=js_location.bodybottom)
                )

        ### CUSTOM:
        # Add shTag.js
        javascript.append(
            JSLink('gibe.static', 'javascript/shTag.js', location=js_location.bodybottom)
        )
        # Call HighlightTag for "pre" tags.
        javascript.append(
            JSSource(
                "dp.SyntaxHighlighter.HighlightTag('pre');",
                location=js_location.bodybottom
                )
            )
        self.javascript = javascript

syntaxhighlighter = SyntaxHighlighter()
