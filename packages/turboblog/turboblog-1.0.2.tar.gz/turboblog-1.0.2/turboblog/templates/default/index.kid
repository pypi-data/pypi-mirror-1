<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
    <head></head>
    <body>
        <div id="page">
            <header></header>
            <div id="content" class="narrowcolumn">
                <div  py:if="blog_posts.count() == 0">No post found!</div>
                <div py:strip="1" py:for="post in blog_posts">
                    <?python
                    from turbogears.identity.conditions import has_permission
                    from turboblog.model import Blog
                    blog_count = blog_posts.count()
                    can_edit = has_permission('can_post') and (tg.identity.user in blog.posters) or (tg.identity.user == blog.owner)

                    nc = 'No Comments'
                    if len(post.comments) == 1:
                        nc = '1 Comment'
                    elif len(post.comments) > 1:
                        nc = '%d Comments'%len(post.comments)
                    post_match = False
                    try:
                        ay = arc_year
                        am = arc_month
                        post_match = (post.creation_time.month == am and post.creation_time.year == ay)
                    except:
                        try:
                            a = tag_name
                            if a in post.tags:
                                post_match = True
                        except:
                            try:
                                a = untagged
                                post_match = not post.tagged()
                            except:
                                post_match = True
                    ?>
                    <span py:strip="1" py:if="post_match and post.published">
                    <div class="post" id="post-${post.id}">
                        <h2><a href="${post.link()}" rel="bookmark" title="Permanent Link to ${post.title}">${post.title}</a></h2>
                        <small>${post.creation_time}<span py:strip="1" py:if="blog_count>1"> by ${post.author.display_name}</span></small>

                        <div class="entry">${XML(post.cut_parsed(blog.id))}</div>
                        <p class="postmetadata">
                            <span py:if="len(post.tags)">
                                Posted in 
                                <span py:for="tag in post.tags">${tag.name}  </span>
                                <strong>|</strong>
                            </span>
                            <a href="${post.link()}#comments">${nc}</a>
                        </p>

                    </div>
                    </span>

                <!-- end stripped div for blog in post -->
                </div>
                <div class="navigation">
                    <?python
                        from turboblog.pager import previous_link, next_link
                    ?>
                    <div class="alignleft">${XML(previous_link(locals()))}</div>
                    <div class="alignright">${XML(next_link(locals()))}</div>
                </div>
            <!-- end narrow column -->
            </div>
            <sidebar></sidebar>
            <footer></footer>
        <!-- end page -->
        </div>
        <adminbar></adminbar>
    </body>
</html>
