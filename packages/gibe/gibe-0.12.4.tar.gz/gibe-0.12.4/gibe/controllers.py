import logging

import cherrypy

import turbogears
from turbogears import controllers, expose, validate, redirect, error_handler
from turbogears import identity, view, widgets, validators, paginate, flash
from turbogears import mochikit
from turbogears.database import session

from gibe import json, model
import routes

from datetime import datetime, timedelta
from gibe.util import slugify, excerptify, commaise, sanitise, display_entries

log = logging.getLogger("gibe.controllers")

from turbogears.decorator import weak_signature_decorator

from urllib2 import URLError

from gibe import plugin

blog_plugin_data = {}

from gibe.util import install_template_loader
from gibe.plugin import get_plugin_data, add_plugin_data

class Root(controllers.RootController):
    def __init__(self, *args, **kw):
        super(Root, self).__init__(*args, **kw)
        self._blogController = BlogController()

    @expose(template="gibe.templates.welcome")
    @add_plugin_data(template="gibe.templates.welcome")
    def index(self):
        import time
        log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())

    @expose(template="gibe.templates.login")
    @add_plugin_data(template="gibe.templates.login")
    def _login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    @add_plugin_data()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

    @expose()
    @add_plugin_data()
    def default(self, *args, **kw):
        blog = model.Blog.get_by(slug=args[0])
        if blog:
            return self._blogController.route(blog, *args[1:], **kw)
        raise cherrypy.NotFound()

def post_expand(kargs):
    if 'post' not in kargs:
        return kargs

    post = kargs.pop('post')
    kargs['year'] = post.creation_time.year
    kargs['month'] = "%02d" % (post.creation_time.month,)
    kargs['day'] = "%02d" % (post.creation_time.day,)
    kargs['slug'] = post.slug

    return kargs

def adminpost_expand(kargs):
    if 'post' not in kargs:
        return kargs

    post = kargs.pop('post')
    kargs['postid'] = post.post_id

    return kargs

def tag_expand(kargs):
    if 'tag' not in kargs:
        return kargs

    tag = kargs.pop('tag')
    kargs['tagname'] = tag.name

    return kargs

def tag_condition(environ, match_dict):
    if environ['PATH_INFO'].endswith('.html'):
        return False
    return True

def date_expand(d):
    if 'month' in d:
        d['month'] = "%02d" % (int(d['month']))
    if 'day' in d:
        d['day'] = "%02d" % (int(d['day']))
    if 'date' in d:
        del d['date']
    return d

def date_expand_day(d):
    if 'date' in d:
        if 'year' not in d:
            d['year'] = d['date'].year
        if 'month' not in d:
            d['month'] = d['date'].month
        if 'day' not in d:
            d['day'] = d['date'].day
    return date_expand(d)

def date_expand_month(d):
    if 'date' in d:
        if 'year' not in d:
            d['year'] = d['date'].year
        if 'month' not in d:
            d['month'] = d['date'].month
    return date_expand(d)

def date_expand_year(d):
    if 'date' in d:
        if 'year' not in d:
            d['year'] = d['date'].year
    return date_expand(d)
 
from tinymce import TinyMCE
class PostFormFields(widgets.WidgetsList):
    title = widgets.TextField(validator=validators.NotEmpty,
        label = "Title", attrs=dict(size="30"))
    content = TinyMCE(validator=validators.NotEmpty, label = "Content",
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
            convert_newlines_to_brs = False,
            force_br_newlines = False,
        ),
        rows=25,
        cols=65,
    )

#post_form = widgets.TableForm(fields=PostFormFields(), submit_text="Post")

