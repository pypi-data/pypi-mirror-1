<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://purl.org/kid/ns#">

<div class="LSRes">
    <p py:if="blog_posts is None">No results found for this search</p>
    <span py:if="blog_posts is not None" py:strip="True">
    <span py:for="post in blog_posts" py:strip="True">
    <div class="LSRow">
        <a href="${post.link()}" rel="bookmark" title="Permanent Link: ${post.title}">${post.title}</a>
    </div>
    </span>
    </span>
</div>
<div class="LSRes">
    <!--
    <a href="/index.php?s=conv">More Results...</a>
    -->
</div>

</html>
