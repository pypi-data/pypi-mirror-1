import turbogears, cherrypy, re, antispam, random, threading, formencode, os
from turbogears import controllers, identity, redirect
from model import *
from turbogears import validators, expose
from cherrypy import request, response
from turbojson.jsonify import jsonify
from pager import pager
from sqlobject.sqlbuilder import AND
from turbogears import validators
from admincontrol import *
from rpccontroller import RPCController

# new imports added during 1.0.1 port
import turbogears as tg
from turbogears.controllers import Controller, RootController
from turbogears import feed
from turboblog.model import AntiSpam, StoredFile, FileNotFoundError

settings = Settings.get(1)

def _theme(blog, tpl):
    def_tpl = tpl % 'default'
    cur_tpl = tpl % blog.theme
    # TODO: Fix this with real code this won't work as expected when using
    # egg deployment
    cp = os.curdir + "/%s.kid" % "/".join(cur_tpl.split('.'))
    ret = [def_tpl, cur_tpl][int(os.path.exists(cp))]
    return ret

def _theme_css(blog):
    url = tg.url("/static/css/%s/style.css" % blog.theme)
    def_url = tg.url("/static/css/style.css")
    # TODO: Fix this with real code this won't work as expected when using
    # egg deployment
    cp = os.curdir + "/turboblog"
    ret = [def_url,url][int(os.path.exists(cp+url))]
    return ret

class FeedController(feed.FeedController):
    def __init__(self, blog_id, default):
        feed.FeedController.__init__(self, default=default)
        self.blog_id = blog_id

    def get_feed_data(self):
        blog = Blog.get(self.blog_id)
        return blog.feed(cherrypy.request.base)

class CommentController(Controller):
    @expose()
    @identity.require(identity.has_permission('can_comment'))
    def add(self, postslug, **kwargs):
        bid = Blog.bySlug(kwargs['blogslug']).id #pylint: disable-msg=E1101
        p = Post.bySlug(postslug) #pylint: disable-msg=E1101
        cparent_id = int(kwargs.get('comment_id','-1'))
        cparent = None

        if cparent_id != -1:
            cparent = Comment.get(cparent_id)

        content = kwargs['comment']
        if Comment.check_tags(content): 
            hub.begin() #pylint: disable-msg=E1101
            c = Comment(content=content, author=identity.current.user,
                    approved=False, post=p, parent_id=cparent_id)

            if cparent:
                cparent.addComment(c)

            hub.commit() #pylint: disable-msg=E1101
            tg.redirect(p.link() + "#comment_%d" % c.id)

        else:
            flashData = {"status": "error",
                    "msg": "Tags are not allowed in comments!"}
            turbogears.flash(flashData)

        tg.redirect(p.link(bid))

    @expose()
    @turbogears.validate(validators={"cid":validators.Int()})
    @identity.require(identity.has_permission('can_moderate'))
    def approve(self, cid, blogslug):
        hub.begin() #pylint: disable-msg=E1101
        c = Comment.get(cid)
        c.approved = True
        turbogears.flash('Comment approved!')
        hub.commit() #pylint: disable-msg=E1101
        return dict()

    @expose()
    @turbogears.validate(validators={"cid":validators.Int()})
    @identity.require(identity.has_permission('can_comment'))
    def source(self, cid, blogslug):
        c = Comment.get(cid)
        return dict(content = c.content)

    @expose()
    @identity.require(identity.has_permission('can_comment'))
    @turbogears.validate(validators={"cid":validators.Int()})
    def edit(self, cid, **kwargs):
        content = kwargs['content']
        if Comment.check_tags(content):
            hub.begin() #pylint: disable-msg=E1101
            Comment.get(cid).content = content
            hub.commit() #pylint: disable-msg=E1101
        else:
            flashData = {"status": "error",
                    "msg": "Tags in the comment are not allowed!"}
            turbogears.flash(jsonify(flashData))
        return dict()

