<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
      <ul id="submenu">
          <li><a href="${tg.url('/blog_admin/settings_general?bid=%s' % blog.id)}">General</a></li>
          <li><a href="/${tg.url('blog_admin/settings_reading?bid=%s' % blog.id)}" class="current">Reading</a></li>
          <li><a href="/${tg.url('blog_admin/settings_comments?bid=%s' % blog.id)}">Comments</a></li>
      </ul>
 
    <div class="wrap">

        <h2>Blog Reading Settings</h2>
        <h3>Not yet implemented!</h3>
        <form name="form1" method="post" action="/blog_admin/update_read_settings?bid=${blog.id}">
            <fieldset class="options">
                <legend>Blog Pages</legend>

                <table width="100%" cellspacing="2" cellpadding="5" class="editform">
                    <tr valign="top">
                        <th width="33%" scope="row">Show at most:</th>
                        <td>
                            <input name="posts_per_page" type="text" id="posts_per_page" value="${posts_per_page}" size="3" /> Posts per page.
                        </td>
                    </tr>
                </table>
            </fieldset>

            <fieldset class="options">

                <legend>Syndication Feeds</legend>
                <table width="100%" cellspacing="2" cellpadding="5" class="editform">
                    <tr valign="top">
                        <th width="33%" scope="row">Show the most recent:</th>
                        <td><input name="posts_per_rss" type="text" id="posts_per_rss" value="${posts_per_rss}" size="3" /> posts</td>
                    </tr>
                    <tr valign="top">
                        <th scope="row">For each article, show: </th>
                        <td py:if="not rss_summary">
                            <label><input name="rss_use_excerpt"  type="radio" value="0" checked="checked" /> Full text</label><br />

                            <label><input name="rss_use_excerpt" type="radio" value="1" /> Summary</label>
                        </td>
                        <td py:if="rss_summary">
                            <label><input name="rss_use_excerpt"  type="radio" value="0" /> Full text</label><br />

                            <label><input name="rss_use_excerpt" type="radio" value="1" checked="checked" /> Summary</label>
                        </td>
                    </tr>
                </table>
            </fieldset>
            <p class="submit">
            <input type="submit" name="Submit" value="Update Options &raquo;" />
            </p>
        </form>


  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>
</body>
</html>
