import sys
import os
from elementtree import ElementTree
from sqlobject import *
from sqlobject.sqlbuilder import AND
from turbogears.database import PackageHub
from datetime import datetime
from turboblog.model import *
import pkg_resources
import cherrypy
import turbogears
from turbogears import controllers
from turbogears import identity
from turboblog.model import *
from elementtree import ElementTree

hub = PackageHub("turboblog")
__connection__ = hub

class ShoutBoxController(controllers.RootController):

    @turbogears.expose()
    @identity.require(identity.has_permission('can_comment'))
    def add_text(self, user, text):
        hub.begin()
        u = User.by_user_name(user)
        s = Shout(who=u,text=text)
        hub.commit()
        return dict()
    
    @turbogears.expose()
    def get_text(self, last):
        ret = Shout.get_shouts()
        if ret:
            if not ret[-1]['id'] == int(last):
                return dict(shouts=Shout.get_shouts())
        return dict(shouts=[])
 
class Shout(SQLObject):
    created = DateTimeCol(default=datetime.now)
    who = ForeignKey('User')
    text = StringCol(length=100)

    @staticmethod
    def get_shouts():
        ret = []
        for s in Shout.select(orderBy="created")[:10]:
            ret += [ dict(who=s.who.userId,text=s.text,id=s.id) ]
        return ret
    
tpl = """ 
<div id="shoutboxwrapper">
<style>
#chatoutput {
/* Height of the shoutbox*/
height: 200px;
/* Horizontal Scrollbar Killer */
padding: 6px 8px; 
/* Borders */
border: 1px solid #0066CC;
border-width: 1px 2px;

font: 11px helvetica, arial, sans-serif;
color: #333333;
background: #FFFFFF;
overflow: auto;
margin-top: 10px;
}

#chatoutput span {
font-size: 1.1em;
color: #0066CC;
}

#chatForm label, #shoutboxAdmin {
display: block;
margin: 4px 0;
}

#chatoutput a {
font-style: normal;
font-weight: bold;
color: #0066CC
}

/* User names with links */
#chatoutput li span a {
font-weight: normal;
display: inline !important;
border-bottom: 1px dotted #0066CC
}

#chatForm input, #chatForm textarea {
width: 100px;
display: block;
margin: 0 auto;
}

#chatForm textarea {
width: 150px;
}


#chatForm input#submitchat {
width: 70px;
margin: 10px auto;
border: 2px outset;
padding: 2px;
}

#chatoutput ul#outputList {
padding: 0;
position: static;
margin: 0;
}

#chatoutput ul#outputList li {
padding: 4px;
margin: 0;
color: #333333;
background: none;
font-size: 1em;
list-style: none;
}

/* No bullets from Kubrick et al. */
#chatoutput ul#outputList li:before {
content: '';
}

ul#outputList li:first-line {
line-height: 16px;
}

#lastMessage {
padding-bottom: 2px;
text-align: center;
border-bottom: 2px dotted #666666;
}

em#responseTime {
font-style: normal;
display: block;
}
</style>
    <input id="shout_last" type="hidden" value="%d"/>
    <script>
    function refresh_box(){
        var d = loadJSONDoc("/shout/get_text?last="+getElement('shout_last').value);
        d.addCallbacks(function (data){ 
                if(data['shouts'].length){
                    e = getElement('outputList');
                    replaceChildNodes(e);
                    sh =  data['shouts'];
                    for(s in sh){
                        node = LI({},sh[s].who+": "+sh[s].text);
                        lid = sh[s].id;
                        appendChildNodes(e, node);
                    }
                    getElement('shout_last').value = lid;
                }
                setTimeout("refresh_box()",1000);    
        } );
    }
   refresh_box();
    </script>

    <strong>Shoutbox!</strong>
    <div id="chatoutput">    
        <ul id="outputList">
        </ul>
        %s
   </div>
</div>
"""
tplform = """
        <form id="chatForm">
 <script>
    function add_text(){
        var d = loadJSONDoc("/shout/add_text?user=%s;text="+getElement('shoutbox_input').value);
        e = getElement('shout_last');
        e.value += 1;
        appendChildNodes(getElement('outputList'),LI({},"%s: "+getElement('shoutbox_input').value));
    }
</script>
            <input id="shoutbox_input" type="text" />
            <a href="javascript:add_text();">add text</a>
        </form>
 
"""
class ShoutboxPlugin(object):
       
    def render(self, blog, user):
        Shout.createTable(ifNotExists=True)
        cherrypy.root.shout = ShoutBoxController()
        f = "You need to login to use shoutbox."
        if user:
            f = tplform%(user.userId,user.userId)
        return ElementTree.XML( tpl%(0,f) )