class BlogController(Controller):
    comment = CommentController()

    @expose(format="xml", content_type="application/atom+xml")
    def feed(self, *args, **kwargs):
        try:
            format = args[0]
        except:
            format = 'atom1_0'

        myfeed = FeedController(
                Blog.bySlug(kwargs['blogslug']).id, #pylint: disable-msg=E1101
                default = format)

        return getattr(myfeed, format)()

    @expose()
    @turbogears.validate(validators={"pid":validators.Int()})
    def tag_post(self, tagname, pid, blogslug):
        p = Post.get(pid)
        blog = Blog.bySlug(blogslug) #pylint: disable-msg=E1101
        t = Tag.select(AND(
            Tag.q.blogID == blog.id, #pylint: disable-msg=E1101
            Tag.q.name == tagname))[0] #pylint: disable-msg=E1101

        hub.begin() #pylint: disable-msg=E1101
        p.addTag(t) #pylint: disable-msg=E1101
        hub.commit() #pylint: disable-msg=E1101
        return dict()

    @expose()
    @turbogears.validate(validators={"pid": validators.Int()})
    def trackback(self, pid, blogslug, url,  *args, **kw):
        title = kw.get('title', '')
        excerpt = kw.get('excerpt', '')
        blog_name = kw.get('blog_name', '')
        hub.begin() #pylint: disable-msg=E1101
        p = Post.get(pid)
        Trackback(url=url, title=title, excerpt=excerpt, 
                blog_name=blog_name, post=p)

        hub.commit() #pylint: disable-msg=E1101
        return """<?xml version="1.0" encoding="utf-8"?>
                    <response>
                        <error>0</error>
                    </response>"""

    @expose(html="turboblog.templates.selector")
    def selector(self, *args, **kwargs):
        return dict(
                blogs = Blog.select(),
                tg_template = "turboblog.templates.default.selector")

    @expose(html="turboblog.templates.post")
    def post(self, blogslug, slug, *args, **kwargs):
        try:
            post = Post.bySlug(slug) #pylint: disable-msg=E1101
            blog = Blog.bySlug(blogslug) #pylint: disable-msg=E1101
        except Exception, e:
            #print "-00---",e
            raise cherrypy.NotFound
        cloud = 0
        if 'cloud' in kwargs:
            cloud = kwargs['cloud']
 
        return dict(
                blog=blog,
                post=post,
                cloud=cloud,
                tg_template=_theme(blog,"turboblog.templates.%s.post"))

    @expose(html="turboblog.templates.index")
    @pager('blog_posts', default_size=5)
    def index(self, slug, *args, **kwargs):
        try:
            blog = Blog.bySlug(slug) #pylint: disable-msg=E1101

        except Exception, e:
            #print "---",e
            raise cherrypy.NotFound

        blog_posts = blog.get_posts(publication_state="published")

        ret =  dict(
                blog=blog,
                blog_posts=blog_posts,
                tg_template=_theme(blog, "turboblog.templates.%s.index"))

        if 'cloud' in kwargs:
            ret.update({"cloud":kwargs['cloud']})

        if 'untagged' in kwargs:
            ret.update({"untagged":1})

        if 'tagged' in kwargs:
            tagname = Tag.select(
                    AND(
                        Tag.q.blogID==blog.id, #pylint: disable-msg=E1101
                        Tag.q.id==kwargs['tagged']))[0] #pylint: disable-msg=E1101

            ret.update({"tag_name": tagname})

        if ('arc_year' in kwargs) and ('arc_month' in kwargs):
            ret.update(
                    {'arc_month': int(kwargs['arc_month']),
                     'arc_year': int(kwargs['arc_year'])
                    })
        return ret 

