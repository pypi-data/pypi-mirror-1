import logging
log = logging.getLogger('gibe.util')
import re

def slugify(title, table, id=0):
    """
    Code taken from Toasty Goat project
    This ugly sack of crap returns a slug from a title. The title and
    table (Posts, Pages, etc) must be passed to determine if the slug
    already exists. The id is for editing a sluggable item, making it
    so that you may replace the item with the same slug without a
    problem.
    """
    regex = re.compile("[^\w\-\ ]")
    slug = regex.sub('', title).lower().strip().replace(' ', '-')

    append = ''
    while True:
        new_slug = slug[:(255 - len(str(append)))] + str(append)
        if not slug_exists(new_slug, table, id):
            return new_slug
        else:
            if append == '':
                append = 1

            append = append + 1


def slug_exists(slug, table, id):
    a = table.get_by(slug=slug)
    if not a:
        return False
    if a.post_id == id:
        return False
    return True

from elementtree import ElementTree as ET
from genshi.core import Attrs, Namespace, stripentities
from genshi.core import END, END_NS, START, START_NS, TEXT
from genshi.input import HTML
from genshi.filters import HTMLSanitizer


class Excerptifier:
    """
    Look for an excerpt marker <hr class="excerpt"/ > in the post.  If found,
    everything before the marker is a excerpt.  Otherwise, the whole post is
    shown.
    """
    found_excerpt = False
    def __call__(self, stream, ctxt = None):
        open_tags = []
        for kind,data,pos in stream:
            if kind == START:
                tag, attrs = data
                open_tags.append(tag)
            if kind == END:
                open_tags.pop()
            if kind == START:
                tag, attrs = data
                if tag == "hr":
                    for name, value in attrs:
                        if name == "class" and value == "excerpt":
                            self.found_excerpt = True
                            break
                    if self.found_excerpt:
                        break
                    
            yield kind, data, pos

        if open_tags:
            for t in open_tags:
                yield END, t, pos

        raise StopIteration

def excerptify(post):
    """
    Look for an excerpt marker <hr class="excerpt"/ > in the post.  If found,
    everything before the marker is a excerpt.  Otherwise, the whole post is
    shown.
    """
    html = HTML(post.content)
    e = Excerptifier()
    res = (html | e)
    foo = res.render(encoding=None)
    if e.found_excerpt:
        return foo
    return post.content

def commaise(elements):
    """
    Given a stream of elements, separate the top-level elements with a comma.
    """
    level = 0
    started = False
    for kind, data, pos in elements:
        if level == 0 and started:
            yield TEXT, ", ", pos

        if kind == START:
            started = True
            level += 1

        if kind == END:
            level -= 1

        yield kind, data, pos

def sanitise(htmltext):
    """
    Sanitise user-provided HTML.
    """
    html = HTML(htmltext)
    return (html | HTMLSanitizer()).render()

from datetime import datetime, timedelta

def display_entries(posts, granularity="day"):
    """
    Convert from a list of posts to a list of (day, posts) tuples.  In other
    words, create a group of posts per day in the list.
    """
    display_entries = []
    last = None
    for entry in posts:
        if granularity == "month":
            this = datetime(year=entry.creation_time.year, month=entry.creation_time.month, day=1)
        else:
            this = datetime(year=entry.creation_time.year, month=entry.creation_time.month, day=entry.creation_time.day)
        if last != this:
            last = this
            last_list = (last, [])
            display_entries.append(last_list)

        last_list[1].append(entry)

    return display_entries

template_loader_installed = False
def install_template_loader():
    """
    Install the "search path" into the Genshi templating engine - the search
    path may be different in each request due to plugins.
    """
    from genshi.template.loader import TemplateLoader, TemplateNotFound
    import cherrypy
    from turbogears import view
    global template_loader_installed

    # Only install the template loader once.
    if template_loader_installed:
        return

    template_loader_installed = True
    class MyTemplateLoader(TemplateLoader):
        def search_path(self):
            from gibe import plugin
            plugin_data = plugin.get_plugin_data(cherrypy.request.blog)
            return plugin_data['template_search_path']
        def dummy(self, value):
            pass
        search_path = property(search_path, dummy)

    old_loader = view.engines['genshi'].loader
    view.engines['genshi'].loader = MyTemplateLoader(search_path =
        old_loader.search_path, auto_reload = old_loader.auto_reload,
        default_encoding = old_loader.default_encoding, default_class =
        old_loader.default_class)
    old_loader = view.engines['genshi-markup'].loader
    view.engines['genshi-markup'].loader = MyTemplateLoader(search_path =
        old_loader.search_path, auto_reload = old_loader.auto_reload,
        default_encoding = old_loader.default_encoding, default_class =
        old_loader.default_class)

noncedir = '/tmp/.nonce'
def authenticate_nonce(id, expires=None, data=''):
    """Authenticate a nonce.  Optional parameters include an expiration date
    and data to be logged with the nonce.

    Written by Sam Ruby, licensed under the Python license, and located at:
        http://intertwingly.net/stories/2003/09/04/nonce.py
    """
    import glob, time, md5, os, os.path

    # default expiration to thirty minutes from now
    if not expires:
        expires = int(time.time() + 1800)

    if not os.path.exists(noncedir):
        os.mkdir(noncedir)

    # produce a legal file name from the id
    filename = os.path.join(noncedir, md5.new(id).hexdigest())

    # remove any expired nonces
    for name in glob.glob(os.path.join(noncedir, '*')):
        if os.stat(name).st_mtime < time.time():
            os.remove(name)

    # if the file exists, authentication fails
    if os.path.exists(filename):
        return False

    # record this nonce
    record = open(filename, 'w')
    record.write(data)
    record.close()

    # mark when this nonce will expire
    os.utime(filename, (expires, expires))

    # successful authentication
    return True
