<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>
<script type="text/javascript">
<!--
function checkAll(form)
{
    for (i = 0, n = form.elements.length; i < n; i++) {
        if(form.elements[i].type == "checkbox") {
            if(form.elements[i].checked == true)
                form.elements[i].checked = false;
            else
                form.elements[i].checked = true;
        }
    }
}
//-->
</script>
<body>
      <ul id="submenu">
          <li><a href="${tg.url('/blog_admin/manage_posts?bid=%s' % blog.id)}" >Posts</a></li>
          <li><a href="${tg.url('/blog_admin/manage_comments?bid=%s' % blog.id)}" class="current">Comments</a></li>
          <li><a href="${tg.url('/blog_admin/manage_tags?bid=%s' % blog.id)}">Tags</a></li>
      </ul>

      <div class="wrap">
          <form name="searchform" action="${tg.url('/blog_admin/manage_comments')}" method="get" style="float: left; width: 16em; margin-right: 3em;">
              <fieldset>
                  <legend> Search Comments... </legend>
                  <input name="bid" value="${blog.id}" type="hidden"/>
                  <input name="s" value="" size="17" type="text"/>
                  <input name="submit" value="Search" type="submit"/>
              </fieldset>
          </form>
          <form name="viewarc" action="" method="get" style="float: left; width: 20em; margin-bottom: 1em;">
              <fieldset>
                  <legend> Browse Month... </legend>
                  <select name="m">
                      <option value="200511"> November 2005 </option>
                  </select>
                  <input name="submit" value="Show Month" type="submit"/>
               </fieldset>
           </form>

          <br style="clear: both; " />
          <p><a href="?bid=${blog.id};mode=view">View Mode</a> | <a href="?bid=${blog.id};mode=mass">Mass Edit Mode</a></p>
          <?python
          from turboblog.model import Blog
          try:
            mass = int(mass)
          except:
            mass = 0          
          ?>
          <ol py:if="not mass" id='the-list' class='commentlist'>
              <li class='${i%2 and "alternate" or ""}' py:for="i, comment in enumerate(blog_comments)" id='comment-${comment.id}' >        
              <p>
              <strong>Name:</strong> ${comment.author.display_name} | <strong>E-mail:</strong>
              <a href="mailto:${comment.author.email_address}">${comment.author.email_address}</a> </p>
              <p>${comment.content}</p>

              <p>Posted ${comment.creation_time} | <a href="#">Edit Comment</a>
              | <a href="${comment.delete_link()}" onclick="return confirm( 'You are about to delete this comment?. Cancel to stop, OK to delete.' );">Delete Comment</a>
              &#8212;  <a href="${comment.post.edit_link(blog.id, comment.post.id)}">Edit Post : ${comment.post.title}</a>
              | <a href="${comment.post.link()}">View Post</a></p>

              </li>
          </ol>
          <form name="deletecomments" id="deletecomments" action="/blog_admin/delete_comments?bid=${blog.id}" method="post" py:if="mass"> 
          <table id="the-list-x" cellpadding="3" cellspacing="3" width="100%"> 
              <tbody>
                  <tr>                            
                      <th scope="col">*</th>
                      <th scope="col">ID</th>
                      <th scope="col">When</th>                        
                      <th scope="col">Email</th>                                                    
                      <th scope="col">Comment Excerpt</th>
                      <th scope="col">Actions</th>
                  </tr>
                  <tr class="${i%2 and 'alternate' or ''}" py:for="i, item in enumerate(blog_comments)">
                      <td><input type="checkbox" name="delete_comments[]" value="${item.id}" /></td>
                      <td>${item.id}</td>
                      <td>${item.creation_time}</td>
                      <td>${item.author.email_address}</td>
                      <td>${item.content[:100]}</td>
                      <td><a href="${item.link()}">View</a></td>
                      <td><a href="${item.edit_link()}">Edit</a></td>
                      <td><a href="${item.delete_link()}" onClick="return confirm('Are you sure you want to delete this comment?');">Delete</a></td>
                  </tr>
              </tbody>
          </table>
          <p><a href="javascript:;" onclick="checkAll(document.getElementById('deletecomments')); return false; ">Invert Checkbox Selection</a></p>
          <p class="submit">
          <input type="submit" name="Submit" value="Delete Checked Comments &raquo;" onclick="return confirm('You are about to delete these comments permanently \n  \'Cancel\' to stop, \'OK\' to delete.')" />  </p>
      </form>
  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>

</body>
</html>
