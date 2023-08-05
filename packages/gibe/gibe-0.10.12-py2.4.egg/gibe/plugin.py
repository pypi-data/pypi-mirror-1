from turbogears import widgets
from turbogears import validators
import pkg_resources

import logging
log = logging.getLogger("gibe.plugin")

class Plugin(object):
    def initialise(self):
        return True

    def enabled(self):
        return True

    def post_top_widgets(self, blog, widgets, context):
        # widgets to put above the post
        pass

    def post_bottom_widgets(self, blog, widgets, context):
        # widgets to put below the post
        pass

    def post_list_top_widgets(self, blog, widgets, context):
        # widgets to put above each post in a list of posts
        pass

    def post_list_bottom_widgets(self, blog, widgets, context):
        # widgets to put below each post in a list of posts
        pass

    def blog_header_widgets(self, blog, widgets, context):
        # widgets (JS/CSS/Link) to put in the headers
        pass

    def blog_top_widgets(self, blog, widgets, context):
        # widgets (usually JS) to put at the top of the page body
        pass

    def blog_bottom_widgets(self, blog, widgets, context):
        # widgets (usually JS) to put at the bottom of the page body
        pass

    def post_edit_widgets(self, blog, widgets, context):
        # widgets to add to post create/edit admin page
        pass

    def post_edit_values(self, blog, post, values, context):
        # values for widgets in post create/edit admin page
        pass

    def post_edit_params(self, blog, post, params, context):
        # params for widgets in post create/edit admin page
        pass

    def post_edit_handle(self, blog, post, form_values, context):
        # post might not exist yet
        pass

    def post_edit_handle_after(self, blog, post, form_values, context):
        # post will exist now
        pass

    def map_routes(self, blog, mapper, controllers):
        pass

    def template_search_path(self, blog, search_path):
        pass

    def template_data(self, blog, template_data):
        pass

    def template_replacements(self, blog, template_replacements):
        pass

class MemberWidgetList(widgets.CompoundWidget):
    def __init__(self, widgets):
        super(MemberWidgetList, self).__init__()
        self.member_widgets = []
        self.member_widgets.extend(widgets)

    def __iter__(self):
        return self.member_widgets.__iter__()

    iter_member_widgets = __iter__

def create_mangle_func(mangler_name):
    def mangle_func(blog, context):
        widget_list = []
        for k, v in plugins.items():
            getattr(v, mangler_name)(blog, widget_list, context)
        return MemberWidgetList(widget_list)

    return mangle_func

post_top_widgets = create_mangle_func('post_top_widgets')
post_bottom_widgets = create_mangle_func('post_bottom_widgets')
blog_header_widgets = create_mangle_func('blog_header_widgets')
blog_top_widgets = create_mangle_func('blog_top_widgets')
blog_bottom_widgets = create_mangle_func('blog_bottom_widgets')
post_list_top_widgets = create_mangle_func('post_list_top_widgets')
post_list_bottom_widgets = create_mangle_func('post_list_bottom_widgets')

def post_edit_values(blog, post, context):
    values = {}
    if post:
        values['title'] = post.title
        values['content'] = post.content

    for k, v in plugins.items():
        v.post_edit_values(blog, post, values, context)
    return values

def post_edit_params(blog, post, context):
    params = {}

    for k, v in plugins.items():
        v.post_edit_params(blog, post, params, context)
    return params

from tinymce import TinyMCE
from turbojson.jsonify import encode

class TinyMCEWithPlugins(TinyMCE):
    params_doc = {
        'plugins': 'list of tuples of plugin name and plugin location',
    }
    params = params_doc.keys()
    plugins = []
    def update_params(self, d):
        super(TinyMCEWithPlugins, self).update_params(d)
        for plugin_name, plugin_url in d['plugins']:
            d['TinyMCEInit'] += '\ntinyMCE.loadPlugin(%s, %s);' % (encode(plugin_name), encode(plugin_url),)

