<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python
import sitetemplate 
from turboblog.controllers import _theme_css
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
<title>${blog.name}</title>
<link py:strip="1" py:for="css in tg_css">${css.insert()}</link>
<link py:strip="1" py:for="js in tg_js_head">${js.insert()}</link>
<meta py:replace="item[:]"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="TurboBlog" />
<link rel="stylesheet" href="${_theme_css(blog)}" type="text/css" media="screen" />
<link rel="stylesheet" href="/static/css/livesearch.css" type="text/css" media="screen" />
<link rel="pingback" href="/RPC" />
<SCRIPT SRC="/tg_widgets/turbogears/js/MochiKit.js" TYPE="text/javascript">
</SCRIPT>
<script type="text/javascript" src="/static/javascript/livesearch.js"></script> 
        <script type="text/javascript">
            function flashedStatusMessage() {
                var flashData = getElement('flashTransport').value;
                if (flashData != "") {
                    statusmsg = eval('(' + flashData + ')');
                    displayStatusMessage(statusmsg['status'], statusmsg['msg']);
                }
            }
            addLoadEvent(flashedStatusMessage);
            addLoadEvent( liveSearchInit );
</script>
</head>
<header py:strip="1" py:match="item.tag=='{http://www.w3.org/1999/xhtml}header'">
<div id="header">
    <div id="headerimg">
        <h1><a href="${blog.link()}">${blog.name}</a></h1>
        <div class="description">${blog.tagline}</div>
    </div>
</div>
<hr />
<div id="statusmessage"></div>
<input type="hidden" id="flashTransport" name="flashTransport" py:attrs="value=tg_flash or ''" />
</header>

<sidebar  py:strip="1" py:match="item.tag=='{http://www.w3.org/1999/xhtml}sidebar'">
<?python
from turbogears.identity.conditions import has_permission
import turboblog.plugins
plugins = turboblog.plugins.get_sidebar_plugins()
print plugins
can_edit = has_permission('can_post') and (tg.identity.user in blog.posters) or (tg.identity.user == blog.owner)
can_admin = has_permission('can_admin')
can_comment = has_permission('can_comment')
?>

<div id="sidebar">
    <ul>

        <li>
            <div>
                <form onsubmit="return liveSearchSubmit()" id="searchform" name="searchform" method="get" action="/?s=">
                    <input type="text" id="livesearch" name="s" value="search this site" onkeypress="liveSearchStart()" onblur="setTimeout('closeResults()',2000); if (this.value == '') {this.value = '';}"  onfocus="if (this.value == 'search this site') {this.value = '';}"  />
                    <input type="submit" id="searchsubmit" style="display: none;" value="Search" />
                    <div id="LSResult" style="display: none;"><div id="LSShadow"></div></div>
                </form>
            </div>
        </li>

        <li><h2>Author</h2>
        <?python
        from turboblog.model import User
        avatar = blog.owner.avatar_link()
        ?>
        <p>
        <table>
            <tr>
                <td><img width="40" height="40" py:if="avatar" src="${avatar}" /></td>
                <td>${blog.owner.about}</td>
            </tr>
        </table>
        </p>
        </li>

        <li><h2>Archives</h2>
        <ul>
            <li py:for="m in blog.archives('monthly')">
            <a href="${blog.link()}?arc_year=${m[1]};arc_month=${m[2]}">${m[0]}</a></li>
        </ul>
        </li>

        <?python
        try:
            cloud = int(cloud)
        except:
            cloud = 0
        print cloud
        import cherrypy,re
        req = cherrypy.request
        qs = cherrypy.request.browser_url
        qs = re.sub(';cloud=\d+','', qs)        
        qs = re.sub('\?cloud=\d+','?', qs)        
        sep = '?'
        if '?' in qs: sep=";"
        ?>
        <li><h2>Tags</h2> <span py:if="not cloud"><a href="${qs}${sep}cloud=1">(view as cloud)</a></span><span py:if="cloud"><a href="${qs}${sep}cloud=0">(view as list)</a></span><br/>
        <ul py:if="not cloud">
            <li py:for="tag in blog.tags"><a href="${blog.link()}?tagged=${tag.id}">${tag.name} (${len(tag.posts)})</a></li>
            <li><a href="${blog.link()}?untagged=1">Untagged (${len(blog.untagged_posts())})</a></li>
        </ul>
        <span py:if="cloud">
            <span py:for="tag in blog.tag_cloud()">
                <?python
                if tag[2] == -1: tlink = blog.link()+"?untagged=1"
                else: tlink = blog.link()+"?tagged="+str(tag[2])
                ?>
                <a style="font-size: ${tag[1]}" href="${tlink}">${tag[0]}</a> 
            </span>
        </span>
        </li>
        <div>
            <span py:if="plugins" py:strip="1" py:for="pl in plugins">
                ${pl.render(blog,tg.identity.user)}
                <br/>
            </span>
        </div>
        <div>

            <li><h2>Meta</h2>
            <ul>
                <li py:if="not can_comment"><a href="/login">Login</a></li>
                <li><a href="http://validator.w3.org/check/referer" title="This page validates as XHTML 1.0 Transitional">Valid <abbr title="eXtensible HyperText Markup Language">XHTML</abbr></a></li>
                <li><a href="http://gmpg.org/xfn/"><abbr title="XHTML Friends Network">XFN</abbr></a></li>
                <li><a href="" title="Powered by TurboBlog">TurboBlog</a></li>
                <li py:if="can_comment">Logged in as ${tg.identity.user.display_name} <a href="/logout" title="Log out of this account">Logout</a>

                </li>

            </ul>
            </li>
        </div>

    </ul>
</div>

</sidebar>
<footer  py:strip="1" py:match="item.tag=='{http://www.w3.org/1999/xhtml}footer'">
<hr />
<div id="footer">
    <p>${blog.name} is proudly powered by <a href="http://turboblog.devjavu.com/projects/turboblog/">TurboBlog</a>
    <br /><a href="feed">Entries (RSS)</a>
    </p>
</div>
<hr />
</footer>
<adminbar py:strip="1" py:match="item.tag=='{http://www.w3.org/1999/xhtml}adminbar'">
<!-- Gorgeous design by Michael Heilemann - http://binarybonsai.com/kubrick/ -->
<?python
from turbogears.identity.conditions import has_permission
from turboblog.model import User, Post
can_post = has_permission('can_post') and (tg.identity.user in blog.posters) or (tg.identity.user == blog.owner)
can_admin = has_permission('can_admin')
can_admin_blog = has_permission('can_admin_blog') and (tg.identity.user == blog.owner) or can_admin
if tg.identity.user:
    ulink = User.get(tg.identity.user.id).link()
else:
    ulink = ""
try:
    a = post
except:
    post = None
?>
<div py:if="can_admin or can_post" id="wpcombar">
    <div id="quicklinks">
        <ul>
            <li py:if="can_admin">  <a href="/admin"> Site Dashboard </a> </li>
            <li py:if="can_admin_blog">  <a href="/blog_admin?bid=${blog.id}"> Blog Dashboard </a> </li>
            <li>  <a href="${Post.edit_link(blog.id)}"> New Post </a> </li>
            <li py:if="post"> <a href="${Post.edit_link(blog.id,post.id)}"> Edit this post </a> </li>
        </ul>
    </div>

    <div id="loginout"> Howdy,
        <a href="${ulink}"> ${tg.identity.user.display_name} </a>
        &#160;&#160;[

        <a href="/logout" title="Log out of this account"> Sign Out </a>
        ,
        <a href="${ulink}"> My Account </a>

        ] </div>
</div>
</adminbar>

</html>
