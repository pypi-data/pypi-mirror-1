import turbogears, re, antispam, random, threading, formencode
from turbogears import feed, identity
#from model import *
from model import Blog, Settings, hub, Post, Comment, Tag, \
        User, Group, StoredFile

from turbojson.jsonify import jsonify
from pager import pager
from sqlobject.sqlbuilder import AND
from turbogears import validators
# new imports added during port to TG 1.0.1
import turbogears as tg
from turbogears import expose
from turbogears.controllers import Controller
from turbogears import validate

from turboblog.forms import file_upload_form, writepost_form

settings = Settings.get(1)

class AdminController(Controller, identity.SecureResource):
    require = identity.has_permission('can_admin')

    @expose()
    def delete_blog(self, *args, **kw):
        if settings.default_blog == int(kw['bid']):
            turbogears.flash(_('Cannot delete default blog!'))
        else:
            hub.begin()
            Blog.delete(kw['bid'])
            hub.commit()
        tg.redirect('/admin/blogs')

    @expose()
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

    @expose()
    def user_delete(self, *args, **kw):
        hub.begin()
        User.delete(kw['uid'])
        hub.commit()
        return dict()

    @expose()
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


    @expose()
    def create_blog(self, *args, **kw):
        bn = kw['name']
        bt = kw['tagline']
        bo = User.get(kw['owner'])
        hub.begin()
        Blog(name=bn, tagline=bt, owner=bo)
        hub.commit()
        tg.redirect('/admin/blogs')

    @expose(html="turboblog.templates.admin.blogs")
    def blogs(self):
        return dict(defblog=settings.default_blog,
                curadmin=settings.admin)

    @expose()
    def index(self):
        return self.blogs()

    @expose(html="turboblog.templates.admin.users")
    def users(self, *args, **kw):
        return dict(users=User.select(), groups=Group.select())

    @expose()
    def user_info(self, uid):
        z = {}
        for p in Group.select():
            z[p.group_name] = { 'id' : p.id, 'desc':p.display_name }
        return dict(user=User.get(uid), allgroup=z)

    @expose()
    def set_admin(self, **kwargs):
        hub.begin()
        settings.admin = User.get(kwargs['aid'])
        hub.commit()
        return dict()
 
    @expose()
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

    @expose()
    def rename_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.name = kw['tag']
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    def add_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag(name=kw['tag'], blogID=blog.id)
        blog.addTag(tag)
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    def delete_post(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        post = Post.get(kw['pid'])
        post.deleteMe()
        hub.commit()
        tg.redirect('/blog_admin/manage_posts?bid='+kw['bid'])

    @expose()
    def delete_file(self, bid, file_id):
        '''
        delete the desired file
        '''
        self.kick({'bid': bid})
        blog = Blog.get(bid)

        try:
            blog.delete_file(file_id)
        except FileNotFoundError, args:
            tg.flash(args)

        tg.redirect('/blog_admin/manage_files?bid=%s' % bid)

    @expose()
    def delete_comment(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        c = Comment.get(kw['cid'])
        c.destroySelf()
        hub.commit()
        tg.redirect('/blog_admin/manage_comments?bid='+kw['bid'])

    @expose()
    def delete_comments(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        for cid in kw['delete_comments[]']:
            c = Comment.get(cid)
            c.destroySelf()
        hub.commit()
        tg.redirect('/blog_admin/manage_comments?mass=1;bid='+kw['bid'])

    @expose()
    def delete_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin()
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.deleteMe()
        hub.commit()
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    @validate(writepost_form)
    def save_post(self, bid=None, post_id=None, post_title=None, content=None,
            publication_state=False, trackback_url=None):

        self.kick({'bid':bid})

        u = validators.URL(add_http=False, check_exists=False)
        if trackback_url is None:
            trackback_url = ''

        for tburl in trackback_url.split(' '):
            if tburl:
                print u.to_python(tburl)

        user = identity.current.user
        blog = Blog.get(bid)

        # was it an edition or a new post ?
        edit = post_id is not None

        hub.begin()

        if edit:
            p = Post.get(post_id)
            p.title = post_title
            p.content = content
            p.published = publication_state
            p.trackback_urls = trackback_url

        else:
            p = Post(title = post_title,
                    content = content,
                    author = user,
                    published = publication_state,
                    blog = blog,
                    trackback_urls = trackback_url
                    )

        hub.commit()

        if p.published:
            p.send_trackbacks()

        tg.redirect('/blog_admin/manage?bid=%d' % blog.id)
 
    @expose(html="turboblog.templates.blog_admin.dash")
    def dash(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.manage_files")
    def manage_files(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        return dict(files=blog.get_files(), bid=bid, blog=blog)

    @expose(html="turboblog.templates.blog_admin.manage_tags")
    def manage_tags(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.manage_comments")
    def manage_comments(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])

        if 's' in kw.keys():
            # a search is going on
            blog_comments = blog.search_comments(kw['s'])
        else:
            blog_comments = blog.get_comments()

        mass = False
        if 'mode' in kw:
            mass = kw['mode'] == 'mass'

        return dict(blog=blog, mass=mass, blog_comments=blog_comments)

    @expose(html="turboblog.templates.blog_admin.manage_posts")
    def manage_posts(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.settings_general")
    def settings_general(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.settings_comments")
    def settings_comments(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.settings_reading")
    def settings_reading(self, *args, **kw):
        self.kick(kw)
        blog = Blog.get(kw['bid'])
        return dict(blog=blog)

    @expose(html="turboblog.templates.blog_admin.write")
    def write(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        post = None
        if 'pid' in kw:
            try:
                post = Post.get(kw['pid'])
            except SQLObjectNotFound:
                # not found so just let go
                tg.flash(_('Invalid post id given...'))

        if post:
            params = dict(
                values = dict(
                    bid=bid,
                    post_id=post.id,
                    post_title=post.title,
                    content=post.content,
                    publication_state=post.published,
                    disabled_fields = [],
                    ),
                options = dict())

        else:
            params = dict(
                    values = dict(bid=bid)
                    )

        return dict(writepost_form=writepost_form, params=params, blog=blog)

    @expose()
    def manage(self, *args, **kw):
        return self.manage_posts(*args, **kw)

    @expose()
    def index(self, *args, **kw):
        return self.dash(*args, **kw)

    @expose()
    def settings(self, *args, **kw):
        return self.settings_general(*args, **kw)

    @expose()
    def update_general_settings(self, bid, blogname, blogdescription,
            admin, theme, submit):
        self.kick({'bid': bid})
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
        self.kick({'bid': bid})
        tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        tg.redirect(tg.url('/blog_admin/settings?bid=%s' % bid))

    @expose()
    def update_comments_settings(self, *args, **kw):
        bid = kw['bid']
        self.kick({'bid': bid})
        tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        tg.redirect(tg.url('/blog_admin/settings?bid=%s' % bid))

    @expose(html='.templates.blog_admin.upload_file')
    def add_file(self, bid):
        '''
        Page to add file to a blog
        '''
        self.kick({'bid': bid})
        blog = Blog.get(bid)

        # the parameters for this widget
        params = dict( 
            values = dict(bid=bid),
            options = dict())

        return dict(bid=bid, blog=blog,
                file_upload_form=file_upload_form, params=params)

    @expose()
    @validate(validators={
        'file_obj': validators.FieldStorageUploadConverter()})
    def upload_file(self, bid, file_obj):
        '''
        the controller that handles image uploads.

        @param bid: the blog id the image belongs to
        @type bid: integer

        @param file_obj: the image object from the form post
        @type file_obj: a cherrypy file object

        returns: the id of the new file we just stored in the database
        '''
        self.kick({'bid': bid})
        hub.begin()

        file_data = file_obj.file.read()

        newfile = StoredFile(
            filename = file_obj.filename,
            filesize = len(file_data),
            blog = Blog.get(bid),
            mimetype = file_obj.type,
            data = file_data)

        hub.commit()

        tg.redirect('/blog_admin/manage_files?bid=%s' % bid) 

# vim: expandtab tabstop=4 shiftwidth=4:
