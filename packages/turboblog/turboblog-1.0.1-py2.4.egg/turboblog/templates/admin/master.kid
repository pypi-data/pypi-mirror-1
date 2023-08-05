<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head  py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
    <link href="/static/css/admin.css" type="text/css" rel="stylesheet" />
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:replace="''" />
    <SCRIPT SRC="/tg_widgets/turbogears/js/MochiKit.js" TYPE="text/javascript">
    </SCRIPT>
    <div py:replace="item[:]"/>
    
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">

    <div id="wphead"><h1>TurboBlog Dashboard <span>(<a href="/">View site &raquo;</a>)</span></h1></div>
    <div id="user_info"><p>Howdy, <strong>${tg.identity.user.display_name}</strong>. [<a href="/logout" title="Log out of this account">Sign Out</a>, <a href="${tg.identity.user.link()}">My Account</a>] </p></div>

  <ul id="adminmenu">
      <li><a href="/admin">Dashboard Home</a></li>
      <li><a href="/admin/blogs/">Blogs</a></li>
      <li><a href="/admin/users/">Users</a></li>
    </ul>
  
    <div id="statusmessage"  py:if="tg_flash" class="flash" py:content="tg_flash"></div>
  
  <div py:replace="item[:]"/>

      <div id="footer">Thank you for using<br /><a href="http://turboblog.devjavu.com/projects/turboblog/">TurboBlog</a><br />

      </div>
</body>
</html>
