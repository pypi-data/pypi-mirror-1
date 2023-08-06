from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy import *
from sqlalchemy.ext.activemapper import ActiveMapper, column, \
                                    one_to_many, one_to_one, many_to_many

from turbogears import identity 
from turbogears.database import metadata, session

import dispatch

# from identitymodel import Visit, VisitIdentity, Group, Permission, user_group, group_permission

poster_blog = Table("poster_blog", metadata,
                      Column("user_id", Integer,
                              ForeignKey("user.user_id"),
                              primary_key=True),
                      Column("blog_id", Integer,
                              ForeignKey("blog.blog_id"),
                              primary_key=True))

post_tag = Table("post_tag", metadata,
                      Column("post_id", Integer,
                              ForeignKey("post.post_id"),
                              primary_key=True),
                      Column("tag_id", Integer,
                              ForeignKey("tag.tag_id"),
                              primary_key=True))

from elementtree import ElementTree as ET
import operator

class Blog(ActiveMapper):
    class mapping:
        blog_id = column(Integer, primary_key=True)
        owner_id = column(Integer, foreign_key=ForeignKey('user.user_id'))

        name    = column(Unicode(255), unique=True)
        tagline = column(Unicode(255))
        slug = column(Unicode(255))
        theme = column(Unicode(255))

        #owner = relation('User', backref="owned_blogs")
        #posters = many_to_many("User", poster_blog, backref="blogs")
        posts = one_to_many("Post", backref="blog")

        # tags = many_to_many("Tag", blog_tag, backref="blogs")

    def months(self):
        s = select(["YEAR(creation_time) AS year, MONTH(creation_time) AS month"],
        from_obj = [Post.table], distinct=True, order_by=[desc("year"),
        desc("month")])
        c = s.execute()
        for year, month in c:
            yield datetime(year=year, month=month, day=1)
        
    def recent_posts(self, num = 5):
        posts = Post.select(Post.c.blog_id == self.blog_id, order_by=desc(Post.c.creation_time), limit = num)
        # posts.reverse()
        return posts

    def recent_comments(self, num = 5):
        comments = Comment.select((Comment.c.blog_id == self.blog_id) & (Comment.c.approved == True), order_by=desc(Comment.c.posted_time), limit = num)
        return comments

    def all_tags_count(self, min = None, limit = None):
        s = select([post_tag.c.tag_id, func.count(post_tag.c.post_id)], group_by=[post_tag.c.tag_id], order_by=[desc(func.count(post_tag.c.post_id))])
        if limit:
            s.limit = limit
        if min:
            s.having = func.count(post_tag.c.post_id) > min
        r = s.execute()
        for tag_id, num in r:
            yield Tag.get(tag_id), num

    def most_commented(self, num = 5, min = None):
        s = select([Post.c.post_id], Post.c.post_id == Comment.c.post_id, group_by=[Post.c.post_id], order_by=[desc(func.count(Comment.c.comment_id))])
        s.limit = num
        r = s.execute()
        for post_id, in r:
            yield Post.get(post_id)

    def years(self, num = 10, min = None):
        year = func.year(Post.c.creation_time)
        in_that_year = func.count(Post.c.post_id)
        s = select([year, in_that_year], Post.c.post_id > 0, group_by=[year], order_by=[desc(year)])
        s.limit = num
        r = s.execute()
        for res_year, res_in_that_year, in r:
            yield res_year, res_in_that_year

    def months(self, num = 12, year = None, min = None):


        year_column = func.year(Post.c.creation_time)
        month = func.month(Post.c.creation_time)
        in_that_month = func.count(Post.c.post_id)

        if not year:
            first_month_to_return = datetime.now().replace(day=1) - relativedelta(months=12)

            s = select([year_column, month, in_that_month], Post.c.creation_time >= first_month_to_return, group_by=[year_column, month], order_by=[desc(year_column), desc(month)])
        else:
            #first_month_to_return = datetime.date(year=year, month=1, day=1)
            #last_month_to_return = datetime.date(year=year+1, month=1, day=1)

            s = select([year_column, month, in_that_month], func.year(Post.c.creation_time) == year, group_by=[year_column, month], order_by=[desc(year_column), desc(month)])

        s.limit = num
        r = s.execute()
        for res_year, res_month, res_in_that_month, in r:
            yield res_year, res_month, datetime(year=res_year, month=res_month, day=1), res_in_that_month

class Post(ActiveMapper):
    class mapping:
        post_id = column(Integer, primary_key=True)
        blog_id = column(Integer, foreign_key=ForeignKey('blog.blog_id'))
        author_id = column(Integer, foreign_key=ForeignKey('user.user_id'))
        title = column(Unicode(255))
        content = column(Unicode())
        published = column(Boolean, default=False)
        creation_time = column(DateTime)
        modification_time = column(DateTime)
        trackback_urls = column(String)
        slug = column(Unicode(255))
        excerpt = column(Unicode())
        accept_comments = column(Boolean, default=True)
        content_format = column(Unicode(25), default = "html")
        excerpt_format = column(Unicode(25), default = "html")
        manual_excerpt = column(Boolean, default = False)
        
        comments = one_to_many("Comment", backref="post")
        # trackbacks = one_to_many("Trackback", backref="post")
        tags = many_to_many("Tag", post_tag, backref="posts")
        #blog = relation("Blog", backref="posts")

    def approved_comments(self):
        return Comment.select((Comment.c.post_id == self.post_id) & (Comment.c.approved == True))
        
    approved_comments = property(approved_comments)
        
    @dispatch.generic()
    def getContentHtml(self):
        pass

    @getContentHtml.when('self.content_format == "html"')
    def getContentHtmlfromHtml(self):
        return self.content

    @dispatch.generic()
    def getExcerptHtml(self):
        pass

    @getExcerptHtml.when('self.excerpt_format == "html"')
    def getExcerptHtmlfromHtml(self):
        return self.excerpt

    content_html = property(getContentHtml)
    excerpt_html = property(getExcerptHtml)

    def surrounding_posts(self, num = 2, numbefore = None):
        if not numbefore:
            numbefore = num

        posts = Post.select(Post.c.creation_time < self.creation_time, order_by=desc(Post.c.creation_time), limit = numbefore)
        posts += [self]
        posts += Post.select(Post.c.creation_time > self.creation_time, order_by=asc(Post.c.creation_time), limit = num) 

        posts.sort(key=operator.attrgetter("creation_time"))

        return posts

