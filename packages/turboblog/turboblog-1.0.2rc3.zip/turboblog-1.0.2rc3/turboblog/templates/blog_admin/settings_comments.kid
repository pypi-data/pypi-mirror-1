<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
      <ul id="submenu">
          <li><a href='/blog_admin/settings_general?bid=${blog.id}'>General</a></li>
          <li><a href='/blog_admin/settings_reading?bid=${blog.id}'>Reading</a></li>
          <li><a href='/blog_admin/settings_comments?bid=${blog.id}' class="current">Comments</a></li>
      </ul>
 
    <div class="wrap">

    <h2>Comment posting Settings</h2>
    <h3>Not Yet Implemented !</h3>
    <form method="post" action="/blog_admin/update_comments_settings?bid=${blog.id}"> 
        <fieldset class="options">
            <legend>Usual settings for an article:<br /><small><em>(These settings may be overridden for individual articles.)</em></small></legend> 

            <ul> 
                <li> 
                <label for="default_pingback_flag"> 
                    <input name="default_pingback_flag" type="checkbox" id="default_pingback_flag" value="1"  checked="checked" /> 
                    Attempt to notify any Weblogs linked to from the article (slows down posting.)</label> 
                </li> 
                <li> 
                <label for="default_ping_status"> 
                    <input name="default_ping_status" type="checkbox" id="default_ping_status" value="open"  checked="checked" /> 
                    Allow link notifications from other Weblogs (pingbacks and trackbacks.)</label> 
                </li> 
                <li> 
                <label for="default_comment_status"> 
                    <input name="default_comment_status" type="checkbox" id="default_comment_status" value="open"  checked="checked" /> 
                    Allow people to post comments on the article</label> 

                </li> 
            </ul> 
        </fieldset>
        <fieldset class="options">
            <legend>E-mail me whenever:</legend> 
            <ul> 
                <li> 
                <label for="comments_notify"> 
                    <input name="comments_notify" type="checkbox" id="comments_notify" value="1"  checked="checked" /> 
                    Anyone posts a comment </label> 
                </li> 
                <li> 
                <label for="moderation_notify"> 
                    <input name="moderation_notify" type="checkbox" id="moderation_notify" value="1"  checked="checked" /> 
                    A comment is held for moderation </label> 

                </li> 
            </ul> 
        </fieldset>
        <fieldset class="options">
            <legend>Before a comment appears:</legend> 
            <ul>
                <li>
                <label for="comment_moderation"> 
                    <input name="comment_moderation" type="checkbox" id="comment_moderation" value="1"  /> 
                    An administrator must approve the comment (regardless of any matches below) </label> 
                </li> 
                <li><label for="require_name_email"><input type="checkbox" name="require_name_email" id="require_name_email" value="1"  checked="checked" /> Comment author must fill out name and e-mail</label></li> 
                <li><label for="comment_whitelist"><input type="checkbox" name="comment_whitelist" id="comment_whitelist" value="1"  /> Comment author must have a previously approved comment</label></li> 

            </ul> 
        </fieldset>
        <fieldset class="options">
            <legend>Comment Moderation</legend>
            <p>Hold a comment in the queue if it contains more than <input name="comment_max_links" type="text" id="comment_max_links" size="3" value="2" /> links. (A common characteristic of comment spam is a large number of hyperlinks.)</p>

            <p>When a comment contains any of these words in its content, name, URI, e-mail, or IP, hold it in the moderation queue: (Separate multiple words with new lines.) <a href="http://codex.wordpress.org/Spam_Words">Common spam words</a>.</p>
            <p> 
            <textarea name="moderation_keys" cols="60" rows="4" id="moderation_keys" style="width: 98%; font-size: 12px;" class="code"></textarea> 

            </p> 
            <p>
            <!--
            <a id="retrospambutton" href="options-discussion.php?action=retrospam">Check past comments against moderation list</a>
            -->
            </p> 
        </fieldset>
        <fieldset class="options">
            <legend>Comment Blacklist</legend>
            <p>This is a list of words that you want completely blacklisted from your blog. Be very careful what you add here, because if a comment matches something here it will be completely nuked and there will be no notification. Remember that partial words can match, so if there is any chance something here might match it would be better to put it in the moderation box above.</p>
            <p> 
            <textarea name="blacklist_keys" cols="60" rows="4" id="blacklist_keys" style="width: 98%; font-size: 12px;" class="code"></textarea> 
            </p>
            <p><label for="open_proxy_check"> 
                <input name="open_proxy_check" type="checkbox" id="open_proxy_check" value="1"  checked="checked" /> 

                Blacklist comments from open and insecure proxies.</label></p>
        </fieldset>
        <p class="submit">
        <input type="submit" name="Submit" value="Update Options" /> 
        </p> 
    </form> 

  <div style="clear: both">&nbsp;
      <br clear="all" />
  </div>
      </div>
</body>
</html>
