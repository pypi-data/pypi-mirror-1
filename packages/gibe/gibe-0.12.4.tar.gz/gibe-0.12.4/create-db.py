#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy
cherrypy.lowercase_api = True

from os.path import *
import sys

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    turbogears.update_config(configfile=sys.argv[1], 
        modulename="gibe.config")
elif exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile="dev.cfg",
        modulename="gibe.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="gibe.config")

from turbogears.startup import startTurboGears
from gibe.controllers import Root, RootBlogController
from gibe.model import *

import cherrypy
cherrypy.root = Root()
startTurboGears()

User.table.create()
Group.table.create()
Permission.table.create()
Blog.table.create()
Post.table.create()
Visit.table.create()
VisitIdentity.table.create()
Tag.table.create()
Comment.table.create()

poster_blog.create()
user_group.create()
group_permission.create()
post_tag.create()

transaction = session.create_transaction()
u = User(about="Vainglorious open source personality",
    display_name="Neil Blakey-Milner",
    email_address = "nbm@mithrandr.moria.org", password = "asdf",
    user_id = 1, user_name = "nbm")
session.save(u)
g = Group(group_name = "admin", display_name = "Admin")
session.save(g)
g.users.append(u)
b = Blog(blog_id = 1, owner_id = 1, name = "Cosmic Seriosity Balance",
    slug = "cosmic-seriosity-balance",
    tagline = "Maintaining the Cosmic Seriosity Balance")
session.save(b)
transaction.commit()
session.close()