class Tag(ActiveMapper):
    class mapping:
        tag_id = column(Integer, primary_key=True)
        name = column(Unicode(255))
        display_name = column(Unicode(255))

    def recent_posts(self, limit = 5, offset = 0):
        posts = Post.select((Post.c.post_id == post_tag.c.post_id) &
            (post_tag.c.tag_id == self.tag_id),
            order_by=desc(Post.c.creation_time), limit = limit, offset =
            offset)
        return posts

class Comment(ActiveMapper):
    class mapping:
        comment_id = column(Integer, primary_key=True)
        post_id = column(Integer, foreign_key=ForeignKey('post.post_id'))
        blog_id = column(Integer, foreign_key=ForeignKey('blog.blog_id'))
        author_id = column(Integer, foreign_key=ForeignKey('user.user_id'))
        author_name = column(Unicode(255))
        author_url = column(String(255))
        author_email = column(String(255))
        content = column(Unicode())
        posted_time = column(DateTime)
        approved = column(Boolean, default=False)
        content_format = column(Unicode(25), default = "html")

    def getReference(self):
        if not self.author_url:
            span = ET.Element('span')
            span.text = self.author_name
            return span

        a = ET.Element('a')
        a.attrib['href'] = self.author_url
        a.attrib['rel'] = 'nofollow'
        a.text = self.author_name
        return a

    allowed_tags = {
        'a': ['title','href'],
        'abbr': ['title'],
        'acronym': ['title'],
        'b': [],
        'blockquote': [],
        'code': [],
        'em': [],
        'i': [],
        'strike': [],
        'strong': [],
    }

    def cleanContent(self):
        return True
    
    @dispatch.generic()
    def getContentHtml(self):
        pass

    @getContentHtml.when('self.content_format == "html"')
    def getContentHtmlfromHtml(self):
        return self.content

    @dispatch.generic()
    def getExcerptHtml(self):
        pass

    @getExcerptHtml.when('self.content_format == "html"')
    def getExcerptHtmlfromHtml(self):
        return self.content

### Identity models ####################################################

class Visit(ActiveMapper):
    class mapping:
        __table__ = "visit"
        visit_key = column(String(40), primary_key=True)
        created = column(DateTime, nullable=False, default=datetime.now)
        expiry = column(DateTime)

    def lookup_visit(cls, visit_key):
        return Visit.get(visit_key)
    lookup_visit = classmethod(lookup_visit)

# tables for SQLAlchemy identity
user_group = Table("user_group", metadata, 
                      Column("user_id", Integer,
                              ForeignKey("user.user_id"),
                              primary_key=True),
                      Column("group_id", Integer,
                              ForeignKey("group.group_id"),
                              primary_key=True))

group_permission = Table("group_permission", metadata,
                            Column("group_id", Integer,
                                    ForeignKey("group.group_id"),
                                    primary_key=True),
                            Column("permission_id", Integer,
                                ForeignKey("permission.permission_id"),
                                    primary_key=True))

class User(ActiveMapper):
    class mapping:
        __table__ = "user"
        user_id = column(Integer, primary_key=True)
        user_name = column(Unicode(16), unique=True)
        email_address = column(Unicode(255), unique=True)
        display_name = column(Unicode(255))
        password = column(Unicode(40))
        created = column(DateTime, default=datetime.now)

        avatar = column(TEXT)
        about = column(TEXT)

        #groups = many_to_many("Group", user_group, backref="users")
        #blogs = many_to_many("Blog", poster_blog, backref="posters")
        owned_blogs = one_to_many("Blog", backref="owner")
        posts = one_to_many("Post", backref="author")

    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
    permissions = property(permissions)



class VisitIdentity(ActiveMapper):
    class mapping:
        __table__ = "visit_identity"
        visit_key = column(String(40), # foreign_key="visit.visit_key",
                          primary_key=True)
        user_id = column(Integer, foreign_key="user.user_id", index=True)


class Group(ActiveMapper):
    """
    An ultra-simple group definition.
    """
    class mapping:
        __table__ = "group"
        group_id = column(Integer, primary_key=True)
        group_name = column(Unicode(16), unique=True)
        display_name = column(Unicode(255))
        created = column(DateTime, default=datetime.now)

        users = many_to_many("User", user_group, backref="groups")
        permissions = many_to_many("Permission", group_permission,
                                   backref="groups")

class Permission(ActiveMapper):
    class mapping:
        __table__ = "permission"
        permission_id = column(Integer, primary_key=True)
        permission_name = column(Unicode(16), unique=True)
        description = column(Unicode(255))

        #groups = many_to_many("Group", group_permission,
        #                      backref="permissions")
