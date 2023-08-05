#!/usr/local/bin/python
# -*- coding: latin1 -*-
"""
gravatar.py -- Simple interface to gravatar.com, 
the Globally Recognized AVATAR.

Project page is located at http://www.deelan.com/dev/gravatar/

Most simple usage:

>>> import gravatar
>>> gravatar.get_uri('john@example.com')
'http://www.gravatar.com/avatar.php?gravatar_id=d4c74594d841139328695756648b6bd6'

Then put returned URI into an HTML image tag, like this: 

<img alt="avatar" src="your-uri-goes-here" width="80" height="80" />

Maybe you want ot give a default URI if requested avatar don't match 
your web site rating criteria or cannot be found in gravatar.com database? 
Then do the following:

>>> gravatar.get_uri('john@example.com', default='http://example.com/blah.jpg')
'http://www.gravatar.com/avatar.php?default=http%3A%2F%2Fexample.com%2Fblah.jpg&gravatar_id=d4c74594d841139328695756648b6bd6'

I may want to grab actual bytes for the avatar. Use the get_image() function:

>>> mime, bytes = gravatar.get_image('john@example.com')
>>> print mime
image/jpeg

Image will issue a HTTP request on gravatar.com, grab the images bytes and 
return them as a (mime, bytes) tuple, common MIME types are image/gif, image/png
or image/jpeg.

If you have Joe Gregorio's httpcache module installed in your system the get_image() function will
use that to cache images on disk, sparing GET requests to the remote server. For further
details check httpcache project page: http://bitworking.org/projects/httpcache/
"""

__author__ = "Andrea Peltrin (deelan AT interplanet DOT it)"
__copyright__ = "Copyright 2005, Andrea Peltrin"
__contributors__ = []
__version__ = "0.1.1"
__license__ = "MIT"
__history__ = ""

#@@ CACHE = 1

from urllib import urlopen, urlencode

class NoCache(object):
    """
    This mimics HTTPCache class, providing a stub if module 
    httpcache is missing.
    """
        
    def __init__(self, uri):
        self._uri = uri
        self._info = None
        
    def content(self):
        f = urlopen(self._uri)    
        self._info = f.info()
                
        data = f.read()        
        f.close()

        return data

    def info(self):
        return self._info

    def fresh(self):        
        # resource is always fresh, 
        #  since ther's no cache
        return True 

try: 
    from httpcache import HTTPCache as Cache
except ImportError, ex:
    Cache = NoCache 

# ---------------------------------------------------------



BASE_URL = "http://www.gravatar.com/avatar.php?"

# HTTP request args
ID = 'gravatar_id'
SIZE = 'size'
RATING  = 'rating'
DEFAULT  = 'default'
BORDER = 'border'

import md5

def _make_uri(email, rating, size, default, border):
    
    email = email.strip()
    
    # make md5
    hash = md5.md5(email).hexdigest()
            
    args = {
        ID : hash
    }
    
    if rating:
        args[RATING] = rating
    
    if size:
        args[SIZE] = min(size, 80) # cap to 80px
        
    if default:
        args[DEFAULT] = default
    
    if border:
        args[BORDER] = border
                
    # build url
    url = BASE_URL + urlencode(args)
    
    return url

def get_uri(email, rating=None, size=None, default=None, border=None):

    """
    Return the gravatar URI. Parameters are:
    
    * email, this is mandatory 
    * size, desired integer size of the avatar (up to 80px)
    * rating, a string chosen from "G", "PG" "R" or "X"
    * border, the avatar border color as hex decimals (e.g. "FF0000" or "F00") 
    * default, fall back URI if avatar is not found or does not match rating   
    """
    
    return _make_uri(email, rating, size, default, border)

def get_image(email, rating=None, size=None, default=None, border=None):
    """
    Make the gravatar URL, do an HTTP request and return 
    the tuple (mime-type, image bytes). 
    
    Paramenters are the same as get_uri().
    """    
    
    uri = _make_uri(email, rating, size, default, border)
    
    c = Cache(uri)
    
    content = c.content()    
    mime = c.info()['Content-Type']
    
    return mime, content



##
## main
##
if __name__ == "__main__":
    print __doc__


