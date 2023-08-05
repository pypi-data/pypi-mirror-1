import turbogears, cherrypy, re, antispam, random
import threading, formencode, xmlrpclib
from turbogears import controllers, feed, identity
from model import *
from turbogears import validators
from turbojson.jsonify import jsonify
from pager import pager
from sqlobject.sqlbuilder import AND
from turbogears import validators

settings = Settings.get(1)

class BloggerController(controllers.RootController):

    @turbogears.expose()
    def newPost(self, appkey, blogid, username, password,
            content, publish, title=""):
        user = User.by_user_name(username)
        blog = Blog.get(blogid)
        assert(user.password == password)
        assert(blog.owner == user or user in blog.posters)
        hub.begin()
        p = Post(title=title, content=content, publish=publish,
                blog=blog, author=user)

        hub.commit()
        return str(p.id)
        
    @turbogears.expose()
    def editPost(self, appkey, postid, username, password,
            content, publish, title=""):
        user = User.by_user_name(username)
        p = Post.get(postid)
        assert(user.password == password)
        assert(p.blog.owner == user or user in p.blog.posters)
        hub.begin()
        p.title = title
        p.content = content
        p.publish = publish
        hub.commit()
        return True
    
    @turbogears.expose()
    def deletePost(self, appkey, postid, username,  password, publish):
        p = Post.get(postid)
        user = User.by_user_name(username)
        assert(user.password == password)
        assert(p.blog.owner == user or user in p.blog.posters)
        hub.begin()
        p.deleteMe()
        hub.commit()
        return True

    @turbogears.expose()
    def getRecentPosts(self, appkey, blogid, username, password,
            numberOfPosts):
        user = User.by_user_name(username)
        assert(user.password == password)
        blog = Blog.get(blogid)
        assert ( blog.owner == user or user in blog.posters )
        ret = []
        for p in blog.get_posts()[:numberOfPosts]:
            ret += [ {'dateCreated': str(p.creation_time),
                'userid': str(p.author.id), 'postid': str(p.id),
                'content': p.content, 'link': p.link()} ]
        return ret

    @turbogears.expose()
    def getUsersBlogs(self,appkey, username, password):
        user = User.by_user_name(username)
        assert(user.password == password)
        ret = []
        for b in user.blogs:
            ret += [ {'url':b.link(), 'blogid':str(b.id), 'blogName':b.name} ]
        return ret

    @turbogears.expose()
    def getUserInfo(self, appkey, username, password):
        u = User.by_user_name(username)
        assert(u.password == password)
        fl = str(u.display_name).split(' ',2)
        f = fl[0]
        if len(fl)<2: l = ""
        return {'userid': str(u.id), 'firstname': f, 'lastname': l,
                'nickname': u.userId, 'email': u.emailAddress, 'url': u.link()}

class MetaWeblogController(controllers.RootController):
    blogger = BloggerController()
    @turbogears.expose()
    def newPost(self, blogid, username, password, content, publish):
        title = content.get('title',"")
        text =  content.get('description',"")
        dc =  content.get('dateCreated',"")
        allow_comment = content.get('mt_allow_comments',0)
        allow_ping = content.get('mt_allow_pingss',0)
        tb_urls = content.get('mt_tb_ping_urls',[])
        pid = self.blogger.newPost("", blogid, username, 
                password, text, publish, title)
        hub.begin()
        p = Post.get(pid)
        if dc: p.creation_time = dc
        if tb_urls: 
            p.trackback_urls = " ".join(tb_urls)
            p.send_trackbacks()
        hub.commit()
        return pid

    @turbogears.expose()
    def editPost(self, postid, username, password, content, publish):
        title = content.get('title',"")
        text =  content.get('description',"")
        dc =  content.get('dateCreated',"")
        allow_comment = content.get('mt_allow_comments',0)
        allow_ping = content.get('mt_allow_pingss',0)
        tb_urls = content.get('mt_tb_ping_urls',[])
        self.blogger.editPost("", postid, username, password,
                text, publish, title
                )

        hub.begin()
        p = Post.get(postid)
        if dc: p.creation_time = dc
        if tb_urls: 
            p.trackback_urls = " ".join(tb_urls)
            p.send_trackbacks()
        hub.commit()
        return True

    @turbogears.expose()
    def getPost(self, postid, username, password):
        user = User.by_user_name(username)
        p = Post.get(postid)
        assert(user.password == password)
        assert(p.blog.owner == user or user in p.blog.posters)
        return {'userid':str(user.id), 'dateCreated':str(p.creation_time),
                'postid':postid, 'description':p.content, 'title':p.title,
                'link':p.link(), 'permaLink':p.link(), 'mt_excerpt':"",
                'mt_text_more':"", 'mt_allow_comments':0, 'mt_allow_pings':0}

    @turbogears.expose()
    def getRecentPosts(self, blogid, username, password, numberOfPosts):
        rp = self.blogger.getRecentPosts("", blogid,
                username, password, numberOfPosts)

        for r in rp:
            c = r.pop('content')
            r['description'] = c
            p = Post.get(r['postid'])
            r['title'] = p.title
            r.update({'permaLink': p.link(), 'mt_excerpt': "",
                'mt_text_more': "", 'mt_allow_comments': 0,
                'mt_allow_pings':0}
                )
        return rp

    @turbogears.expose()
    def newMediaObject(self, blogid, username, password, file):
        pass

class MTController(controllers.RootController):
    blogger = BloggerController()
    metaWeblog = MetaWeblogController()
        
    @turbogears.expose()
    def getRecentPostTitles(self, blogid, username, password, numberOfPosts):
        rp = self.metaWeblog.getRecentPosts(
                blogid, username, password, numberOfPosts)

        for r in rp:
            for poppy in ['description', 'mt_excerpt', 'mt_text_more',
                    'mt_allow_comments', 'mt_allow_pings',
                    'link', 'permaLink']:
                r.pop(poppy)
        return rp
        
    @turbogears.expose()
    def getCategoryList(self, blogid, username, password):
        user = User.by_user_name(username)
        assert(user.password == password)
        blog = Blog.get(blogid) 
        assert ( blog.owner == user or user in blog.posters )
        ret = []
        for t in blog.tags:
            ret += [ {'categoryId':str(t.id),'categoryName':t.name} ]
        return ret
    
    @turbogears.expose()
    def getPostCategories(self, blogid, username, password):
        p = Post.get(postid)
        user = User.by_user(username)
        assert(user.password == password)
        assert(p.blog.owner == user or user in p.blog.posters)
        ret = []
        for t in p.tags:
            ret += [ {'categoryId': str(t.id), 'categoryName': t.name,
                'isPrimary':0} ]
        return ret
               

    @turbogears.expose()
    def setPostCategories(self, postid, username, password, tags):
        p = Post.get(postid)
        user = User.by_user_name(username)
        assert(user.password == password)
        assert(p.blog.owner == user or user in p.blog.posters)
        hub.begin()
        for ts in tags:
            t = Tag.get(ts['categoryId'])
            if not t in p.tags:
                p.addTag(t)
        hub.commit()
        return True       

class PingBackController(controllers.RootController):
    @turbogears.expose()
    def ping(self, sourceURI, targetURI):
        parts = targetURI.split('/')
        assert (len(parts) > 2)
        (blogslug,postslug) = (parts[-2],parts[-1])
        b = Blog.bySlug(blogslug)
        p = Post.bySlug(postslug)
        assert (p in b.posts)
        hub.begin()
        t=Trackback(post=p,url=sourceURI)
        hub.commt()
        return "Ping received and created with id:",t.id

    
class RPCController(controllers.RootController):
    blogger = BloggerController()
    metaWeblog = MetaWeblogController()
    mt = MTController()

    def _cpOnError(self):
        import traceback, StringIO
        bodyFile = StringIO.StringIO()
        traceback.print_exc(file = bodyFile)
        errorBody = bodyFile.getvalue()
        cherrypy.response.body = [xmlrpclib.dumps(
            xmlrpclib.Fault(1, errorBody)
            )]

# vim: expandtab tabstop=4 shiftwidth=4:
