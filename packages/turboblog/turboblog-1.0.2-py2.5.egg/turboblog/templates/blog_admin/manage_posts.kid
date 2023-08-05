<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
      ${submenu}
 
      <div class="wrap">
          <div name="searchform" style="float: left; width: 16em; margin-right: 3em;">
              ${search_text.display_with_params(search_text, st_params)}
          </div>
          <div name="viewarc" style="float: left; width: 35em; margin-bottom: 1em;">
              ${search_date.display_with_params(search_date, sd_params)}
          </div>

          <br style="clear: both; " />
          <table id="the-list-x" cellpadding="3" cellspacing="3" width="100%">
              <tbody>
                  <tr>
                      <th scope="col">ID</th>
                      <th scope="col">When</th>
                      <th scope="col">Title</th>
                      <th scope="col">Categories</th>
                      <th scope="col">Comments</th>
                      <th scope="col">Published</th>
                      <th scope="col">Author</th>
                      <th scope="col"></th>
                      <th scope="col"></th>
                      <th scope="col"></th>
                  </tr>
                  <tr class="${i%2 and 'alternate' or ''}" py:for="i,item in enumerate(blog_posts)">
                      <th scope="row">${item.id}</th>
                      <td>${item.modification_time}</td>
                      <td>${item.title}</td>
                      <td>${len(item.tags)}</td>
                      <td>${len(item.comments)}</td>
                      <td>${item.published}</td>
                      <td>${item.author.display_name}</td>
                      <td><a href="${item.link()}">View</a></td>
                      <td><a href="${item.edit_link(blog.id,item.id)}">Edit</a></td>
                      <td><a href="${item.delete_link()}" onClick="return confirm('Are you sure you want to delete this post?');">Delete</a></td>
                  </tr>
              </tbody>
            </table>
  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>

</body>
</html>
