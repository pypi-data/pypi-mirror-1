'''
this module is in charge of the administation part of our
application. It is the reserved interface that only authorized
users see and interact with
'''
from turbogears import identity
from turboblog.model import Blog, Settings, hub, Post, Comment, Tag, \
        User, Group, StoredFile

from turbogears import validators
# new imports added during port to TG 1.0.1
import turbogears as tg
from turbogears import expose
from turbogears.controllers import Controller
from turbogears import validate
from elementtree.ElementTree import Element, SubElement

from turboblog.forms import file_upload_form, writepost_form, \
        search_text_form, search_date_form, edit_comment_form, \
        submod
import cherrypy
from  htmlentitydefs import name2codepoint

SETTINGS = Settings.get(1)

def render_submenu(blog_id, active):
    '''
    renders the submenu for a given blog
    @param blog_id: the id of the blog for which we want to generate a submenu
    @type blog_id: integer

    @param active: the active element name
    @type active: string

    returns: an ElementTree.Element instance containing the desired HTML code
    '''
    subelements = ['posts', 'comments', 'tags', 'files'] 

    submenu = Element('ul', id="submenu")
    for subelement in subelements:
        s = SubElement(submenu, 'li',
                title=_('Manage %s' % subelement.capitalize()))

        a = SubElement(s, 'a',
                href=tg.url('/blog_admin/manage_%s?bid=%s' % (
                    subelement, blog_id)))

        if subelement == active:
            a.set('class', 'current')

        a.text = subelement.capitalize()

    return submenu

def render_adminmenu(blog_id):
    '''
    renders the adminmenu for a given blog

    @param blog_id: the id of the blog for which we want to generate a submenu
    @type blog_id: integer

    returns: an ElementTree.Element instance containing the desired HTML code
    '''
    subelements = [
            {
                'name': 'admin',
                'url': tg.url('/admin'),
                'text': _('Site Dashboard'),
                'popup': _('Lets you manage all the blogs')
                },
            {
                'name': 'dashboard',
                'url': tg.url('/blog_admin?bid=%s' % blog_id),
                'text': _('Blog Dashboard'),
                'popup': _('Lets you manage your blog details')
                },
            {
                'name': 'write',
                'url': tg.url('/blog_admin/write?bid=%s' % blog_id),
                'text': _('Write'),
                'popup': _('Write a new post for your blog')
                },
            {
                'name': 'manage',
                'url': tg.url('/blog_admin/manage?bid=%s' % blog_id),
                'text': _('Manage'),
                'popup': _('Manage posts, comments, tags and files')
                },
            {
                'name': 'settings',
                'url': tg.url('/blog_admin/settings?bid=%s' % blog_id),
                'text': _('Settings'),
                'popup': _('Change the blog settings such as name and tagline')
                }
            ]

    adminmenu = Element('ul', id="adminmenu")
    for subelement in subelements:
        s = SubElement(adminmenu, 'li', title=subelement['popup'])
        a = SubElement(s, 'a', href=subelement['url'])
        a.text = subelement['text']

    return adminmenu

