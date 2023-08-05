#!/usr/bin/env python
import pkg_resources
pkg_resources.require("TurboGears")

import cherrypy
import turbogears
from os.path import *
import sys,os

os.system("del devdata.sqlite")
os.system("c:/python24/scripts/tg-admin sql create -v -v")

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    turbogears.update_config(configfile=sys.argv[1], 
        modulename="turboblog.config")
elif exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile="dev.cfg",
        modulename="turboblog.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="turboblog.config")

from turboblog.model import *
from sqlobject import *
from turbogears.database import PackageHub
#from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
from turboblog.model import User, Group, Permission

hub = PackageHub("turboblog")
__connection__ = hub

turbogears.identity.current_provider = turbogears.identity.create_default_provider()

hub.begin()
print "[i] Creating permissions"
can_admin = Permission(permission_name="can_admin", description="Can add/delete blogs/users")
can_admin_blog = Permission(permission_name="can_admin_blog", description="Can manage one blog")
can_post = Permission(permission_name="can_post", description="Can add posts")
can_comment = Permission(permission_name="can_comment", description="Can add comments")
can_moderate = Permission(permission_name="can_moderate", description="Can approve comments")
hub.commit()

print "[i] Creating groups permissions"
admin = Group(group_name='admin', display_name="Administrators")
#admin.permissions.extend([can_admin, can_post, can_comment, can_moderate, can_admin_blog])
[admin.addPermission(t) for t in [can_admin, can_post, can_comment, can_moderate, can_admin_blog]]

user = Group(group_name='user', display_name="Users")
#user.permissions.append(can_comment)
user.addPermission(can_comment)

poster = Group(group_name='poster', display_name="Posters")
#poster.permissions.extend([can_comment, can_post, can_moderate])
[poster.addPermission(t) for t in [can_comment, can_post, can_moderate]]

blogadmin = Group(group_name='blogadmin', display_name="Blog admins")
#blogadmin.permissions.extend([can_comment, can_post, can_moderate, can_admin_blog])
[blogadmin.addPermission(t) for t in [can_comment, can_post, can_moderate, can_admin_blog]]

hub.commit()

print "[i] Creating admin user"
dude = User(user_name='admin', display_name="Administrator", email_address="me@me.com",
	password="secret", avatar=open('admin.jpg').read(),
	about="A little something about you, the author. Nothing lengthy, just an overview.")
#dude.groups.append(admin)
dude.addGroup(admin)

hub.commit()

print "[i] Creating default blog"
blog = Blog(name="Default blog", tagline="default turboblog!", ownerID=dude.id)
blog.addUser(dude)
hub.commit()

print "[i] Creating test tag"
tag = Tag(name="turboblog", blogID=blog.id)
blog.addTag(tag)
hub.commit()

print "[i] Creating test post"
post = Post(title="Welcome!", content="welcome to turboblog", author=dude, published=True, blog=blog)
post.addTag(tag)
hub.commit()

print "[i] Creating test post comment"
comment = Comment(content="how do u like them apples?", author=dude, approved=True, post=post)

print "[i] Creating test post sub comment"
subcomment = Comment(content="i like em!", author=dude, approved=True, post=post, parent_id=comment.id)
comment.addComment(subcomment)

print "[i] Creating settings"
settings = Settings(admin=dude, default_blog=1)
hub.commit()

