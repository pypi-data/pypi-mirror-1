# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.

from turbogears import testutil, database
from turboblog.model import User, Blog, Tag

class TestUser(testutil.DBTest):
     '''User Tests here'''
     def test_creation(self):
         "Object creation should set the name"
         obj = User(user_name = "gman",
                       email_address = "spam@python.not",
                       display_name = "Mr G",
                       password = "bcbcbcbc",
                       avatar='',
                       about='G.')

         assert obj.display_name == "Mr G"

class TestBlog(testutil.DBTest):
    '''Blog tests here'''
    def test_creation(self):
        '''Blog creation should set a blog name'''
        u = User(user_name = "gman", email_address = "spam@python.not",
                display_name = "Mr G", password = "bcbcbcbc",
                avatar='', about='G.')
        b = Blog(owner=u, name="My Blog", tagline="Super Blogotest")

        assert b.name == "My Blog"

class TestTag(testutil.DBTest):
    '''Tag Tests here'''

    def test_creation(self):
        '''Tag creation should set a blog'''
        u = User(user_name = "gman", email_address = "spam@python.not",
                display_name = "Mr G", password = "bcbcbcbc",
                avatar='', about='G.')
        b = Blog(owner=u, name="My Blog", tagline="Super Blogotest")
        t = Tag(name='TurboGears', blog=b)

        assert t.blog == b

