from tinymce import TinyMCE

from gibe.model import Comment
@Comment.getContentHtml.when('self.content_format == "tinymce"')
def getContentHtmlPostMarkup(self):
    """
    No conversion - we're HTML already.
    """
    return self.content
@Comment.getExcerptHtml.when('self.content_format == "tinymce"')
def getExcerptHtmlPostMarkup(self):
    """
    No special excerpts for HTML.
    """
    return self.content

from turbogears import widgets, validators
def addCommentFields(wl):
    """
    Add TinyMCE comment widget.
    """
    class CommentFormFieldsExtra(widgets.WidgetsList):
        comment = TinyMCE(validator=validators.NotEmpty, label = "Comment",
            mce_options = dict(
                mode = "exact",
                theme = "advanced",
                plugins = "fullscreen",
                relative_urls = False,
                theme_advanced_buttons2_add = "fullscreen",
                extended_valid_elements = "a[href|target|name]",
                paste_auto_cleanup_on_paste = True,
                paste_convert_headers_to_strong = True,
                paste_strip_class_attributes = "all",
                theme_advanced_buttons3 = "",
                remove_linebreaks = False,
                browsers = "msie,gecko",
            ),
            rows=15,
            cols=60,
        )
    wl.extend(CommentFormFieldsExtra())

import commenting
from gibe.util import sanitise
class Commenting(commenting.Commenting):
    def convert(self, kw):
        """
        Sanitise comments, and convert them to a unicode string.
        """
        kw['comment'] = sanitise(kw['comment']).decode('utf-8')
