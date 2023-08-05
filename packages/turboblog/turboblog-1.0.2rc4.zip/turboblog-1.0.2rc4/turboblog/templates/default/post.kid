<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
    <head>
        <script src="/static/javascript/editinplace.js"></script>
        <script src="/static/javascript/approveinplace.js"></script>
        <script src="/static/javascript/taginplace.js"></script>
        <script>
        function reply(cid,slug){
            p = getElement('commentform').cloneNode(true);
            p.comment_id.value = cid;
            e = getElement('comment-'+cid);
            eh = getElement('replylink-'+cid);
            hideElement(eh);
            appendChildNodes(e.parentNode,p);
        }
        </script>
   </head>
    <body>
        <div id="page">

            <header></header>
	<div id="content" class="narrowcolumn">

		<div class="post" id="post-${post.id}">
		<h2>${post.title}</h2>
			<div class="entrytext">${XML(post.content)}</div>
                    </div>
<?python
from turboblog.pager import previous_link,next_link
nc = 'No Responses'
if len(post.comments) == 1:
    nc = 'One Response'
elif len(post.comments) > 1:
    nc = '%d Responses'%len(post.comments)
from turbogears.identity.conditions import has_permission
from turboblog.model import Comment,Tag
registered = has_permission('can_comment')    
can_edit = has_permission('can_post')    
if registered:
    from turboblog.model import User
    calink = User.get(tg.identity.user.id).link() 
more_tags = []    
for tag in blog.tags:
    if not tag in post.tags:
        more_tags += [ tag ]
?>
 <span id="taglist" py:if="len(post.tags)">
                    Posted in <span py:for="tag in post.tags">${tag.name}</span>
                </span>
   
        <span py:strip="1" py:if="can_edit">
                    |
        <a href="javascript: tag(${post.id}, 'tag_selector', '${blog.slug}');">Add Tag:</a>
        <select id="tag_selector">
            <option id="tag_none">Untagged</option>
            <option py:for="tag in more_tags" id="tag_${tag.id}">${tag.name}</option>
        </select>
    </span>


<a name="comments"></a>
<h3 id="comments">${nc} to "${post.title}"</h3> 
${post.generate_comments_html()}


    <h3 py:if="len(post.trackbacks)" id="trackbacks">Trackbacks</h3>
    <ol class="commentlist">
        <li  py:for="i, tb in enumerate(post.trackbacks)"
                            class="${i%2 and 'alt' or ''}" id="tb-${tb.id}">
                            <cite py:if="tb.blog_name != ''">from ${tb.blog_name}</cite><br/>
                            <em py:if="tb.title != ''"><a href="${tb.url}">${tb.title}</a></em><br/>
        <span py:if="tb.excerpt">
            ${XML(tb.excerpt)}
        </span>
        </li>
    </ol>

   <h3 id="respond">Leave a Reply</h3>
   <div py:if="not registered">
        <p>You must be <a href="/login">logged in</a> to post a comment.</p>
    </div>
    <div py:if="registered">

        <form action="${Comment.link_add(blog.id,post.id)}" method="post" id="commentform">

            <p>Logged in as <a href="${calink}">${tg.identity.user.display_name}</a>. 
            <a href="${tg.url('/logout')}" title="Log out of this account">Logout &raquo;</a></p>

            <input name="comment_id" type="hidden" value="-1" />
            <p><small><strong>XHTML:</strong> You can use these tags: 
                [ 
                <span py:for="at in Comment.allowed_tags">${at[0]} </span>
             ]</small></p>

            <p><textarea name="comment" id="comment" cols="100%" rows="10" tabindex="4"></textarea></p>

            <p><input name="submit" type="submit" id="submit" tabindex="5" value="Submit Comment" />
            </p>

        </form>
    </div>
    <br/>
    To send a trackback, use <a href="${post.trackback_link()}">this url</a>.
</div>
    <sidebar></sidebar>
    <footer></footer>
</div>
<adminbar></adminbar>
</body>
</html>

