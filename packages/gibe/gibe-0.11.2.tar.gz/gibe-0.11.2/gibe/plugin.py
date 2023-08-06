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
        """widgets to put above the post."""
        pass

    def post_bottom_widgets(self, blog, widgets, context):
        """widgets to put below the post"""
        pass

    def post_list_top_widgets(self, blog, widgets, context):
        """widgets to put above each post in a list of posts"""
        pass

    def post_list_bottom_widgets(self, blog, widgets, context):
        """widgets to put below each post in a list of posts"""
        pass

    def blog_header_widgets(self, blog, widgets, context):
        """widgets (JS/CSS/Link) to put in the headers"""
        pass

    def blog_top_widgets(self, blog, widgets, context):
        """widgets (usually JS) to put at the top of the page body"""
        pass

    def blog_bottom_widgets(self, blog, widgets, context):
        """widgets (usually JS) to put at the bottom of the page body"""
        pass

    def post_edit_widgets(self, blog, widgets, context):
        """widgets to add to post create/edit admin page"""
        pass

    def post_edit_values(self, blog, post, values, context):
        """values for widgets in post create/edit admin page"""
        pass

    def post_edit_params(self, blog, post, params, context):
        """params for widgets in post create/edit admin page"""
        pass

    def post_edit_handle(self, blog, post, form_values, context):
        """post might not exist yet"""
        pass

    def post_edit_handle_after(self, blog, post, form_values, context):
        """post will exist now"""
        pass

    def map_routes(self, blog, mapper, controllers):
        """
        Routes to add for this plugin.

        Add rules to the mapper.

        Should also add controller to controllers dictionary.
        """
        pass

    def template_search_path(self, blog, search_path):
        """
        Additional location to search for templates.
        """
        pass

    def template_data(self, blog, template_data):
        """
        Add data to the template_data dictionary to be provided to every
        request to provide the (usually master) template with what it needs.
        """
        pass

    def template_replacements(self, blog, template_replacements):
        """
        template_replacements is a dictionary of key original template and
        value the replacement template.
        """
        pass


class MemberWidgetList(widgets.CompoundWidget):
    """
    List of widgets that will be passed into the template system.  Will cause
    their JS and CSS to be loaded.
    """
    def __init__(self, widgets):
        super(MemberWidgetList, self).__init__()
        self.member_widgets = []
        self.member_widgets.extend(widgets)

    def __iter__(self):
        return self.member_widgets.__iter__()

    iter_member_widgets = __iter__

def create_mangle_func(mangler_name):
    """
    Returns a function that will execute the named function on all plugins, and
    convert the resulting list into a MemberWidgetList
    """
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
    """
    Provide edit values for editing posts.
    """
    values = {}
    if post:
        values['title'] = post.title
        values['content'] = post.content

    for k, v in plugins.items():
        v.post_edit_values(blog, post, values, context)
    return values

def post_edit_params(blog, post, context):
    """
    Provide parameters for the edit post page's widgets.  To set up select
    boxes, checkbox/radio lists, and so forth.
    """
    params = {}

    for k, v in plugins.items():
        v.post_edit_params(blog, post, params, context)
    return params

from tinymce import TinyMCE
from turbojson.jsonify import encode


class TinyMCEWithPlugins(TinyMCE):
    """
    TinyMCE widget that will load a list of plugins at startup.
    """
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
    """
    Build the edit post form, with some base fields, and then passing through
    the post_edit_widgets method on all plugins.
    """

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
                # Added for microformats support
                extended_valid_elements = "a[class|title|href|target|name],abbr[class|title]",
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

def map_routes(blog, mapper, controllers):
    """
    Call each plugins' map_routes method, building up new rules in mapper and
    controllers in controllers.
    """
    for k, v in plugins.items():
        v.map_routes(blog, mapper, controllers)

def template_data(blog):
    """
    Call each plugin's template_data method, building up a dictionary of
    additional template data to pass to all template views.
    """
    d = {}
    for k, v in plugins.items():
        v.template_data(blog, d)
    return d

def template_search_path(blog):
    """
    Build up the template search path by defaulting to the gibe templates, and
    then passing that list to every plugins' template_search_path method.
    """
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
    """
    Build up a dictionary of key old template name and value new template name
    so that plugins can replace the use of a template in the main Gibe code.
    """
    d = {}
    for k, v in plugins.items():
        v.template_replacements(blog, d)
    return d

def find_template(blog, template):
    """
    Look up a template replacement from template_replacements.
    """
    d = get_plugin_data(blog)
    template = d['template_replacements'].get(template, template)
    return template

def get_plugin_data(blog):
    """
    One-time plugin data load - return is cached.
    """
    from gibe import plugin
    blogid = blog.blog_id
    if blogid not in blog_plugin_data:
        blog_bottom_widgets = plugin.blog_bottom_widgets(blog, {})
        blog_top_widgets = plugin.blog_top_widgets(blog, {})
        blog_header_widgets = plugin.blog_header_widgets(blog, {})
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
            'blog_header_widgets': blog_header_widgets,
        }
        blog_plugin_data[blogid].update(plugin.template_data(blog))
        blog_plugin_data[blogid].update({
            '_gibe_blog_widgets': MemberWidgetList([blog_header_widgets, blog_bottom_widgets, blog_top_widgets]),
        })
    return blog_plugin_data[blogid]

def add_plugin_data(template=None):
    def wrap(func):
        def entangle(self, *args, **kw):
            ret = func(self, *args, **kw)

            blog = kw.get('blog', None)
            if not blog:
                return ret

            # The method might return a string or other non-dict.  Just pass that though.
            if not isinstance(ret, dict):
                return ret

            # Add general plugin data.
            ret.update(get_plugin_data(blog))

            ret['blog'] = blog

            # Single post view.
            if 'post' in ret:
                # A standard list isn't explored in TurboGears widgets to load
                # up JS/CSS.  Converting to a MemberWidgetList causes these to
                # be loaded.
                ret.update({
                    '_gibe_post_widgets': MemberWidgetList([ret['post_top_widgets'], ret['post_bottom_widgets']]),
                })

            # Multiple post list.
            if 'posts' in ret:
                # A standard list isn't explored in TurboGears widgets to load
                # up JS/CSS.  Converting to a MemberWidgetList causes these to
                # be loaded.
                ret.update({
                    '_gibe_list_widgets': MemberWidgetList([ret['post_list_top_widgets'], ret['post_list_bottom_widgets']]),
                })

            # Locate possible replacement template from template_replacements
            if template:
                ret['tg_template'] = find_template(blog, template)

            return ret
        return entangle
    return wrap


blog_plugin_data = {}
plugins = {}

def on_startup():
    """
    Load up plugins at startup, and check whether to include them.  If they
    load up and say they're initialised, then add them to the plugins list.
    """
    for plugin_mod in pkg_resources.iter_entry_points("gibe.plugins"):
        plugin_name = plugin_mod.module_name
        if plugin_mod.attrs:
            plugin_name += ':' + '.'.join(plugin_mod.attrs)

        if plugin_name == "gibetags.plugin:TagsPlugin":
            continue
        if plugin_name == "gibebloggingpro.plugin:BloggingProPlugin":
            continue

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

# Make on_startup run at TurboGears startup time (after database is set up, and
# so forth).
from turbogears.startup import call_on_startup
call_on_startup.append(on_startup)
