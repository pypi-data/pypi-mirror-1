from gibe.plugin import Plugin

from widgets import *
from feeds import *

tagController = TagController()
tagFeedController = TagFeedController()
tpdw = TagPostDisplayWidget(name="tagpostdisplaywidget")
tepw = TagEditPostWidget(name='tageditpostwidget', label="Tags")

import turbogears.widgets

def tag_expand(kargs):
    if 'tag' not in kargs:
        return kargs

    tag = kargs.pop('tag')
    kargs['tagname'] = tag.name

    return kargs

def tag_condition(environ, match_dict):
    if environ['PATH_INFO'].endswith('.html'):
        return False
    if environ['PATH_INFO'].endswith('.rss'):
        return False
    return True

class TagsPlugin(Plugin):
    def map_routes(self, blog, maps, controllers):
        controllers['tagController'] = tagController
        controllers['tagFeedController'] = tagFeedController
        maps.append(('tags', 'tags/:(tagname)', dict(controller='tagController', action='tag', _filter=tag_expand, conditions=dict(function=tag_condition))))
        maps.append(('deprecated_tags_html', 'tags/:(tagname).html', dict(controller='tagController', action='tag')))
        maps.append(('tags_rss', 'tags/:(tagname).rss', dict(controller='tagFeedController', action='rss2_0')))
        maps.append(('tags_rss_deprecated', 'category_:(tagname).rss', dict(controller='tagFeedController', action='rss2_0')))

    def post_top_widgets(self, blog, widget_list, context):
        widget_list.append(tpdw)

    def post_list_top_widgets(self, blog, widget_list, context):
        widget_list.append(tpdw)

    def post_edit_widgets(self, blog, widget_list, context):
        for i, w in enumerate(widget_list):
            if w.name == "title":
                widget_list.insert(i+1, tepw)

    def post_edit_values(self, blog, post, values, context):
        if post:
            values['tageditpostwidget'] = post.tags

    def post_edit_handle_after(self, blog, post, form_values, context):
        post.tags = form_values['tageditpostwidget']

