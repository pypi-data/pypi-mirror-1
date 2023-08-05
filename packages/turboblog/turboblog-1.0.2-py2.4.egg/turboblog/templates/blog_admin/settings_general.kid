<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
      <ul id="submenu">
          <li><a href="${tg.url('/blog_admin/settings_general?bid=%s' % blog.id)}" class="current">General</a></li>
          <li><a href="${tg.url('/blog_admin/settings_reading?bid=%s' % blog.id)}">Reading</a></li>
          <li><a href="${tg.url('/blog_admin/settings_comments?bid=%s' % blog.id)}">Comments</a></li>
      </ul>
 
    <div class="wrap">

    <h2>General Blog Settings</h2>
    <form method="post" action="/blog_admin/update_general_settings?bid=${blog.id}">
        <table class="optiontable">
            <tr valign="top">
                <th scope="row">Weblog title:</th>
                <td><input name="blogname" type="text" id="blogname" value="${blog.name}" size="40" />
                <br />
                <b><i>Warning</i></b> changing this title will change your Url and your readers may loose track of your blog.</td>
            </tr>
            <tr valign="top">
                <th scope="row">Tagline:</th>
                <td><input name="blogdescription" type="text" id="blogdescription" style="width: 95%" value="${blog.tagline}" size="45" />
                    <br />
                    In a few words, explain what this weblog is about.</td>
            </tr>
            <tr valign="top">
                <th scope="row">Blog Admin:</th>
                <td>
                    <?python
                    from turboblog.model import User
                    ?>
                    <select name="admin">
                        <option py:for="u in User.select()" py:attrs="dict(value=u.id, selected=(u==blog.owner and 'selected' or None))">${u.display_name}</option>
                    </select>
                <br/>
                This is the person who can manage posts,tags and etc.
                </td>
            </tr>
             <tr valign="top">
                 <th scope="row">Theme:</th>
                 <td>
                     <select name="theme">
                         <option>default</option>
                     </select>
                     <br/>
                     Select a theme that will be used from your blog
             </td>
         </tr>
        </table>
        <p class="submit"><input type="submit" name="submit" value="Update Options &raquo;" /></p>
    </form>

  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>
</body>
</html>