class AdminController(Controller, identity.SecureResource):
    require = identity.has_permission('can_admin')

    @expose()
    def delete_blog(self, *args, **kw):
        if SETTINGS.default_blog == int(kw['bid']):
            tg.flash(_('Cannot delete default blog!'))
        else:
            hub.begin() #pylint: disable-msg=E1101
            Blog.delete(kw['bid'])
            hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/admin/blogs')

    @expose()
    def user_create(self, *args, **kw):
        groups = kw['groups'].split(',')
        validators.FieldsMatch('psw', 'psw2').to_python(kw)
        hub.begin() #pylint: disable-msg=E1101
        u = User(user_name=kw['login'], display_name=kw['fullname'],
                password=kw['psw'], email_address=kw['email'],
                avatar=None, about='')

        for g in groups:
            #print 'adding: ', g
            u.addGroup(Group.by_group_name(g)) #pylint: disable-msg=E1101

        hub.commit() #pylint: disable-msg=E1101
        return dict(user_name=u.user_name, display_name=kw['fullname'])

    @expose()
    def user_delete(self, *args, **kw):
        hub.begin() #pylint: disable-msg=E1101
        User.delete(kw['uid'])
        hub.commit() #pylint: disable-msg=E1101
        return dict()

    @expose()
    def user_update(self, *args, **kw):
        groups = kw['groups'].split(',')
        validators.FieldsMatch('psw', 'psw2').to_python(kw)
        hub.begin() #pylint: disable-msg=E1101
        u = User.get(kw['uid'])
        u.emailAddress = emailAddress = kw['email']
        u.display_name = kw['fullname']
        u.password = kw['psw']
        for g in u.groups[:]:
            u.removeGroup(g) #pylint: disable-msg=E1103
        for g in groups:
            u.addGroup(Group.by_group_name(g)) #pylint: disable-msg=E1103
        hub.commit() #pylint: disable-msg=E1101
        return dict(user_name = u.user_name, display_name = kw['fullname'])


    @expose()
    def create_blog(self, *args, **kw):
        bn = kw['name']
        bt = kw['tagline']
        bo = User.get(kw['owner'])
        hub.begin() #pylint: disable-msg=E1101
        Blog(name=bn, tagline=bt, owner=bo)
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/admin/blogs')

    @expose(html="turboblog.templates.admin.blogs")
    def blogs(self):
        return dict(defblog=SETTINGS.default_blog,
                curadmin=SETTINGS.admin)

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
        hub.begin() #pylint: disable-msg=E1101
        SETTINGS.admin = User.get(kwargs['aid'])
        hub.commit() #pylint: disable-msg=E1101
        return dict()
 
    @expose()
    def set_default(self, **kwargs):
        hub.begin() #pylint: disable-msg=E1101
        SETTINGS.default_blog = int(kwargs['defblog'])
        hub.commit() #pylint: disable-msg=E1101
        return dict()
 
