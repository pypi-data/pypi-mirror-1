import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

resource_dir = pkg_resources.resource_filename("gibe.tags",
                                         "static")

from gibe.release import version
resource_name = "gibe.tags-%s" % (version,)
register_static_directory(resource_name, resource_dir)

from turbogears import widgets
from turbogears import validators
from gibe import model
from turbogears import expose, paginate
import cherrypy

import routes

import simplejson
import scriptaculous

from gibe.plugin import add_plugin_data

class TagController(object):
    @expose(template="genshi:gibe.templates.archives", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.archives")
    @paginate('posts', limit = 10)
    def tag(self, blog, tagname, **kw):
        t = model.Tag.get_by(name=tagname)
        if not t:
            raise cherrypy.NotFound()

        posts = t.recent_posts(limit = None)
        return dict(blog=blog, posts=posts, tag=t)

class TagDisplayWidget(widgets.Widget):
    template = "gibe.tags.templates.tagdisplay"

    css = [
        widgets.CSSLink(resource_name, 'css/tags.css'),
    ]

    params_doc = {
        'tags': 'Tags to display',
    }
    params = params_doc.keys()

    tags = []

    def update_params(self, d):
        super(TagDisplayWidget, self).update_params(d)
        d['url_for'] = routes.url_for

class TagPostDisplayWidget(TagDisplayWidget):
    params_doc = {
        'post': 'Post to display tags for',
    }
    params = params_doc.keys()
    post = None

    def update_params(self, d):
        super(TagPostDisplayWidget, self).update_params(d)
        d['tags'] = d['post'].tags

class TagFieldValidator(validators.String):
    def _to_python(self, value, state):
        tagnames = value.split(",")
        tagnames = [tagname.strip() for tagname in tagnames if tagname.strip()]
        tags = []
        for tagname in tagnames:
            t = model.Tag.select_by(name=tagname)
            if t:
                t = t[0]
            if not t:
                t = model.Tag(name=tagname, display_name=tagname)
            tags.append(t)
        return tags

    def _from_python(self, value, state):
        tags = value
        return ", ".join([t.name for t in tags])

class TagEditPostWidget(widgets.TextField):
    template = """
<div xmlns:py="http://purl.org/kid/ns#">
    <input
        autocomplete="off"
        type="text"
        name="${name}"
        class="${field_class}"
        id="${field_id}"
        value="${value}"
        size="50"
        py:attrs="attrs"
    />
   <div class="auto_complete" id="${field_id}_ac"></div>
   <script type="text/javascript">
   autocomplete_${field_id} = ${options_json};
   new Autocompleter.Local('${field_id}', '${field_id}_ac', autocomplete_${field_id}, ${autocompleter_options});
   </script>
</div>
"""
    params_doc = {
        'autocompleter_options': 'Options for the autocompleter',
    }
    params = params_doc.keys()

    autocompleter_options = {
        'tokens': [','],
        'frequency': 0.001,
    }

    validator = TagFieldValidator
    list_attrs = {'class': 'tageditlist',}
    css = [
        widgets.CSSLink(resource_name, 'css/tags.css'),
    ]
    javascript = [
        scriptaculous.prototype_js,
        scriptaculous.scriptaculous_js,
        scriptaculous.effects_js,
        scriptaculous.controls_js,
    ]
    def update_params(self, d):
        d['options'] = [(tag.tag_id, tag.display_name) for tag in model.Tag.select(order_by = 'display_name')]
        super(TagEditPostWidget, self).update_params(d)
        d['options_json'] = simplejson.dumps([tag_display_name for tag_id, tag_display_name in d['options']])
        d['autocompleter_options'] = simplejson.dumps(d['autocompleter_options'])
