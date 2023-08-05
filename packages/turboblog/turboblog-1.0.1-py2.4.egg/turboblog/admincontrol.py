import turbogears, re, antispam, random, threading, formencode
from turbogears import feed, identity
#from model import *
from model import Blog, Settings, hub, Post, Comment, Tag, \
        User, Group

from turbogears import validators
from turbojson.jsonify import jsonify
from pager import pager
from sqlobject.sqlbuilder import AND
from turbogears import validators
# new imports added during port to TG 1.0.1
import turbogears as tg
from turbogears import expose
from turbogears.controllers import Controller

settings = Settings.get(1)

class AdminController(Controller, identity.SecureResource):
    require = identity.has_permission('can_admin')

    @turbogears.expose()
    def delete_blog(self, *args, **kw):
        if settings.default_blog == int(kw['bid']):
            turbogears.flash(_('Cannot delete default blog!'))
        else:
            hub.begin()
            Blog.delete(kw['bid'])
            hub.commit()
        tg.redirect('/admin/blogs')

    @turbogears.expose()
    def user_create(self, *args, **kw):
        groups = kw['groups'].split(',')
        validators.FieldsMatch('psw', 'psw2').to_python(kw)
        hub.begin()
        u = User(user_name=kw['login'], display_name=kw['fullname'],
                password=kw['psw'], email_address=kw['email'],
                avatar=None,about='')

        for g in groups:
            print 'adding: ', g
            u.addGroup(Group.by_group_name(g))
        hub.commit()
        return dict(user_name=u.user_name,display_name=kw['fullname'])

    @turbogears.expose()
    def user_delete(self, *args, **kw):
        hub.begin()
        User.delete(kw['uid'])
        hub.commit()
        return dict()

    @turbogears.expose()
    def user_update(self, *args, **kw):
        groups = kw['groups'].split(',')
        validators.FieldsMatch('psw', 'psw2').to_python(kw)
        hub.begin()
        u = User.get(kw['uid'])
        u.emailAddress = emailAddress=kw['email']
        u.display_name = kw['fullname']
        u.password = kw['psw']
        for g in u.groups[:]:
            u.removeGroup(g)
        for g in groups:
            u.addGroup(Group.by_group_name(g))
        hub.commit()
        return dict(user_name=u.user_name, display_name=kw['fullname'])


    @turbogears.expose()
    def create_blog(self, *args, **kw):
        bn = kw['name']
        bt = kw['tagline']
        bo = User.get(kw['owner'])
        hub.begin()
        Blog(name=bn, tagline=bt, owner=bo)
        hub.commit()
        tg.redirect('/admin/blogs')

    @turbogears.expose(html="turboblog.templates.admin.blogs")
    def blogs(self):
        return dict(defblog=settings.default_blog,
                curadmin=settings.admin)

    @turbogears.expose()
    def index(self):
        return self.blogs()

    @turbogears.expose(html="turboblog.templates.admin.users")
    def users(self, *args, **kw):
        return dict(users=User.select(), groups=Group.select())

    @turbogears.expose()
    def user_info(self, uid):
        z = {}
        for p in Group.select():
            z[p.group_name] = { 'id' : p.id, 'desc':p.display_name }
        return dict(user=User.get(uid), allgroup=z)

    @turbogears.expose()
    def set_admin(self, **kwargs):
        hub.begin()
        settings.admin = User.get(kwargs['aid'])
        hub.commit()
        return dict()
 
    @turbogears.expose()
    def set_default(self, **kwargs):
        hub.begin()
        settings.default_blog = int(kwargs['defblog'])
        hub.commit()
        return dict()
 