class BlogAdminController(Controller, identity.SecureResource):
    require = identity.has_permission('can_admin_blog')

    def kick(self, kw):
        blog = Blog.get(kw['bid'])
        if not identity.current.user == blog.owner \
                and not identity.current.user == SETTINGS.admin:
            raise identity.IdentityFailure(_("You are not this blog's owner!"))

    @expose()
    def rename_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin() #pylint: disable-msg=E1101
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.name = kw['tag']
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    def add_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin() #pylint: disable-msg=E1101
        blog = Blog.get(kw['bid'])
        tag = Tag(name=kw['tag'], blogID=blog.id)
        blog.addTag(tag) #pylint: disable-msg=E1101
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    def delete_post(self, *args, **kw):
        self.kick(kw)
        hub.begin() #pylint: disable-msg=E1101
        blog = Blog.get(kw['bid'])
        post = Post.get(kw['pid'])
        post.deleteMe()
        hub.commit() #pylint: disable-msg=E1101
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
        hub.begin() #pylint: disable-msg=E1101
        c = Comment.get(kw['cid'])
        c.destroySelf()
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/blog_admin/manage_comments?bid='+kw['bid'])

    @expose()
    def delete_comments(self, *args, **kw):
        self.kick(kw)
        hub.begin() #pylint: disable-msg=E1101
        for cid in kw['delete_comments[]']:
            c = Comment.get(cid)
            c.destroySelf()
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/blog_admin/manage_comments?mass=1;bid='+kw['bid'])

    @expose()
    def delete_tag(self, *args, **kw):
        self.kick(kw)
        hub.begin() #pylint: disable-msg=E1101
        blog = Blog.get(kw['bid'])
        tag = Tag.get(kw['tid'])
        tag.deleteMe()
        hub.commit() #pylint: disable-msg=E1101
        tg.redirect('/blog_admin/manage_tags?bid='+kw['bid'])

    @expose()
    @validate(writepost_form)
    def save_post(self, bid=None, post_id=None, post_title=None, content=None,
            publication_state=False, trackback_url=None):

        self.kick({'bid':bid})

        u = validators.URL(add_http=False, check_exists=False)
        if trackback_url is None:
            trackback_url = ''

        #for tburl in trackback_url.split(' '):
        #    if tburl:
        #        #print u.to_python(tburl)
        #        pass

        user = identity.current.user
        blog = Blog.get(bid)

        # was it an edition or a new post ?
        edit = post_id is not None

        # clear up TinyMCE html to obtain a clean Unicode
        # string
        for entity in name2codepoint.keys():
            if entity in content:
                content = content.replace(
                    "&%s;" % entity,
                    unichr(name2codepoint[entity])
                    )

        hub.begin() #pylint: disable-msg=E1101

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

        hub.commit() #pylint: disable-msg=E1101

        if p.published:
            p.send_trackbacks()

        tg.redirect('/blog_admin/manage?bid=%d' % blog.id)
 
    @expose(html="turboblog.templates.blog_admin.dash")
    def dash(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        adminmenu = render_adminmenu(bid)
        return dict(blog=blog, adminmenu=adminmenu)

    @expose(html="turboblog.templates.blog_admin.manage_files")
    def manage_files(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        submenu = render_submenu(bid, 'files')
        adminmenu = render_adminmenu(bid)

        return dict(files=blog.get_files(), bid=bid, blog=blog,
                submenu=submenu, adminmenu=adminmenu)

    @expose(html="turboblog.templates.blog_admin.manage_tags")
    def manage_tags(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)

        submenu = render_submenu(bid, 'tags')
        adminmenu = render_adminmenu(bid)
        return dict(blog=blog, submenu=submenu, adminmenu=adminmenu)

    @expose(html="turboblog.templates.blog_admin.manage_comments")
    def manage_comments(self, *args, **kw):
        '''
        this method exposes the main management page for comments.
        it handles the text/date searches as well as plain comment
        displays
        '''
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        submenu = render_submenu(bid, 'comments')
        adminmenu = render_adminmenu(bid)

        search_text = search_text_form
        search_date = search_date_form

        if 's' in kw.keys():
            # a search is going on
            blog_comments = blog.search_comments(kw['s'])

        elif 'sd' in kw.keys():
            # a date search is going on
            date_convert = validators.DateTimeConverter()
            start_date  = date_convert.to_python(kw['sd'])

            try:
                end_date = date_convert.to_python(kw['ed'])
            except KeyError:
                tg.flash(_('End date not specified in search'))
                tg.redirect('/blog_admin/manage_comments?bid=%s' % bid)

            #print "type: %s, value: %s" % (type(start_date), start_date)
            blog_comments = blog.search_comments_bydate(
                    start_date,
                    end_date)

        else:
            # no search is going on, just plain normal view
            blog_comments = blog.get_comments()

        # TODO: review this small snippet
        # I put it here because I wanted to move it out of the kid template
        # but I am not happy with this implementation
        mass = False
        if 'mode' in kw:
            mass = kw['mode'] == 'mass'
            try:
                mass = int(mass)
            except:
                mass = 0

        # parameters for search_date widget
        sd_params = dict(
                values=dict(
                    bid = bid,
                    calendar_lang = 'en'
                    ),
                options=dict(),
                form_opts=dict(
                    action = tg.url('/blog_admin/manage_comments?bid=%s' % bid),
                    submit_text = _('Search')
                    ),
                )

        # parameters for search_text widget
        st_params = dict(
                values=dict(
                    bid = bid,
                    ),
                options=dict(),
                form_opts=dict(
                    action = tg.url('/blog_admin/manage_comments?bid=%s' % bid),
                    submit_text = _('Search')
                    ),
                )           

        return dict(blog=blog, mass=mass,
                blog_comments=blog_comments, submenu=submenu,
                adminmenu=adminmenu, submod=submod,
                search_text=search_text, search_date=search_date,
                sd_params=sd_params, st_params=st_params)

    @expose(html="turboblog.templates.blog_admin.edit_comment")
    def edit_comment(self, bid, cid):
        '''
        edit a comment. This is called by the submodal window
        from the manage_comments method
        '''
        self.kick({'bid': bid})

        blog = Blog.get(bid)

        try:
            comment = Comment.get(cid)
        except SQLObjectNotFound:
            raise cherrypy.NotFound('invalid comment id %s' % cid) 

        params = dict(
                values=dict(
                    bid = bid,
                    cid = comment.id,
                    comment_content = comment.content,
                    ),
                options=dict(),
                form_opts=dict(
                    action = tg.url('/blog_admin/save_comment'),
                    submit_text = _('Save'),
                    form_attrs = dict(),
                    )
                )

        comment_form = edit_comment_form

        return dict(blog=blog, cid=comment.id, form=comment_form, params=params)

    @expose()
    def save_comment(self, bid, cid, comment_content):
        '''
        save a comment from the edit_comment method ONLY
        This is only to be used by a submodal caller since it sends javascript
        code back to the caller to close the submodal window when the database
        insert is finished correctly
        '''
        self.kick({'bid': bid})
        hub.begin() #pylint: disable-msg=E1101
        try:
            comment = Comment.get(cid)
        except SQLObjectNotFound:
            # gracefully handle the error if any
            payload = '<html><body>%s</body></html>' % (
                    _('The comment does not exist'))
            return payload

        comment.content = comment_content
        hub.commit() #pylint: disable-msg=E1101

        html_payload = '<html><body \
                onload="javascript:window.top.hidePopWin(true);">'
        html_payload += 'Comment value saved</body></html>'
        return html_payload

    @expose("json")
    def comment_value(self, cid):
        '''
        returns the comment value for the specified cid
        '''
        comment = Comment.get(cid)
        return dict(
                comment_id=cid,
                comment_content=comment.content
                )

    @expose(html="turboblog.templates.blog_admin.manage_posts")
    #@validate(search_date_form)
    def manage_posts(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        submenu = render_submenu(bid, 'posts')
        adminmenu = render_adminmenu(bid)
        search_text = search_text_form
        search_date = search_date_form

        if 's' in kw.keys():
            # a text search is going on
            blog_posts = blog.search_posts(kw['s'])

        elif 'sd' in kw.keys():
            # a month search is going on
            date_convert = validators.DateTimeConverter()
            start_date  = date_convert.to_python(kw['sd'])

            try:
                end_date = date_convert.to_python(kw['ed'])
            except KeyError:
                tg.flash(_('End date not specified in search'))
                tg.redirect('/blog_admin/manage_posts?bid=%s' % bid)

            #print "type: %s, value: %s" % (type(start_date), start_date)
            blog_posts = blog.search_posts_bydate(
                    start_date,
                    end_date)

        else:
            blog_posts = blog.get_posts()

        sd_params = dict(
                values=dict(
                    bid = bid,
                    #action = tg.url('/blog_admin/manage_posts?bid=%s' % bid),
                    calendar_lang = 'en'
                    ),
                options=dict(),
                form_opts=dict(
                    action = tg.url('/blog_admin/manage_posts?bid=%s' % bid),
                    submit_text = _('Search')
                    ),
                )

        st_params = dict(
                values=dict(
                    bid = bid,
                    #action = tg.url('/blog_admin/manage_posts?bid=%s' % bid)
                    ),
                options=dict(),
                form_opts=dict(
                    action = tg.url('/blog_admin/manage_posts?bid=%s' % bid),
                    submit_text = _('Search')
                    ),
                )

        return dict(blog=blog, blog_posts=blog_posts,
                submenu=submenu, adminmenu=adminmenu,
                search_text=search_text,
                search_date=search_date, st_params=st_params,
                sd_params=sd_params)

    @expose(html="turboblog.templates.blog_admin.settings_general")
    def settings_general(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        adminmenu = render_adminmenu(bid)
        return dict(blog=blog, adminmenu=adminmenu)

    @expose(html="turboblog.templates.blog_admin.settings_comments")
    def settings_comments(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        adminmenu = render_adminmenu(bid)
        return dict(blog=blog, adminmenu=adminmenu)

    @expose(html="turboblog.templates.blog_admin.settings_reading")
    def settings_reading(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        read_settings = blog.get_read_settings()
        posts_per_page = read_settings.postsperpage
        posts_per_rss = read_settings.postsperrss
        rss_type = read_settings.rsstype
        if rss_type == "summary":
            rss_summary = True
        else:
            rss_summary = False

        adminmenu = render_adminmenu(bid)
        return dict(blog=blog, adminmenu=adminmenu,
                 posts_per_page=posts_per_page, posts_per_rss=posts_per_rss,
                 rss_summary=rss_summary)

    @expose(html="turboblog.templates.blog_admin.write")
    def write(self, *args, **kw):
        self.kick(kw)
        bid = kw['bid']
        blog = Blog.get(bid)
        adminmenu = render_adminmenu(bid)
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

        return dict(writepost_form=writepost_form, params=params, blog=blog,
                adminmenu=adminmenu)

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
        '''
        Exposed method that handles forms from the settings management
        for the general TAB
        '''
        self.kick({'bid': bid})
        hub.begin() #pylint: disable-msg=E1101
        blog = Blog.get(bid)

        if not blogname == blog.name:
            blog.name = blogname

        blog.tagline = blogdescription
        blog.ownerID = admin
        blog.theme = theme
        hub.commit() #pylint: disable-msg=E1101
        tg.flash({'status': "success",
            'msg': _('Settings saved successfully')})
        tg.redirect(tg.url('/blog_admin/settings_general?bid=%s' % bid))

    # TODO: remove the Submit by reworking the template into some
    # widget aware version
    @expose()
    def update_read_settings(self, bid, posts_per_page, posts_per_rss,
            rss_use_excerpt, Submit):
        '''
        Exposed method that handles forms from the settings management
        for the read TAB
        '''
        self.kick({'bid': bid})

        blog = Blog.get(bid)

        read_settings = blog.get_read_settings()
        hub.begin() #pylint: disable-msg=E1101
        read_settings.postsperpage = int(posts_per_page)
        read_settings.postsperrss = int(posts_per_rss)

        if int(rss_use_excerpt) == 1:
            read_settings.rsstype = 'summary'
        else:
            read_settings.rsstype = 'fulltext'

        hub.commit() #pylint: disable-msg=E1101
        hub.end() #pylint: disable-msg=E1101

        #tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        
        tg.redirect(tg.url('/blog_admin/settings_reading?bid=%s' % bid))

    @expose()
    def update_comments_settings(self, *args, **kw):
        '''
        Exposed method that handles forms from the settings management
        for the comments TAB
        '''
        bid = kw['bid']
        self.kick({'bid': bid})
        tg.flash({'status': "error", 'msg': _('Not implemented yet')})
        tg.redirect(tg.url('/blog_admin/settings_comments?bid=%s' % bid))

    @expose(html='.templates.blog_admin.upload_file')
    def add_file(self, bid):
        '''
        Page to add file to a blog
        '''
        self.kick({'bid': bid})
        blog = Blog.get(bid)
        submenu = render_submenu(bid, 'files')
        adminmenu = render_adminmenu(bid)

        # the parameters for this widget
        params = dict( 
            values = dict(bid=bid),
            options = dict())

        return dict(bid=bid, blog=blog, adminmenu=adminmenu,
                submenu=submenu,
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
        hub.begin() #pylint: disable-msg=E1101

        file_data = file_obj.file.read()

        newfile = StoredFile(
            filename = file_obj.filename,
            filesize = len(file_data),
            blog = Blog.get(bid),
            mimetype = file_obj.type,
            data = file_data)

        hub.commit() #pylint: disable-msg=E1101

        tg.redirect('/blog_admin/manage_files?bid=%s' % bid) 

# vim: expandtab tabstop=4 shiftwidth=4:
