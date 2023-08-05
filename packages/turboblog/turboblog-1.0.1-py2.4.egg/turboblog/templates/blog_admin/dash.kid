<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
     <div class="wrap">

          <h2>Dashboard</h2>

          <div id="zeitgeist">
              <h2>Latest Activity</h2>
              <div>
                  <h3>Comments <a href="/admin/comments" title="More comments...">&raquo;</a></h3>
              </div>
              <ul>
                  <?python 
                  from turboblog.model import Comment, Post, Tag
                  ?>
                  <li py:for="c in Comment.get_last(3, blog.id)">${c.author.display_name} on <a href="${c.post.link()}">${c.post.title}</a> <small>(<a href="${c.edit_link()}">Edit</a>)</small>
                  </li>
              </ul>

              <div>
                  <h3>Posts <a href="/admin/posts" title="More posts...">&raquo;</a></h3>
                  <ul>
                      <li py:for="p in Post.get_last(3, blog.id)"><a href='${Post.edit_link(p.blog.id, p.id)}'>${p.title}</a></li>
                  </ul>
              </div>
      
      <div>
          <h3>Blog Stats</h3>
          <p>There are currently ${len(blog.posts)} <a href="/blog_admin/manage_posts?bid=${blog.id}" title="Posts">posts</a> and ${blog.get_comments().count()} <a href="/blog_admin/manage_comments?bid=${blog.id}" title="Comments">comments</a>, tagged by ${len(blog.tags)} <a href="/blog_admin/manage_tags?bid=${blog.id}" title="tags">tags</a>.</p>

      </div>

  </div>

  <h3>Welcome to your TurboBlog</h3>

  <p>Use these links to get started:</p>
  <ul>
  </ul>
  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>
</body>
</html>
