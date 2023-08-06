import pkg_resources
import cherrypy
from turbogears import widgets, validators, error_handler, validate, flash, expose
from turbogears.database import session

from gibe.plugin import get_plugin_data, add_plugin_data
import gibe.util

class Commenting(object):
    def convert(self, kw):
        """
        Convert the data from the comment form into something you'd like to
        work with.
        """
        pass
    def post_save(self, kw):
        """
        Actions to take after saving a comment.
        """
        pass

format_registry = {}
for comment_format_mod in pkg_resources.iter_entry_points("gibe.comment_formats"):
    mod = comment_format_mod.load()
    format_registry[comment_format_mod.name] = mod

from turbogears.validators import FancyValidator, Invalid
class NonceValidator(FancyValidator):
    messages = {
        'badFormat': 'Invalid nonce',
        'empty': 'No nonce, please preview',
    }

    def _to_python(self, value, state):
        if not value:
            raise Invalid(self.message('empty', state), value, state)

        if not gibe.util.authenticate_nonce(value):
            raise Invalid(self.message('badFormat', state), value, state)

        return value

def fields():
    formats = []

    formats_to_check = [
        cherrypy.config.get('gibe.comment_format.preferred'),
        cherrypy.config.get('gibe.comment_format.fallback', None),
        ['postmarkup', 'tinymce'],
    ]

    for fs in formats_to_check:
        if isinstance(fs, (str, unicode)):
            fs = [fs]
        for f in fs:
            if f not in formats:
                formats.append(f)

    # Look through each format...
    for format in formats:
        # And use the first match in the registry
        if format in format_registry:
            class CommentFormFields(widgets.WidgetsList):
                postid = widgets.HiddenField()

                nonce = widgets.HiddenField(validator=validators.All(validators.NotEmpty, NonceValidator))

                content_format = widgets.HiddenField(default=format,
                    validator=validators.OneOf(format_registry.keys()))

                name = widgets.TextField(validator=validators.NotEmpty,
                    label = "Your name", attrs=dict(size=60))

                email = widgets.TextField(label = "Email",
                    validator=validators.All(validators.Email, validators.NotEmpty),
                    attrs=dict(size=60))

                website = widgets.TextField(validator=validators.URL,
                    label = "Site", attrs=dict(size=60))

            comment_form_fields = CommentFormFields()

            format_registry[format].addCommentFields(comment_form_fields)
            return comment_form_fields

comment_form = widgets.TableForm(fields=fields(), submit_text="Post")

akismet = None
try:
    from akismet import Akismet
    if cherrypy.config.get("akismet.key"):
        akismet = Akismet(
            agent="Gibe",
            key=cherrypy.config.get("akismet.key"),
            blog_url=cherrypy.config.get("akismet.url")
        )
        akismet.verify_key()
except (ImportError, URLError), e:
    pass

turbomail = None
try:
    if cherrypy.config.get('mail.on', False) != False:
        import turbomail
except:
    pass

import routes
from gibe.model import Post, Comment, User

from datetime import datetime, timedelta

import uuid
def _make_nonce():
    return uuid.uuid4()

class CommentController(object):
    def post(self, blog, **kw):
        """
        Error handler for add_comment - just forward to the main post page.
        """
        from gibe.controllers import gibe_controllers
        return gibe_controllers['self'].post(blog=blog, **kw)

    def preview(self, blog, **kw):
        return self._preview(blog=blog, **kw)

    @expose(template="genshi:gibe.templates.comment_preview", content_type='text/html; charset=utf-8')
    @add_plugin_data(template="genshi:gibe.templates.comment_preview")
    def _preview(self, blog, tg_errors=None, **kw):
        if len(tg_errors) ==1:
            if 'nonce' in tg_errors:
                flash("Please confirm your post content before publication")

        cherrypy.request.input_values['nonce'] = _make_nonce()

        post = Post.get_by(post_id = kw['postid'])
        return dict(blog=blog, post=post, comment_form=comment_form)

    @error_handler(preview)
    @validate(form=comment_form)
    def add_comment(self, blog, **kw):
        post = Post.get_by(post_id = kw['postid'])
        if not post.accept_comments:
            flash("Post does not allow comments")
            raise routes.redirect_to('posts', post = post)

        content_format = kw['content_format']
        commenting = format_registry[content_format].Commenting()

        commenting.convert(kw)

        ckw = {
            'post_id': kw['postid'], 
            'blog_id': blog.blog_id, 
            'author_name': kw['name'],
            'author_url': kw['website'],
            'author_email': kw['email'],
            'content': kw['comment'],
            'approved': True,
            'posted_time': datetime.now(),
            'content_format': kw['content_format'],
        }

        c = Comment(**ckw)

        commenting.post_save(kw)

        self._check_for_spam(blog, c, kw)

        try:
            c.getContentHtml()
            c.getExcerptHtml()
        except:
            flash("Could not render comment, marked for moderation")
            c.approved = False
            session.save(c)

        raise routes.redirect_to('posts', post = post)


    def _check_for_spam(self, blog, c, kw):
        data = {}
        data['comment_author'] = kw['name'].encode('utf-8')
        data['comment_author_email'] = kw['email'].encode('utf-8')
        if kw['website']:
            data['comment_author_url'] = kw['website'].encode('utf-8')

        data['user_ip'] = cherrypy.request.headers.get('Remote-Addr')
        data['user_agent'] = cherrypy.request.headers.get('User-Agent', '')

        try:
            if akismet and akismet.comment_check(kw['comment'].encode('utf-8'), data):
                c.approved = False
        except IOError:
            # When approval is around, set .approved to False
            c.approved = False

        session.save(c)
        if c.approved == False:
            flash("Comment marked for moderation")
        else:
            flash("Comment added")

        if turbomail:
            try:
                #from_address = kw['email']
                to_address = User.get_by(user_id = blog.owner_id).email_address
                from_address = to_address
                if c.approved == False:
                    subject = "A possible spam comment awaits moderation on post %s" % (post.title)
                else:
                    subject = "A comment was made on post %s" % (post.title)
                message = turbomail.Message(from_address, to_address, subject)
                message.plain = u"""
    Post by %(name)s, email address %(email)s, site %(website)s

    Comment:

    %(comment)s
    """ % kw
                message.plain = message.plain.encode('utf-8', 'replace')
                turbomail.enqueue(message)
            except Exception:
                pass

commentController = CommentController()

