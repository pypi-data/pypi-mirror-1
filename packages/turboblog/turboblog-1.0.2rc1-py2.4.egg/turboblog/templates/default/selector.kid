<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
<title>Select a blog!</title>
<link py:strip="1" py:for="css in tg_css">${css.insert()}</link>
<link py:strip="1" py:for="js in tg_js_head">${js.insert()}</link>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="generator" content="TurboBlog" />
<link rel="stylesheet" href="/static/css/style.css" type="text/css" media="screen" />
 
<style type="text/css" media="screen">
/*	To accomodate differing install paths of WordPress, images are referred only here,
	and not in the wp-layout.css file. If you prefer to use only CSS for colors and what
	not, then go right ahead and delete the following lines, and the image files. */
		
	body { background: url("/static/images/kubrickbgcolor.jpg"); }	
	#page { background: url("/static/images/kubrickbg.jpg") repeat-y top; border: none; }
	#header { background: url("/static/images/kubrickheader.jpg") no-repeat bottom center; }
	#footer { background: url("/static/images/kubrickfooter.jpg") no-repeat bottom; border: none;}

/*	Because the template is slightly different, size-wise, with images, this needs to be set here
	If you don't want to use the template's images, you can also delete the following two lines. */
		
	#header 	{ margin: 0 !important; margin: 0 0 0 1px; padding: 1px; height: 198px; width: 758px; }
	#headerimg 	{ margin: 7px 9px 0; height: 192px; width: 740px; } 

/* 	To ease the insertion of a personal header image, I have done it in such a way,
	that you simply drop in an image called 'personalheader.jpg' into your /images/
	directory. Dimensions should be at least 760px x 200px. Anything above that will
	get cropped off of the image. */
	/*
	#headerimg { background: url('/static/images/personalheader.jpg') no-repeat top;}
	*/
</style>
</head>
    <body>
        <div id="page">
<div id="header">
    <div id="headerimg">
        <h1>Blog Selector</h1>
        <div class="description">please select a blog you want to view:</div>
    </div>
</div>
<hr />
<div id="content" class="narrowcolumn">
    <ol>
        <li py:for="blog in blogs"><h2><a href="${blog.link()}">${blog.name}</a> - ${blog.tagline}</h2></li>
    </ol>
</div>

<hr />

<div id="sidebar">
    <ul>
        <li>
        <img src="/static/images/oddlogo.png"/>
        </li>
    </ul>
</div>
<div id="footer">
    <br/>
    <p>This site is powered by TurboBlog</p>
</div>
<hr />
</div>
<!-- Gorgeous design by Michael Heilemann - http://binarybonsai.com/kubrick/ -->
<?python
from turbogears.identity.conditions import has_permission
from turboblog.model import User, Post
can_admin = has_permission('can_admin')
?>
<div py:if="can_admin" id="wpcombar">
    <div id="quicklinks">
        <ul>
            <li py:if="can_admin">  <a href="/admin"> Site Dashboard </a> </li>
        </ul>
    </div>

    <div id="loginout"> Howdy,
        ${tg.identity.user.display_name}
        &#160;&#160;[

        <a href="/logout" title="Log out of this account"> Sign Out </a>

        ] </div>
</div>
</body>
</html>