class BlogAdminController(Controller, identity.SecureResource):
    require = identity.has_permission('can_admin_blog')

    def kick(self, kw):
        blog = Blog.get(kw['bid'])
        if not identity.current.user == blog.owner \
                and not identity.current.user == settings.admin:
            raise identity.IdentityFailure(_("You are not this blog's owner!"))

    @turbogears.expose()
    def rename_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.name = kw['tag']
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @turbogears.expose()
    def add_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag(name=kw['tag'], blogID=blog.id)
        blog.addTag(tag)
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @turbogears.expose()
    def delete_post(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        post = Post.get(kw['pid'])
        post.deleteMe()
        hub.commit()
        tg.redirect('/blog_admin/manage_posts?bid='+kw['bid'])

    @turbogears.expose()
    def delete_comment(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        c = Comment.get(kw['cid'])
        c.destroySelf()
        hub.commit()
        tg.redirect('/blog_admin/manage_comments?bid='+kw['bid'])

    @turbogears.expose()
    def delete_comments(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        for cid in kw['delete_comments[]']:
            c = Comment.get(cid)
            c.destroySelf()
        hub.commit()
        tg.redirect('/blog_admin/manage_comments?mass=1;bid='+kw['bid'])

    @turbogears.expose()
    def delete_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.deleteMe()
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @turbogears.expose()
    def new_post(self, *args, **kw):
        self.kick(kw)
        u = validators.URL(add_http=False, check_exists=False)
        for tburl in kw.get('trackback_url','').split(' '):
            if tburl:
                print u.to_python(tburl)
        user = identity.current.user
        blog = Blog.get(kw['bid'])
        pub = 'publish' in kw
        edit = ('edit' in kw) or ('publishedit' in kw)
        hub.begin()
        if edit:
            p = Post.get(kw['post_id'])
            p.title = kw['post_title']
            p.content = kw['content']
            p.published = 'publishedit' in kw
            p.trackback_urls = kw['trackback_url']

        else:
            p = Post(title = kw['post_title'],
                    content = kw['content'],
                    author = user,
                    published = pub,
                    blog = blog,
                    trackback_urls = kw['trackback_url']
                    )

        hub.commit()
        if p.published:
            p.send_trackbacks()
        tg.redirect('/blog_admin/manage?bid=%d'%blog.id)
 
    @turbogears.expose(html="turboblog.templates.blog_admin.dash")
    def dash(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.manage_tags")
    def manage_tags(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.manage_comments")
    def manage_comments(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        mass = False
        if 'mode' in kw:
            mass = kw['mode'] == 'mass'
        return dict(blog=blog, mass=mass)

    @turbogears.expose(html="turboblog.templates.blog_admin.manage_posts")
    def manage_posts(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.settings_general")
    def settings_general(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.settings_comments")
    def settings_comments(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.settings_reading")
    def settings_reading(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @turbogears.expose(html="turboblog.templates.blog_admin.write")
    def write(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        post = None
        if 'pid' in kw:
            post = Post.get(kw['pid'])
        return dict(blog=blog, post=post)

    @turbogears.expose()
    def manage(self, *args, **kw):
        return self.manage_posts(*args, **kw)

    @turbogears.expose()
    def index(self, *args, **kw):
        return self.dash(*args, **kw)

    @turbogears.expose()
    def settings(self, *args, **kw):
        return self.settings_general(*args, **kw)

    @expose()
    def update_general_settings(self, bid, blogname, blogdescription,
            admin, theme, submit):
        hub.begin()
        blog = Blog.get(bid)

        if not blogname == blog.name:
            blog.name = blogname

        blog.tagline = blogdescription
        blog.ownerID = admin
        blog.theme = theme
        hub.commit()
        tg.flash({'status': "success",
            'msg': _('Settings saved successfully')})
        tg.redirect(tg.url('/blog_admin/settings?bid=%s' % bid))

    @expose()
    def update_read_settings(self, *args, **kw):
        bid = kw['bid']
        tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        tg.redirect(tg.url('/blog_admin/settings?bid=%s' % bid))

    @expose()
    def update_comments_settings(self, *args, **kw):
        bid = kw['bid']
        tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        tg.redirect(tg.url('/blog_admin/settings?bid=%s' % bid))

# vim: expandtab tabstop=4 shiftwidth=4:
