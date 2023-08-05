import sys
import os
from elementtree import ElementTree

import pkg_resources

class RecentPostsPlugin(object):
    def render(self, blog, user):
        html = "<div id='recent_posts'><strong>Last 5 Posts</strong><ol>"
        for p in blog.get_posts(True, 5):
            html += "<li><a href='%s'>%s</a></li>"%(p.link(),p.title)
        html += "</ol></div>"
        ret = ElementTree.XML(html)
        return ret
            
