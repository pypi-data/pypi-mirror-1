<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
    <script>
    function update_default(who) {
        var d = loadJSONDoc("/admin/set_default?defblog="+who);
        d.addCallbacks(function (data){ return 1 } );
    }
    function update_admin(){
        box = getElement('adminselect');
        aid = box.options[box.selectedIndex].value;
        var d = loadJSONDoc("/admin/set_admin?aid="+aid);
        d.addCallbacks(function (data){ return 1 } );
    }
        
    </script>
</head>

<body>
      <div class="wrap">

          <h2>Blog selection</h2>

  <h3>Welcome to your TurboBlog</h3>

  <p>Please select the blog you want to edit (and mark it as default if you want)</p>
  <?python from turboblog.model import Blog,User ?>
  <input onClick="update_default(-1);"  type="radio" name="def" value="-1"
  py:attrs="dict(checked=(defblog==-1 and 'checked' or None))"> Show blog selector page by default</input><br/>
  <span py:strip="1" py:for="blog in Blog.select()">
      <input onClick="update_default(${blog.id});" type="radio" name="def" value="${blog.id}" 
      py:attrs="dict(checked=(defblog==blog.id and 'checked' or None))">
      <a href="${blog.admin_link()}"> ${blog.name}</a> 
      <a href="/admin/delete_blog?bid=${blog.id}" onclick="return confirm('Are you sure you want to delete?')">[ Delete ]</a>
      </input>
      <br/>
  </span><br/>
  Site Administrator: 
  <select id="adminselect" onchange="update_admin()">
      <?python
      from turboblog.model import *
      users = User.select()
      ag = Group.by_group_name("admin")
      ?>
      <option py:for="u in users" py:if="ag in u.groups" py:attrs="dict(value=u.id, selected=(u==curadmin and 'selected' or None))" >
      ${u.display_name} [${u.email_address}]
      </option>
  </select>
  <br/>
  <br/>
  <a href="#" onClick="showElement('blogCreator');">Create new blog</a>
  <br/>
  <div id="blogCreator" style="display: none;" >
      <form action="/admin/create_blog" method="POST">
          <table>
              <tr>
                  <td><label for="name">Blog name:</label></td>
                  <td><input name="name" /></td>
              </tr>
              <tr>
                  <td><label for="tagline">Blog Tagline:</label></td>
                  <td><input name="tagline" /></td>
              </tr>
              <tr>
                  <td><label for="owner">Owner:</label></td>
                      <td><select name="owner">
                              <OPTION py:for="u in User.select()" VALUE="${u.id}">${u.display_name}</OPTION>
                          </select>
                        </td>
              </tr>
          </table>
          <input type="submit"/>
      </form>
  </div>
  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>
</body>
</html>
