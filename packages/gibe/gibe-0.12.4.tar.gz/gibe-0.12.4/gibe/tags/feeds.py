import cherrypy

import turbogears
from turbogears import widgets

from gibe import model
import routes

import logging
log = logging.getLogger("gibe.feeds")

from turbogears import feed
class TagFeedController(feed.FeedController):
    def get_feed_data(self, blog, tagname, **kw):
        host = cherrypy.config.get('gibe.hostname', cherrypy.request.headers.get('Host', ''))
        t = model.Tag.get_by(name=tagname)
        last_entries = t.recent_posts(limit=5)

        blog_base = cherrypy.config.get("gibe.blog_base", routes.url_for("frontpage", host=host))

        return dict(
            title=blog.name,
            #author=dict(name=blog.owner.name),
            link=blog_base,
            updated=last_entries[0].creation_time,
            generator="gibe",
            entries=[
                dict(title=post.title, content=post.content, summary=post.excerpt, updated = post.modification_time, published = post.creation_time,
                #author=dict(name=post.author.name),
                link=routes.url_for('posts', post=post, host=host)) for post in last_entries],
        )

