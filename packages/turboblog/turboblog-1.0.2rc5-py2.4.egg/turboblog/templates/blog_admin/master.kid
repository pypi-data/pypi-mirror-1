<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
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
    ${adminmenu}
  
  <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
  
  <div py:replace="[item.text]+item[:]"/>

      <div id="footer"><p>Thank you for using<br /><a href="http://turboblog.devjavu.com/projects/turboblog/">TurboBlog</a><br />          </p>
      </div>
</body>
</html>
