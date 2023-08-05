<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head  py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
    <link href="/static/css/admin.css" type="text/css" rel="stylesheet" />
    <title py:replace="''" />
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <meta py:replace="item[:]"/> 
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">

    <div id="wphead"><h1>${blog.name} <span>(<a href="${blog.link()}">View site &raquo;</a>)</span></h1></div>
    <div id="user_info"><p>Howdy, <strong>${tg.identity.user.display_name}</strong>. [<a href="/logout" title="Log out of this account">Sign Out</a>, <a href="${tg.identity.user.link()}">My Account</a>] </p></div>
    <?python
    from turbogears.identity.conditions import has_permission
    can_admin = has_permission('can_admin')
    ?>
  <ul id="adminmenu">
      <li py:if="can_admin"><a href="/admin">Site Dashboard</a></li>
      <li><a href="/blog_admin?bid=${blog.id}">Blog Dashboard</a></li>
      <li><a href="/blog_admin/write?bid=${blog.id}">Write</a></li>
      <li><a href="/blog_admin/manage?bid=${blog.id}">Manage</a></li>
      <li><a href="/blog_admin/settings?bid=${blog.id}">Settings</a></li>
    </ul>
  
  <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
  
  <div py:replace="item[:]"/>

      <div id="footer"><p>Thank you for using<br /><a href="http://turboblog.devjavu.com/projects/turboblog/">TurboBlog</a><br />          </p>
      </div>
</body>
</html>
