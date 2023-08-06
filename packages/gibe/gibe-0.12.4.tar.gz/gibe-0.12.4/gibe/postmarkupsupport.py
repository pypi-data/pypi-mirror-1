import postmarkup

class CodeTag(postmarkup.TagBase):
    """
    Generates a code block that is syntax highlighted.
    """
    def __init__(self):
        postmarkup.TagBase.__init__(self, 'code')

    def open(self, open_pos):
        return '<pre class="prettyprint">'

    def close(self, close_pos, content):
        return "</pre>" 

from gibe.model import Comment

@Comment.getContentHtml.when('self.content_format == "postmarkup"')
def getContentHtmlPostMarkup(self):
    """
    Describe how to convert the entire comment content into HTML.
    """
    return pm.render_to_html(self.content)

@Comment.getExcerptHtml.when('self.content_format == "postmarkup"')
def getExcerptHtmlPostMarkup(self, length = 150):
    """
    Describe how to convert an excerpt of the comment content into HTML.
    """
    content = self.content
    #if len(content) > length:
    #    content = content[:length-3] + "..."
    return pm.render_to_html(content, max_length = length, continuation_text = "...", max_continuous = 25)

    input_content = self.content
    output_content = ""
    done = False
    remaining_length = length
    tries = 0
    while not done:
        tries += 1
        if tries > 5:
            break
        print "input_content: %s" % (input_content,)
        print "output_content: %s" % (output_content,)
        print "remaining_length: %s" % (remaining_length,)
        work_on = input_content[:length]

        if "[" not in work_on:
            if len(work_on) > remaining_length:
                output_content += work_on[:remaining_length-3] + "..."
            else:
                output_content += work_on

            done = True
            break

        tag_start = input_content.index("[")
        output_content += input_content[:tag_start+1]
        remaining_length -= tag_start
        input_content = input_content[tag_start+1:]

        if "]" not in input_content:
            if len(input_content) > remaining_length:
                output_content += input_content[:remaining_length-3] + "..."
            else:
                output_content += input_content
            output_content += "]"
            done = True
            break

        tag_end = input_content.index("]")
        output_content += input_content[:tag_end+1]
        input_content = input_content[tag_end+1:]

    #if len(content) > length:
    #    content = content[:length-3] + "..."
    return pm.render_to_html(output_content.encode('utf-8')).decode('utf-8')

from turbogears import widgets, validators
class PostMarkupExplanation(widgets.FormField):
    """
    A widget to add an explanation of the PostMarkup functionality to the "add
    comment" form.
    """
    template = """
    <div xmlns:py="http://purl.org/kid/ns#"
        class="${field_class}"
        id="${field_id}"
    >
        <p>The text area above accepts Post Markup, a BBCode work-alike.</p>

        <pre>
[b]foo[/b]: <strong>foo</strong>
[i]foo[/i]: <em>foo</em>
[link]http://nxsy.org/[/link]: <a href="http://nxsy.org/">http://nxsy.org/</a> [nxsy.org]
[link http://nxsy.org/]Neil[/link]: <a href="http://nxsy.org/">Neil</a> [nxsy.org]
        </pre>

        <p>You can also use:</p>
        <pre>
[code python]
import foo
[/code]
        </pre>
    </div>
    """

def addCommentFields(wl):
    """
    Add the PostMarkup text area and explanation to the "add comment" form.
    """
    class CommentFormFieldsExtra(widgets.WidgetsList):
        comment = widgets.TextArea(label = "Your comment", rows=15, cols=45,
            validator=validators.NotEmpty,
        )
        explanation = PostMarkupExplanation()
    wl.extend(CommentFormFieldsExtra())

import commenting
class Commenting(commenting.Commenting):
    def convert(self, kw):
        """
        This plugin doesn't do conversion.
        """
        pass
    def post_save(self, kw):
        """
        This plugin doesn't do anything post-save.
        """
        pass
    

# Build the postmarkup renderer for comments.
pm = postmarkup.PostMarkup().default_tags()
pm.add_tag('link', postmarkup.LinkTag, 'link')
pm.add_tag('quote', postmarkup.QuoteTag)
pm.add_tag('code', CodeTag)