class UserController(Controller):
    @expose(html="turboblog.templates.user")
    def show(self, user_name):
        user = User.by_user_name(user_name) #pylint: disable-msg=E1101
        return dict(
                user = user,
                tg_template = "turboblog.templates.default.user")

    @expose(content_type='image/jpg')
    def avatar(self, user_name):
        avatar = User.by_user_name(user_name).avatar #pylint: disable-msg=E1101
        return avatar
 
class Root(RootController):
    admin = AdminController()
    blog_admin = BlogAdminController()
    blog = BlogController()
    user = UserController()
    RPC = RPCController()

    @expose(content_type='image/png')
    def get_antispam_image(self):
        cv = turbogears.visit.current()

        # protect our resource against other servers theft
        if cv.is_new:
            tg.redirect(tg.url('/unauthorized_use'))

        cvk = cv.key
        rannum = str(random.randrange(1,99999,1))
        hub.begin() #pylint: disable-msg=E1101
        # just to make sure

        try:
            # I hate SQLObject!!! forcing me to catch exceptions
            # this is no exception this is a simple SQL Request
            # where I am not sure if something will come back
            # Stupid SO. Remind me to switch to SA ASAP
            anti_spam = AntiSpam.by_visit_key(cvk) #pylint: disable-msg=E1101
            anti_spam.destroySelf()

        except SQLObjectNotFound, args:
            # Hey nothing to see here it is just because SO forces use to
            # use exceptions that we do so
            pass

        # store our string for easy retrieval
        anti_spam = AntiSpam(visit_key=cvk, verif_string=rannum) 
        hub.commit() #pylint: disable-msg=E1101

        return antispam.write_image(rannum)

    @expose()
    def index(self, *args, **kwargs):
        if settings.default_blog != -1:
            return self.blog.index(Blog.get(settings.default_blog).slug)
        return self.blog.selector()

    @expose()
    def default(self, *args, **kwargs):
        #print "def with:",args,kwargs
        if not args: self.index(*args,**kwargs)
        blogslug = args[0]
        if len(args)>1: #have more params
            mname = args[1]
            method = getattr(self, mname, None) # try root first
            if method:
                return method(*args[1:], **kwargs)
            method = getattr(self.blog, mname, None)
            if method:
                kwargs.update({'blogslug':blogslug})
                if callable(method):
                    return method(*args[2:], **kwargs)
                else:
                    sm = getattr(method, args[2])
                    sa = args[3:]
                    return sm(*sa, **kwargs)
            else:
                c = getattr(self, args[0], None)
                if c:
                    method = getattr(c, args[1], None)
                    if method:
                        return method(args[1:])
                sa = args[2:]
                return self.blog.post(blogslug, mname, *sa, **kwargs)
        else:
            method = getattr(self, args[0], None)
            if method:
                return method.default()
            return self.blog.index(blogslug, **kwargs)

    #@turbogears.expose(html="turboblog.templates.login")
    #def login( self, *args, **kw ):
    #    if hasattr(cherrypy.request,"identity_exception"):
    #        msg= str(cherrypy.request.identity_exception)
    #        userId= getattr( cherrypy.request.identity_exception,
    #                "userId", None )
    #    else:
    #        msg= "Please log in"
    #        userId= None
    #        cherrypy.response.status=403
    #    return dict( message=msg, previous_url=kw.get('redirect_to','/'),
    #                 userId=userId )

    @expose(html="turboblog.templates.signup")
    def signup(self, *args, **kw):
        return dict()

    @expose()
    def create_user(self, *args, **kw):
        flash = None

        # grab the verif string and remove the
        # entry from database
        cv = turbogears.visit.current()
        try:
            anti_spam = AntiSpam.by_visit_key(cv.key) #pylint: disable-msg=E1101
        except SQLObjectNotFound, args:
            tg.flash(_('Session not set, please activate cookies'))
            tg.redirect(tg.url('/signup'))

        verif_string = anti_spam.verif_string

        # remove the key since it is a one usage basis
        hub.begin() #pylint: disable-msg=E1101
        anti_spam.destroySelf()
        hub.commit() #pylint: disable-msg=E1101

        try:
            validators.FieldsMatch('psw', 'psw2').to_python(kw)
            assert (kw['code'] == verif_string)

        except formencode.api.Invalid, e:
            flash = 'Password don\'t match'

        except Exception, e:
            flash = 'Code was incorrect'

        if flash:
            turbogears.flash(flash)
            raise cherrypy.HTTPRedirect("/signup")

        hub.begin() #pylint: disable-msg=E1101
        try:
            avatar = kw['image'].file.read()

        except:
            avatar = None
            if ('usegravatar' in kw) and (kw['usegravatar']=='on'):
                import gravatar
                (mime,avatar) = gravatar.get_image(kw['email'])

        try:
            u = User.by_email_address(kw['email']) #pylint: disable-msg=E1101
            tg.flash(_('Email already registered, Sorry'))
            tg.redirect(tg.url('/signup'))

        except SQLObjectNotFound, args:
            # stupid SQLObject using excpetions for this!!!
            pass

        u = User(
                user_name=kw['userid'],
                password=kw['psw'],
                display_name=kw['fullname'],
                email_address=kw['email'],
                avatar=avatar,
                about=kw.get('summary',''))

        g = Group.by_group_name('user') #pylint: disable-msg=E1101
        u.addGroup(g) #pylint: disable-msg=E1101
        hub.commit() #pylint: disable-msg=E1101
        turbogears.flash('Please login with your details.')
        raise cherrypy.HTTPRedirect ("/login")

    #@expose(template=".templates.livesearch", fragment=True)
    @expose(template=".templates.index")
    @pager('blog_posts', default_size=5)
    def livesearch(self, *args, **kw):
        """
        Search for the given search term. This is in a separate method because
        the intent is to make this method handle queries and return fragments so
        that the site can query with Ajax on this and update the content without
        reloading the browser page
        """
        if 'bid' in kw.keys():
            bid = kw['bid']
            blog = Blog.get(bid)

        else:
            raise cherrypy.NotFound('You did not specify a blog id')

        if 's' in kw.keys():
            blog_posts = blog.search_posts(kw['s'], publication_state="published")

        else:
            raise cherrypy.NotFound('You did not specify a search string')

        return dict(bid=bid, blog=blog, blog_posts=blog_posts,
                tg_template=_theme(blog, "turboblog.templates.%s.index"))

    #@turbogears.expose()
    #def logout( self, *args, **kw ):
    #    identity.current.logout()
    #    raise cherrypy.InternalRedirect(kw.get('redirect_to','/'))

    @expose(template=".templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")

        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

    @expose()
    def unauthorized_use(self):
        '''
        redirect you resource thefts to this controller to make
        their life a little bit harder
        '''
        msg = _("This resource is private and should be accessed \
                only from our own web site. Sorry :)")

        return msg

    @expose()
    def download_file(self, bid, file_id):
        '''
        @param bid: blog id
        @type bid: integer

        @param file_id: a file id
        @type file_id: integer

        returns the file content
        '''
        try:
            myfile = StoredFile.get_file(bid, file_id)
        except FileNotFoundError, args:
            tg.flash(args)

        cherrypy.response.headerMap["Content-Type"] = "application/x-download"
        disposition = "attachment; filename=%s" % (myfile.filename)
        cherrypy.response.headerMap["Content-Disposition"] = disposition
        return myfile.data

    @expose()
    def show_file(self, bid, file_id):
        '''
        displays a file from the database

        @param bid: the blog id the image belongs to
        @type bid: integer

        @param file_id: the id of the file to get
        @type file_id: integer
        '''
        try:
            myfile = StoredFile.get_file(bid, file_id)
        except FileNotFoundError, args:
            tg.flash(args)
            return None

        cherrypy.response.headerMap["Content-Type"] = myfile.mimetype
        return myfile.data

# vim: expandtab tabstop=4 shiftwidth=4:
