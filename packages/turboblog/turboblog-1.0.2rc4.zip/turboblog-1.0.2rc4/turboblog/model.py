#pylint: disable-msg: W0232
from sqlobject import *
from sqlobject.dberrors import DuplicateEntryError, OperationalError
from sqlobject.sqlbuilder import AND
#from turbogears.jsonify import jsonify
from turbojson.jsonify import jsonify
from turbogears.database import PackageHub
#from turbogears.identity.soprovider import TG_User, \
#        TG_Group,TG_Permission,jsonify_permission,jsonify_group
from turbogears import identity
from datetime import datetime,date
from elementtree import ElementTree
import re,urllib2,urllib,turbogears
from turbogears.identity.conditions import has_permission    

# imports added for porting or bugfixing
from sqlobject.sqlbuilder import LEFTJOINOn 

hub = PackageHub("turboblog")
__connection__ = hub

month_names = [date(2005, x, 1).strftime("%B") for x in range(1,13)] 

class FileNotFoundError(Exception):
    '''
    This is raised if the desired file is not found
    and should be catched by the caller.
    This ensures ORM independence for a future migration
    because the caller does not have to catch an SQLObject specific exception
    '''
    pass

class StoredFile(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,C0103
        table = 'storedfiles'
        
    # filename is not unique because the id is unique already
    # filename is just a way to send back some filename
    # to someone downloading the file, it is not really
    # used by us
    filename = UnicodeCol(length=255)
    # store the size in octet of the file
    filesize = IntCol()
    # the blog to which this file belongs
    blog = ForeignKey("Blog") 
    # can be None... but not for images
    mimetype = StringCol(length=50)
    # the actual data for our file
    data = BLOBCol(notNone=True)

    @staticmethod
    def get_file(bid, fileid):
        '''
        this static method permits to get one file and be sure it belongs
        to the right blog.
        '''
        try:
            file_select_result = StoredFile.select(AND(
                StoredFile.q.id==fileid,
                StoredFile.q.blogID==bid))

        except SQLObjectNotFound:
            msg = _('Blog %s does not have the file %s' % (bid, fileid))
            raise FileNotFoundError()

        # we can only have one
        return file_select_result[0]

class Blog(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,C0103
        table = "turboblog_blog"

    owner = ForeignKey("User")
    posters = RelatedJoin("User", intermediateTable="turboblog_blog_user",
            joinColumn="user_id", otherColumn="blog_id")

    name = UnicodeCol(length=255, alternateID=True, unique=True, notNone=True)
    tagline = UnicodeCol(length=255, title="Tag Line")
    posts = MultipleJoin("Post", joinColumn="blog_id")
    tags = RelatedJoin("Tag", intermediateTable="turboblog_blog_tag",
            joinColumn="tag_id", otherColumn="blog_id")

    slug = StringCol(alternateID=True, length=255, default="")
    theme = StringCol(default="")

    def _set_name(self, value):
        self._SO_set_slug(slugify(value, self))
        self._SO_set_name(value)

    def untagged_posts(self):
        return [p for p in self.get_posts() if not p.tagged()]
    
    def tag_cloud(self, smallest=10, largest=48, unit='pt'):
        counts = dict()

        for tag in self.tags:
            counts[tag.name] = len(tag.posts)

        counts['Untagged'] = len(self.untagged_posts())
        spread = max(counts.values()) - min(counts.values())

        if spread <= 0:
            spread = 1

        fontspread = largest - smallest
        fontstep = spread / fontspread

        if fontstep <= 0:
            fontstep = 1

        ret = []
        for k,v in counts.items():
            if k != 'Untagged': tid = Tag.byName(k).id
            else: tid = -1
            ret += [(k, "%d%s" % (smallest + (v/fontstep), unit), tid)]
        return ret   
    
    def get_files(self):
        '''
        returns: all files for the current blog
        '''
        return StoredFile.select(StoredFile.q.blogID==self.id)

    def get_file(self, fid):
        '''
        returns: the desired file
        '''
        # TODO: not optimum we should do one request
        # but I am tired :)
        myfile = StoredFile.get(fid)
        if not myfile.blogID == self.id:
            msg = _('The file was not found')
            raise FileNotFoundError(msg)
        
        return myfile

    def delete_file(self, fid):
        '''
        delete the desired file
        '''
        todel_file = self.get_file(fid)
        todel_file.destroySelf()

    def get_comments(self):
        '''
        returns: all comments for the current blog sorted in reverse order
        by modification date
        '''
        return Comment.select(Post.q.blogID == self.id,
                join=LEFTJOINOn(None, Post, Comment.q.postID == Post.q.id),
                orderBy=Comment.q.creation_time).reversed()

    def search_comments(self, search_string, case=False, limit=None):
        '''
        search all comments containing this string.
        case insensitive is on by default but can be changed by passing
        the case=True parameter

        @param search_string: the search string (unicode)
            to search in the comments bodies
        @type search_string: unicode string

        @param case: A boolean flag to controle case sensitivity
            True means search case sensitive, False means case insensitive
            False is the default value if nothing is passed.
            WARNING: this is not implemented at the moment.
        @type search: boolean

        @param limit: the maximum number of matches to return for this search
            the default is None, meaning every match will be returned
        @type limit: integer

        returns: all comments matching the search string sorted in by
            modification date in reverse order.
        '''
        return Comment.select(
                AND(
                    Post.q.blogID == self.id,
                    Comment.q.content.contains(search_string)
                    ),
                join=LEFTJOINOn(None, Post, Comment.q.postID == Post.q.id),
                orderBy=Comment.q.creation_time).reversed()
        
    def get_posts(self, published=True, limit=None):
        '''
        @param published: a flag to indicat if you want to select
                published posts or not
        @type published: Boolean

        @param limit: the max number of posts grab from the db
        @type limit: integer
        '''
        return Post.select(AND(
                Post.q.blogID == self.id,
                Post.q.published == published),
                orderBy = Post.q.modification_time,
                limit = limit).reversed()

    def archives(self, type='monthly', arg=None):
        def srt(x,y):
            return cmp(x.creation_time, y.creation_time)
        ar = dict()
        for p in self.posts:
            if not p.creation_time.year in ar:
                ar [p.creation_time.year] = dict()
            if not  p.creation_time.month in ar [p.creation_time.year]:
                ar [p.creation_time.year] [p.creation_time.month] = []
            ar [p.creation_time.year] [p.creation_time.month] += [p]
        #TODO: implement weekly/yearly
        if ar:
            if type == 'monthly':
                res = []
                year = max(ar.keys())
                for mi in range(1,13):
                    if mi in ar[year]:
                        res += [(month_names[mi-1] + " %d (%d)" % (
                            year, len(ar[year][mi])), year, mi)]
                return res
            elif type == 'yearly':
                raise Exception("Not implemented!")
            elif type == 'weekly':
                raise Exception("Not implemented!")
        return ar
    
    def link(self):
        return turbogears.url("/%s" % self.slug)

    def admin_link(self):
        return "/blog_admin?bid=%d" % self.id

    def feed(self):
        feed = { 
            "title": self.name, 
            "subtitle": self.tagline, 
            "author": {"name": self.owner.display_name},
            "id": self.id,
            "link": self.link(),
            "entrys": []
            }

        for post in self.posts:
            feed["entrys"] += [post.feed(self.id)]

        return feed

class Post(SQLObject):
    class sqlmeta:
        table = "turboblog_post"

    author = ForeignKey("User")    
    title = UnicodeCol(length=255)
    content = UnicodeCol(length=14000)
    published = BoolCol(default=False)
    creation_time = DateTimeCol(default=datetime.now)
    modification_time = DateTimeCol(default=datetime.now)
    comments = MultipleJoin("Comment", joinColumn="post_id")
    trackbacks = MultipleJoin("Trackback", joinColumn="post_id")
    trackback_urls = StringCol(default="")
    tags = RelatedJoin("Tag", intermediateTable="turboblog_post_tag",
            joinColumn="tag_id", otherColumn="post_id")

    blog = ForeignKey("Blog")
    slug = StringCol(alternateID=True, length=255, default="")
   
    def deleteMe(self):
        # make sure all comments for this post are also removed
        for comment in self.comments:
            comment.deleteMe()

        self.destroySelf()
   
    def _set_title(self, value):
        self._SO_set_modification_time(datetime.now())
        self._SO_set_slug(slugify(value, self))
        self._SO_set_title(value)

    def tagged(self):
        return len(self.tags) > 0
    
    @staticmethod
    def get_last(count, blog_id=None):
        if blog_id:
            return Post.select(
                    Post.q.blogID==blog_id,
                    orderBy="-creation_time",
                    limit=count
                    )
        else:
            return Post.select(orderBy="-creation_time")[:count]
    
    @staticmethod
    def edit_link(blogid, postid=None):
        if postid:
            return "/blog_admin/write?bid=%d;pid=%d" % (blogid, postid)
        
        return "/blog_admin/write?bid=%d" % blogid
    
    def delete_link(self):
        return "/blog_admin/delete_post?bid=%d;pid=%d" % (
                self.blog.id, self.id)

    def link(self, blogid=None):
        blogid = blogid or self.blog.id
        return  turbogears.url("/%s/%s" % (
            Blog.get(blogid).slug, self.slug))
    
    def trackback_link(self):
        return turbogears.url("/%s/trackback/%d" % (
            self.blog.slug,self.id))


    def cut_parsed(self, blogid):
        cut_xml =  ElementTree.fromstring(
                '<span><br/><a href="%s">[ Read More... ]</a></span>' % (
                    self.link(blogid)))

        et = ElementTree.fromstring("<span>"+self.content+"</span>") 
        for index, element in enumerate(et):
            if element.tag == 'cut':
                et[index] = cut_xml
        return ElementTree.tostring(et)

    def feed(self, blog_id):
        ret = dict( 
        {
        "title": self.title,
        "content": self.content,
        "author": {"name":self.author.display_name,
            "email":self.author.email_address},
        "link": self.link(blog_id),
        "published": self.creation_time,
        "id": self.id
        })
        return ret
    
    def send_trackbacks(self):
        params = { 'excerpt': self.content[:100],
                   'title': self.title,
                   'url': turbogears.url(self.link()),
                   'blog_name': self.blog.name
                   }

        for tb_url in self.trackback_urls.split(' '):
            if tb_url:
                postdata = urllib.unquote(urllib.urlencode(params))
                print tb_url
                print urllib2.urlopen(tb_url,postdata)
                
    def generate_comments_html(self):
        def item_html(comment, i):
            o = u'<li  class="%s" id="comment-%d">' % (i%2 and 'alt' or '', comment.id)
            alink = comment.author.link()
            avatar = comment.author.avatar_link()
            moderator = has_permission('can_moderate')
            post_owner = has_permission('can_comment') \
                    and comment.author == turbogears.identity.current.user

            o += u'<a name="comment-%d"></a><table><tr><td>' % (comment.id)

            if avatar:
                o += u'<img width="40" height="40" src="%s" />' % avatar

            o += u'</td><td>'
            o += u'<cite><a href="%s">%s</a></cite> Says: ' % (alink, comment.author.display_name)

            if not comment.approved :
                o += u'<div id="comment_%d_approval">' % comment.id
                o += u'<em>Your comment is awaiting moderation.</em><br/>'

                if moderator:
                    o += u'<a href="javascript:approve(%d,\'%s\')">Approve this post!</a>' % (
                            comment.id, self.blog.slug)

                o += u'</div><br />'

            if post_owner:
                o += u'<small class="commentmetadata">at %s <a href="javascript:makeEditable(\'comment_%d_text\',\'%s\');" > Edit comment </a>' % (
                        str(comment.creation_time), comment.id, self.blog.slug)

                o += u'</small>'

            o += u'<small class="commentmetadata"><a id="replylink-%(cid)d" href="javascript:reply(%(cid)d,\'%(slug)s\');" >Reply</a> </small>' % {
                    'cid': comment.id, 'slug': self.blog.slug}

            o += u'<span id="comment_%(cid)d_text">%(content)s</span><span id="comment_%(cid)d_text_holder"></span></td></tr></table>' % {
                    'cid': comment.id, 'content': comment.content}

            o += u"<ol class=\"commentlist\">"

            for i, c in enumerate(comment.sub_comments):
                o += item_html(c, i)

            o += u"</ol>"
            o += u'</li>'

            return o
        
        out = u"<ol class=\"commentlist\">"

        for i, c in enumerate(self.comments):
            if c.parent_id == -1:
                out += item_html(c,i)

        out += u"</ol>"
        # ElementTree.XML does not accept Unidoce data
        # so encode it properly for easy consumption :)
        return ElementTree.XML(out.encode('UTF-8'))
    
class Trackback(SQLObject):
    class sqlmeta:
        table = "turboblog_trackback"
    blog_name = UnicodeCol(default="")
    title = UnicodeCol(default="")
    url = StringCol()
    excerpt = UnicodeCol(default="")
    post = ForeignKey("Post")
    
class AntiSpam(SQLObject):
    class sqlmeta:
        table = "turboblog_antispam"

    # I hate SQLObject !!!!!
    # I'll switch to SQLAlchemy as soon as I stabilize this application
    visit_key = StringCol(length=40, alternateID=True,
            alternateMethodName="by_visit_key")
    verif_string = StringCol()

class Comment(SQLObject):
    class sqlmeta:
        table = "turboblog_comment"

    content = UnicodeCol(length=4096)
    creation_time = DateTimeCol(default=datetime.now)
    author = ForeignKey("User")
    approved = BoolCol()
    post = ForeignKey("Post")
    parent_id = IntCol(default=-1)
    sub_comments = RelatedJoin("Comment", joinColumn="parent_id")

    def deleteMe(self):
        # sub comment ?
        self.destroySelf()

    @staticmethod
    def get_last(count, blog_id=None):
        if blog_id:
            # only return comments from the desired blog
            return Comment.select(
                Post.q.blogID == blog_id,
                join=LEFTJOINOn(None, Post, Comment.q.postID == Post.q.id),
                orderBy=Comment.q.creation_time, limit=count).reversed()

        else:
            return Comment.select(orderBy="-creation_time", limit=count)

    @staticmethod
    def link_add(blogid, postid):
        return "/%s/comment/add/%s" % (Blog.get(blogid).slug,
                Post.get(postid).slug)

    def edit_link(self):
        return "/blog_admin/edit_comment?bid=%d;cid=%d" % (
                self.post.blog.id, self.id)

    def link(self):
        return self.post.link() + "#comment-%d" % self.id

    def delete_link(self):
        return "/blog_admin/delete_comment?bid=%d;cid=%d" % (
                self.post.blog.id,self.id)

    allowed_tags = [
            ['a',['title','href']],
            ['abbr',['title']],
            ['acronym',['title']],['b',[]],
            ['blockquote',[]],
            ['code',[]],
            ['em',[]],
            ['i',[]],
            ['strike',[]],
            ['strong',[]]]

    @staticmethod
    def check_attrib(eattrs, attrs):
        for a in eattrs:
            if a in attrs:
                continue
            else:
                return False

        return True

    @staticmethod
    def check_element_tags(e, tags):
        for tag in tags:
            if e.tag == tag[0] and Comment.check_attrib(e.attrib, tag[1]):
                for c in e.getchildren():
                    if not Comment.check_element_tags(e, Comment.allowed_tags):
                        return False

                return True

        return False

    @staticmethod
    def check_tags(text):
        try:
            # ElementTree.XML does not like unicode objects, give it some
            # utf8 encoded strings instead
            e = ElementTree.XML("<z>%s</z>" % text.encode('UTF-8'))

        except Exception, args:
            return False

        for el in e.getchildren():
            if not Comment.check_element_tags(el, Comment.allowed_tags):
                return False

        return True

class Tag(SQLObject):
    class sqlmeta:
        table = "turboblog_tag"
    name = UnicodeCol(length=255,alternateID=True,unique=True,notNone=True)
    posts = RelatedJoin("Post",intermediateTable="turboblog_post_tag",
            joinColumn="post_id",otherColumn="tag_id")

    blog = ForeignKey("Blog")

    def deleteMe(self):
        for p in self.blog.posts:
            if self in p.tags:
                p.removeTag(self)
        self.blog.removeTag(self)
        self.destroySelf()
        
class Settings(SQLObject):
    class sqlmeta:
        table = "turboblog_blogsettings"
    admin   = ForeignKey("User")
    default_blog = IntCol(default=-1) 

def slugify(title, table, id=0):
    """
    Code taken from Toasty Goat project
    This ugly sack of crap returns a slug from a title. The title and
    table (Posts, Pages, etc) must be passed to determine if the slug
    already exists. The id is for editing a sluggable item, making it
    so that you may replace the item with the same slug without a 
    problem.
    """
    regex = re.compile("[^\w\-\ ]")
    slug = regex.sub('', title).lower().strip().replace(' ', '-')
    
    append = ''
    while True:
        new_slug = slug[:(255 - len(str(append)))] + str(append)
        if not slug_exists(new_slug, table, id):
            return new_slug
        else:
            if append == '':
                append = 1

            append = append + 1

def slug_exists(slug, table, id):
    try:
        a = table.bySlug(slug)
        hub.end()
        if a.id == id:
            return False
        return True
    except SQLObjectNotFound:
        hub.end()
        return False

# identity models.
class Visit(SQLObject):
    class sqlmeta:
        table = "visit"

    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    created = DateTimeCol(default=datetime.now)
    expiry = DateTimeCol()

    def lookup_visit(cls, visit_key):
        try:
            return cls.by_visit_key(visit_key)
        except SQLObjectNotFound:
            return None
    lookup_visit = classmethod(lookup_visit)

class VisitIdentity(SQLObject):
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    user_id = IntCol()

class Group(SQLObject):
    """
    An ultra-simple group definition.
    """

    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_group"

    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = RelatedJoin("User", intermediateTable="user_group",
                        joinColumn="group_id", otherColumn="user_id")

    # collection of all permissions for this group
    permissions = RelatedJoin("Permission", joinColumn="group_id", 
                              intermediateTable="group_permission",
                              otherColumn="permission_id")

class User(SQLObject):
    """
    Reasonably basic User definition.
    Probably would want additional attributes.
    """
    # names like "Group", "Order" and "User" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table = "tg_user"

    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    display_name = UnicodeCol(length=255)
    password = UnicodeCol(length=40)
    created = DateTimeCol(default=datetime.now)

    # groups this user belongs to
    groups = RelatedJoin("Group", intermediateTable="user_group",
                         joinColumn="user_id", otherColumn="group_id")

    avatar = BLOBCol(length=14000)
    about  = UnicodeCol(length=1025) 
    blogs  = RelatedJoin("Blog", intermediateTable="turboblog_blog_user",
            joinColumn="blog_id", otherColumn="user_id")

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."
        password_hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(password_hash)

    def set_password_raw(self, password):
        "Saves the password as-is to the database."
        self._SO_set_password(password)

    def link(self):
        return turbogears.url("/user/show/%s"%self.user_name)
    
    def avatar_link(self):
        if not self.avatar: return None
        return "/user/avatar/%s"%self.user_name
    def _set_avatar(self, value):
        if value:
            self._SO_set_avatar(value.encode('base64'))
        else:
            self._SO_set_avatar(None)
            
    def _get_avatar(self):
        av = self._SO_get_avatar()
        if av: return av.decode('base64')
        return None

class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)

    groups = RelatedJoin("Group",
                        intermediateTable="group_permission",
                         joinColumn="permission_id", 
                         otherColumn="group_id")

def jsonify_myuser(obj):
    result = {}
    for attr in ['user_name','id','display_name','email_address','password','about']:
        result[attr] = jsonify( getattr(obj,attr) )
        
    result["groups"]= jsonify( [g.group_name for g in obj.groups] )
    result["permissions"]= jsonify( [p.permissionId for p in obj.permissions] )
 
    return result
jsonify_myuser = jsonify.when('isinstance(obj, User)')(jsonify_myuser)

def create_model():
    # create the database tables
    try:
        hub.begin()

        Blog.createTable(ifNotExists=True)
        Post.createTable(ifNotExists=True)
        Comment.createTable(ifNotExists=True)
        Trackback.createTable(ifNotExists=True)
        AntiSpam.createTable(ifNotExists=True)
        Tag.createTable(ifNotExists=True)
        Settings.createTable(ifNotExists=True)

        User.createTable(ifNotExists=True)
        Group.createTable(ifNotExists=True)
        Permission.createTable(ifNotExists=True)

        hub.commit()

        # our default set of permissions
        can_admin = Permission(permission_name="can_admin",
                description="Can add/delete blogs/users")
        can_admin_blog = Permission(permission_name="can_admin_blog",
                description="Can manage one blog")
        can_post = Permission(permission_name="can_post",
                description="Can add posts")
        can_comment = Permission(permission_name="can_comment",
                description="Can add comments")
        can_moderate = Permission(permission_name="can_moderate",
                description="Can approve comments")

        hub.commit()

        # groups
        admin = Group(group_name='admin', display_name="Administrators")
        [admin.addPermission(t) for t in [can_admin, can_post, 
            can_comment, can_moderate, can_admin_blog]]

        user = Group(group_name='user', display_name="Users")
        user.addPermission(can_comment)

        poster = Group(group_name='poster', display_name="Posters")
        [poster.addPermission(t) for t in [can_comment, can_post,
            can_moderate]]

        blogadmin = Group(group_name='blogadmin', display_name="Blog admins")
        [blogadmin.addPermission(t) for t in [can_comment, can_post,
            can_moderate, can_admin_blog]]

        hub.commit()

        # Admin User
        # TODO: change this to have a password from config file or
        # something... I don't know yet...
        dude = User(user_name='admin', display_name="Administrator",
                email_address="me@me.com", password="secret",
                avatar='',
                about="A little something about you, the author. \
                        Nothing lengthy, just an overview.")
        dude.addGroup(admin)

        hub.commit()

        # default blog
        blog = Blog(name="Default blog", tagline="default turboblog!",
                ownerID=dude.id)
        blog.addUser(dude)

        # default setting
        settings = Settings(admin=dude, default_blog=1)

        hub.commit()
        hub.end()

    except KeyError:
        log.warning("No database is configured.")
        return

    except DuplicateEntryError:
        # this is surely because user has already a database
        # setup... don't touch this...
        hub.end()
        return

try:
    User.get(1)

except OperationalError:
    # tables are not created... we should create theses
    create_model()

except SQLObjectNotFound:
    # the user did some cleanup
    # don't touch
    pass

# Additionnal Tables
# we put them here because it will create them
# even if all other tables exist and so
# users from older versions get the new table
hub.begin()
StoredFile.createTable(ifNotExists=True)
hub.end()
                       
# vim: expandtab tabstop=4 shiftwidth=4:
