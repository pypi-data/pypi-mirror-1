import cherrypy

import turbogears
from turbogears import widgets

from gibe import model
import routes

import logging
log = logging.getLogger("gibe.feeds")

from turbogears import feed
class FeedController(feed.FeedController):
    def get_feed_data(self, blog, **kw):

        # url_for won't give the hostname unless you pass one in.  The hostname
        # can be hardcoded in gibe.hostname in configuration, otherwise it will
        # be read from the HTTP Host header.  Failing that, no host will be
        # used.
        host = cherrypy.config.get('gibe.hostname', cherrypy.request.headers.get('Host', ''))

        # Get the last 5 entries - either on the blog, or for a particular tag
        tagname = kw.get('tagname', '')
        if tagname:
            t = model.Tag.get_by(name=tagname)
            last_entries = t.recent_posts(limit=5)
        else:
            last_entries = model.Post.select(order_by=model.desc(model.Post.c.creation_time), limit = 5)

        # You can hardcode the "link" for the blog to something other than the
        # front page in gibe.blog_base in the configuration.  Otherwise, the
        # front page will be used.
        blog_base = cherrypy.config.get("gibe.blog_base", routes.url_for("frontpage", host=host))

        return dict(
            title=blog.name,
            author=dict(name=blog.owner.display_name),
            link=blog_base,
            updated=last_entries[0].creation_time,
            generator="gibe",
            entries=[
                dict(title=post.title, content=post.content, summary=post.excerpt, updated = post.modification_time, published = post.creation_time,
                author=dict(name=post.author.display_name),
                link=routes.url_for('posts', post=post, host=host),
                id=routes.url_for('posts', post=post, host=host)) for post in last_entries],
        )

    def atom1_0(self, **kwargs):
        """
        This is overridden from base, since base assumes the feed content will
        be provided in text data, whereas we're outputing XHTML.
        """
        host = cherrypy.config.get('gibe.hostname', cherrypy.request.headers.get('Host', ''))
        feed = self.get_feed_data(**kwargs)
        self.format_dates(feed, 3339)
        feed["id"] = routes.url_for('atom1_0', host=host)
        feed["href"] = routes.url_for('atom1_0', host=host)
        self.depr_entrys(feed)
        return feed
    atom1_0 = turbogears.expose(template="genshi:gibe.templates.atom1_0", format="xml", content_type="application/atom+xml")(atom1_0)


class FeedLink(widgets.Source):
    template = """
    <link rel="alternate" href="$src" title="$title" type="$type" />
    """
    params = ['title', 'type']
    params_doc = {'src': 'The feed URL', 'title': 'Title for the feed', 'type': 'MIME type for the feed'}

    retrieve_css = widgets.set_with_self

class FeedLinks(widgets.Widget):
    def retrieve_css(self):
        return [
            FeedLink(src=routes.url_for('rss2.0.xml'), title="RSS 2.0", type="application/rss+xml"), 
            FeedLink(src=routes.url_for('atom1_0'), title="Atom 1.0", type="application/atom+xml"), 
        ]

feedlinks = FeedLinks()