def post_edit_widgets(blog, context):
    import turbogears
    class PostFormFields(widgets.WidgetsList):
        title = widgets.TextField(validator=validators.NotEmpty,
            label = "Title", attrs=dict(size="30"))
        content = TinyMCEWithPlugins(validator=validators.NotEmpty, label = "Content",
            mce_options = dict(
                mode = "exact",
                theme = "advanced",
                plugins = "fullscreen,insertexcerptline",
                relative_urls = False,
                theme_advanced_buttons2_add = "fullscreen,insertexcerptline",
                extended_valid_elements = "a[href|target|name]",
                paste_auto_cleanup_on_paste = True,
                paste_convert_headers_to_strong = True,
                paste_strip_class_attributes = "all",
                theme_advanced_buttons3 = "",
                remove_linebreaks = False,
                convert_newlines_to_brs = False,
                force_br_newlines = False,
            ),
            rows=25,
            cols=65,
            plugins=[
                ('insertexcerptline', turbogears.url('/tg_widgets/gibe.static/javascript/insertexcerptline')),
            ],
        )

    widgets_list = []
    for w in PostFormFields():
        widgets_list.append(w)

    for k, v in plugins.items():
        v.post_edit_widgets(blog, widgets_list, context)

    return widgets_list
    return PostFormFields()

def map_routes(blog, mapper, controllers):
    for k, v in plugins.items():
        v.map_routes(blog, mapper, controllers)

def template_data(blog):
    d = {}
    for k, v in plugins.items():
        v.template_data(blog, d)
    return d

def template_search_path(blog):
    search_path = []
    import gibe.templates
    search_path.extend(gibe.templates.__path__)
    for k, v in plugins.items():
        v.template_search_path(blog, search_path)
    return search_path

def post_edit_handle_after(blog, post, kw, context):
    for k, v in plugins.items():
        v.post_edit_handle_after(blog, post, kw, context)

def template_replacements(blog):
    d = {}
    for k, v in plugins.items():
        v.template_replacements(blog, d)
    return d

def find_template(blog, template):
    d = get_plugin_data(blog)
    template = d['template_replacements'].get(template, template)
    return template

def get_plugin_data(blog):
    from gibe import plugin
    blogid = blog.blog_id
    if blogid not in blog_plugin_data:
        blog_bottom_widgets = plugin.blog_bottom_widgets(blog, {})
        blog_top_widgets = plugin.blog_top_widgets(blog, {})
        blog_plugin_data[blogid] = {
            'post_top_widgets': plugin.post_top_widgets(blog, {}),
            'post_bottom_widgets': plugin.post_bottom_widgets(blog, {}),
            'post_list_top_widgets': plugin.post_list_top_widgets(blog, {}),
            'post_list_bottom_widgets': plugin.post_list_bottom_widgets(blog, {}),
            'post_edit_widgets': plugin.post_edit_widgets(blog, {}),
            'template_search_path': plugin.template_search_path(blog),
            'template_replacements': plugin.template_replacements(blog),
            'blog_top_widgets': blog_top_widgets,
            'blog_bottom_widgets': blog_bottom_widgets,
        }
        blog_plugin_data[blogid].update(plugin.template_data(blog))
        blog_plugin_data[blogid].update({
            '_gibe_blog_widgets': MemberWidgetList([blog_bottom_widgets, blog_top_widgets]),
        })
    return blog_plugin_data[blogid]

def add_plugin_data(template=None):
    def wrap(func):
        def entangle(self, *args, **kw):
            ret = func(self, *args, **kw)

            blog = kw.get('blog', None)
            if not blog:
                return ret

            if not isinstance(ret, dict):
                return ret

            ret.update(get_plugin_data(blog))

            ret['blog'] = blog

            if 'post' in ret:
                ret.update({
                    '_gibe_post_widgets': MemberWidgetList([ret['post_top_widgets'], ret['post_bottom_widgets']]),
                })

            if 'posts' in ret:
                ret.update({
                    '_gibe_list_widgets': MemberWidgetList([ret['post_list_top_widgets'], ret['post_list_bottom_widgets']]),
                })

            if template:
                ret['tg_template'] = find_template(blog, template)

            return ret
        return entangle
    return wrap


blog_plugin_data = {}
plugins = {}

def on_startup():
    for plugin_mod in pkg_resources.iter_entry_points("gibe.plugins"):
        plugin_name = plugin_mod.module_name
        if plugin_mod.attrs:
            plugin_name += ':' + '.'.join(plugin_mod.attrs)

        mod = plugin_mod.load()
        p = mod()
        if p.enabled():
            initialised = False
            try:
                initialised = p.initialise()
            except (Exception,), e:
                print e
                pass

            if initialised:
                plugins[plugin_name] = p

from turbogears.startup import call_on_startup
call_on_startup.append(on_startup)