class AdminController(object):
    _post_form = None
    def post_form(self):
        if self._post_form:
            return self._post_form
        ws = plugin.post_edit_widgets(None, None)
        self._post_form = widgets.TableForm(fields=ws, submit_text="Post")
        return self._post_form

    @expose(template="genshi:gibe.templates.adminpost", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    @paginate('comments', limit = 25)
    def post(self, blog, postid, **kw):
        post = model.Post.get_by(post_id = postid)

        comments = list(post.comments)
        context = {'post': post}
        return dict(blog=blog, post_form = self.post_form(), post_form_values = plugin.post_edit_values(blog, post, context), post = post,
            comments = comments, approved_comments =
            post.approved_comments, mochikit = mochikit, post_form_params = plugin.post_edit_params(blog, post, context))

    @expose(template="genshi:gibe.templates.writepost", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    def writepost(self, blog, **kw):
        post = None
        context = {}
        return dict(blog=blog, post_form = self.post_form(), post_form_values = plugin.post_edit_values(blog, post, context), post_form_params = plugin.post_edit_params(blog, post, context))

    @error_handler(writepost)
    @identity.require(identity.in_group("admin"))
    @validate(form=post_form)
    @add_plugin_data()
    def newpost(self, blog, title, content, **kw):
        p = model.Post(title=title, content=content, author_id = 1, published = True, creation_time = datetime.now(), modification_time=datetime.now(), blog_id = blog.blog_id, slug = slugify(title, model.Post))
        kw['title'] = title
        kw['content'] = content
        p.excerpt = excerptify(p)
        context = {}
        plugin.post_edit_handle_after(blog, p, kw, context)
        session.save(p)
        raise routes.redirect_to('posts', post = p)

    @error_handler(post)
    @identity.require(identity.in_group("admin"))
    @validate(form=post_form)
    @add_plugin_data()
    def updatepost(self, blog, postid, title, content, **kw):
        p = model.Post.get_by(post_id = postid)
        p.title = title
        p.content = content
        context = {}
        kw['title'] = title
        kw['content'] = content
        p.excerpt = excerptify(p)
        plugin.post_edit_handle_after(blog, p, kw, context)
        session.update(p)
        raise routes.redirect_to('adminpost', post = p)

    @expose(template="genshi:gibe.templates.adminposts", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    @paginate('posts', limit = 25)
    def posts(self, blog, **kw):
        return dict(blog=blog, posts = model.Post.select(order_by=model.desc(model.Post.c.creation_time)))

    @expose(template="genshi:gibe.templates.admincomments", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    @paginate('comments', limit = 25)
    def comments(self, blog, **kw):
        return dict(blog=blog, comments =
        model.Comment.select(order_by=model.desc(model.Comment.c.posted_time)),
        mochikit = mochikit)

    @expose(template="genshi:gibe.templates.admincomments", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    @paginate('comments', limit = 25)
    def unapproved_comments(self, blog, **kw):
        return dict(blog=blog, comments =
            model.Comment.select(model.Comment.c.approved == False, order_by=model.desc(model.Comment.c.posted_time)),
            mochikit = mochikit)

    @expose(template="genshi:gibe.templates.adminindex", content_type='text/html; charset=utf-8')
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    def index(self, blog, **kw):
        return dict(blog=blog, post_form = self.post_form())

    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    def stop_comments(self, blog, **kw):
        post = model.Post.get_by(post_id = kw['postid'])
        post.accept_comments = False
        session.save(post)
        raise routes.redirect_to('adminpost', post=post)

    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    def start_comments(self, blog, **kw):
        post = model.Post.get_by(post_id = kw['postid'])
        post.accept_comments = True
        session.save(post)
        raise routes.redirect_to('adminpost', post=post)
        
    @identity.require(identity.in_group("admin"))
    @add_plugin_data()
    def remove_comments(self, blog, post = None, **kw):
        comment_ids = kw.get('comment_id', [])
        import types
        if type(comment_ids) in types.StringTypes:
            comment_ids = [comment_ids]
        for comment_id in comment_ids:
            c = model.Comment.get_by(comment_id = comment_id)
            session.delete(c)
        if kw.get('return_url', None):
           raise cherrypy.HTTPRedirect(kw['return_url'])
        if post:
           raise routes.redirect_to('adminpost', post=post)
        raise routes.redirect_to("admincomments")

from gibe.feeds import FeedController

class TagController(object):
    @expose(template="genshi:gibe.templates.archives", content_type='text/html; charset=utf-8')
    @add_plugin_data()
    @paginate('posts', limit = 10)
    def tag(self, blog, tagname, **kw):
        t = model.Tag.get_by(name=tagname)
        if not t:
            raise cherrypy.NotFound()
    
        posts = t.recent_posts(limit = None)
        return dict(blog=blog, posts=posts, tag=t)

class BlogController(object):
    blog_is_root = False

    def __init__(self, *args, **kw):
        super(BlogController, self).__init__(*args, **kw)
        import re
        self._base_re = re.compile(r'^(?P<protocol>[a-zA-Z]+)://(?P<host>.*)' )
        from turbogears.startup import call_on_startup
        call_on_startup.append(self._create_mapper)

    def _redirect(self, url):
        raise cherrypy.HTTPRedirect(url, 302)

    def _create_mapper(self):
        self._mapper = routes.Mapper()
        mapper = self._mapper

        gibe_controllers['self'] = self

        maps = []
        maps.append(('frontpage', '', dict(controller='self', action='frontpage')))
        maps.append(('frontpage_redirect', 'redirect', dict(controller='self', action='frontpage_redirect')))
        maps.append(('index.html', 'index.html', dict(controller='self', action='frontpage')))
        maps.append(('posts', 'archives/:year/:month/:day/:slug', dict(controller='self', action='post', _filter=post_expand)))
        maps.append(('posts_by_id', ':(postid).html', dict(controller='self', action='post', requirements=dict(postid=r'\d+'))))
        maps.append(('archives_day', 'archives/:year/:month/:day/', dict(controller='self', action='archives_day', _filter=date_expand_day)))
        maps.append(('archives_month', 'archives/:year/:month/', dict(controller='self', action='archives_month', _filter=date_expand_month)))
        maps.append(('archives_month_deprecated', ':(year)-:(month).html', dict(controller='self', action='archives_month', _filter=date_expand_month, requirements=dict(year='\d{4,}', month='\d{1,2}'))))
        maps.append(('archives_year', 'archives/:year/', dict(controller='self', action='archives_year', _filter=date_expand_year)))
        maps.append(('archives', 'archives', dict(controller='self', action='archives')))
        maps.append(('writepost', 'admin/posts/write', dict(controller='adminController', action='writepost')))
        maps.append(('newpost', 'admin/posts/new', dict(controller='adminController', action='newpost')))
        maps.append(('updatepost', 'admin/posts/update/:postid', dict(controller='adminController', action='updatepost', _filter=adminpost_expand)))
        maps.append(('login', 'login', dict(controller='self', action='login')))
        maps.append(('logout', 'logout', dict(controller='self', action='logout')))
        maps.append(('email.js', 'email_js/:section', dict(controller='self', action='email_js', section = "start")))
        maps.append(('rss2.0.xml', 'rss2.0.xml', dict(controller='feedController', action='rss2_0')))
        maps.append(('atom1_0', 'atom1.0', dict(controller='feedController', action='atom1_0')))

        maps.append(('add_comment', 'form/add_comment', dict(controller='commentController', action='add_comment')))
        maps.append(('adminposts', 'admin/posts', dict(controller='adminController', action='posts')))
        maps.append(('stop_comments', 'admin/post/:postid/stop_comments', dict(controller='adminController', action='stop_comments', _filter=adminpost_expand)))
        maps.append(('start_comments', 'admin/post/:postid/start_comments', dict(controller='adminController', action='start_comments', _filter=adminpost_expand)))
        maps.append(('adminpost', 'admin/post/:postid', dict(controller='adminController', action='post', _filter=adminpost_expand)))
        maps.append(('remove_comments', 'admin/comments/remove', dict(controller='adminController', action='remove_comments', _filter=adminpost_expand)))
        maps.append(('comments', 'admin/comments', dict(controller='adminController', action='comments')))
        maps.append(('unapproved_comments', 'admin/unapproved_comments', dict(controller='adminController', action='unapproved_comments')))
        maps.append(('admin', 'admin', dict(controller='adminController', action='index')))

        plugin.map_routes(None, maps, gibe_controllers)

        for m in maps:
            if '_method' in m[2]:
                if 'conditions' in m[2]:
                    m[2]['conditions']['method'] = m[2]['_method']
                else:
                    m[2]['conditions'] = dict(method = m[2]['_method'])

        for m in maps:
            mapper.connect(m[0], m[1], **m[2])

    @expose(template="genshi:gibe.templates.archives", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.archives")
    @paginate('posts', limit = 10)
    def archives(self, blog, **kw):
        posts = model.Post.select(order_by=model.desc(model.Post.c.creation_time))
        #display_entries = []
        #last = None
        #for entry in last_entries:
        #    this = datetime(year=entry.creation_time.year, month=entry.creation_time.month, day=entry.creation_time.day)
        #    if last != this:
        #        last = this
        #        last_list = (last, [])
        #        display_entries.append(last_list)
        #
        #    last_list[1].append(entry)
        return dict(blog=blog, link = routes.url_for('frontpage'), posts = posts)
    archives.exposed = False

    @expose(template="genshi:gibe.templates.archives", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.archives")
    @paginate('posts', limit = 10)
    def archives_day(self, blog, year, **kw):
        st = datetime(year = int(year), month = int(kw.get('month', 1)), day = int(kw.get('day', 1)))
        day = kw.get('day')
        month = kw.get('month')
        if day:
            et = st + timedelta(days=1)
        elif month:
            et = st + timedelta(days=32)
            et = datetime(et.year, month=et.month, day=1)
        else:
            et = st + timedelta(days=366)
            et = datetime(et.year, month=1, day=1)

        posts = model.Post.select(model.Post.c.creation_time.between(st, et), order_by=model.desc(model.Post.c.creation_time))
        return dict(blog=blog, link = routes.url_for('frontpage'), posts = posts)
    archives_day.exposed = False
    archives_month = archives_day
    archives_year = archives_day

    @expose(content_type="text/javascript")
    def email_js(self, blog, section, **kw):
        #log.info("section=%s" % (section,))
        if section == "end":
            return """document.write('</a>');"""
        else:
            return """document.write('<a href="mailto:nbm' + '@' + 'mithrandr.moria.org">');"""
    email_js.exposed = False

    def _configure_mapper(self, blog):

        base = cherrypy.request.base
        d = self._base_re.match(base).groupdict()
        host = d['host']
        proto = d['protocol']

        config = routes.request_config()
        config.mapper = self._mapper
        host = cherrypy.config.get('gibe.hostname', host)
        config.host = host
        config.protocol = proto
        config.redirect = self._redirect

        path = "/"

        # Pure evil...
        if not self.blog_is_root:
            path = '/%s' % (blog.slug)

        path = turbogears.url(path)
        if path[-1] == "/":
            path = path[:-1]

        from cherrypy.filters.wsgiappfilter import make_environ
        environ = make_environ()
        #logging.info(str(environ))
        environ['SERVER_PORT'] = str(cherrypy.config.get('gibe.port', cherrypy.config.get('server.socket_port')))
        environ['SCRIPT_NAME'] = path
        #logging.info("SCRIPT_NAME is %s" % (environ['SCRIPT_NAME'],))
        config.environ = environ

        return config

    def route(self, blog, *args, **kw):
        cherrypy.request.blog = blog
        install_template_loader()
        config = self._configure_mapper(blog)
        import os.path
        if len(args):
            path = "/" + os.path.join(*args)
        else:
            path = "/"
        mapper_dict = self._mapper.match(path)
        if not mapper_dict:
            raise cherrypy.NotFound()
            return str(dict(path=path, mapper_dict=mapper_dict, args=args, blog=blog))

        controller = gibe_controllers[mapper_dict['controller']]
        try:
            action = getattr(controller, mapper_dict['action'])
        except AttributeError:
            raise cherrypy.NotFound()

        kw['blog'] = blog
        del mapper_dict['controller']
        kw.update(mapper_dict)
        return action(**kw)

    @expose(template="genshi:gibe.templates.post", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.post")
    def post(self, blog, **kw):
        if 'postid' in kw:
            post = model.Post.get_by(post_id = kw['postid'])
        if 'slug' in kw:
            post = model.Post.get_by(slug = kw['slug'])

        id = post.post_id

        previous_post = model.Post.select(model.Post.c.post_id < id, order_by=model.desc(model.Post.c.post_id), limit = 1)
        next_post = model.Post.select(model.Post.c.post_id > id, order_by=model.asc(model.Post.c.post_id), limit = 1)
        if previous_post:
            previous_post = previous_post[0]
        if next_post:
            next_post = next_post[0]

        import commenting
        context = {}
        return dict(blog=blog,
            post = post,
            previous_post = previous_post,
            next_post = next_post,
            url_for = routes.url_for,
            comment_form = commenting.comment_form,
            accept_comments = post.accept_comments
        )

    @error_handler(post)
    #@validate(form=commenting.comment_form)
    def add_comment(self, blog, **kw):
        return commenting.commentController.add_comment(blog, **kw)

    @expose(template="genshi:gibe.templates.frontpage", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.frontpage")
    @paginate('posts', limit = 25)
    def frontpage(self, blog, **kw):
        posts = model.Post.select(order_by=model.desc(model.Post.c.creation_time))
        return dict(blog=blog, link = routes.url_for('frontpage'), posts = posts)

    @expose()
    def frontpage_redirect(self, blog, **kw):
        return routes.redirect_to('frontpage')

    @expose(template="genshi:gibe.templates.login", content_type='text/html; charset=utf-8')
    @add_plugin_data()
    def login(self, blog, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(blog=blog, message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)
    login.exposed = False

    @expose()
    @add_plugin_data()
    def logout(self, blog, *args, **kw):
        identity.current.logout()
        raise redirect("/")
    logout.exposed = False

class RootBlogController(BlogController, controllers.RootController):
    blog_is_root = True

    def __init__(self, blog, *args, **kw):
        super(RootBlogController, self).__init__(*args, **kw)
        self.blog = blog

    @expose()
    def default(self, *args, **kw):
        return self.route(self.blog, *args, **kw)

    @expose()
    def index(self, *args, **kw):
        return self.route(self.blog, *args, **kw)

import urlparse

def comment_class(comment):
    if comment.approved:
        return "gibe_comment_approved"
    return "gibe_comment_unapproved"

from genshi.core import Attrs, QName, Stream, stripentities
from genshi.core import DOCTYPE, START, END, START_NS, END_NS, TEXT, \
                        START_CDATA, END_CDATA, PI, COMMENT
def myET(element):
    """Convert a given ElementTree element to a markup stream."""
    tag_name = QName(element.tag.lstrip('{'))
    attrs = Attrs((QName(k), v) for k, v in element.items())

    yield START, (tag_name, attrs), (None, -1, -1)
    if element.text:
        yield TEXT, element.text, (None, -1, -1)
    for child in element.getchildren():
        for item in myET(child):
            yield item
    yield END, tag_name, (None, -1, -1)
    if element.tail:
        yield TEXT, element.tail, (None, -1, -1)

def add_usual_suspects(d):
    d['url_for'] = routes.url_for
    d['production'] = (cherrypy.config.get('server.environment', '') == 'production')
    d['commaise'] = commaise
    # has the query string
    d['browser_url'] = cherrypy.request.browser_url


    url_parts = list(urlparse.urlparse(cherrypy.request.browser_url))
    url_parts[4] = None
    # no query string
    d['base_url'] = urlparse.urlunparse(url_parts)

    d['comment_class'] = comment_class
    d['display_entries'] = display_entries
    d['ET'] = myET

    return

view.variable_providers.append(add_usual_suspects)

gibe_controllers = {}
def getControllers():
    import commenting
    return dict(
        adminController=AdminController(),
        feedController=FeedController(),
        #tagController=TagController(),
        commentController=commenting.CommentController(),
    )
gibe_controllers.update(getControllers())

