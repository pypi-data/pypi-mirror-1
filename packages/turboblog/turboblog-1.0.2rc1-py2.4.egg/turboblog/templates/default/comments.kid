<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns:py="http://purl.org/kid/ns#">
<body py:strip="1" py:match="item.tag=='{http://www.w3.org/1999/xhtml}comments'">
    <h3 id="comments">
        ${comments_number('No Responses', 'One Response', '% Responses' )} to &#8220; ${post.title} &#8221;
    </h3> 

    <ol class="commentlist">
        <li  py:for="comment in post.comments"  class="oddcomment" id="comment-${comment.id}">
        <cite>${comment.author.link()}</cite> Says:
        <div py:if="not comment.approved">
            <em>Your comment is awaiting moderation.</em>
        </div>
        <br />

        <small class="commentmetadata">
            at ${comment.creation_time}
            ${edit_comment_link('e','','')}
        </small>

        ${comment.content}

        </li>
    </ol>



    <h3 id="respond">Leave a Reply</h3>

    <div py:if="not registered()">
        <p>You must be <a href="/login?redirect_to">logged in</a> to post a comment.</p>
    </div>
    <div py:if="registered()">

        <form action="/add_comment" method="post" id="commentform">

            <p>Logged in as <a href="${tg.identity.current.link()}">${tg.identity.current}</a>. 
            <a href="${tg.url('/logout')}" title="Log out of this account">Logout &raquo;</a></p>


            <p><small><strong>XHTML:</strong> You can use these tags: ${allowed_tags()}</small></p>

            <p><textarea name="comment" id="comment" cols="100%" rows="10" tabindex="4"></textarea></p>

            <p><input name="submit" type="submit" id="submit" tabindex="5" value="Submit Comment" />
            </p>

        </form>
    </div>
</body>
</html>
