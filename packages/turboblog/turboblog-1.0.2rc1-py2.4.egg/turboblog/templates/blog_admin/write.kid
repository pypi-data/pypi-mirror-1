<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
    <script language="javascript" type="text/javascript" src="/static/javascript/tiny_mce/tiny_mce.js"></script>
    <script language="javascript" type="text/javascript">
tinyMCE.init({
mode : "textareas",
theme : "advanced",
plugins : "table,save,advhr,advimage,advlink,emotions,iespell,insertdatetime,preview,zoom,flash,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable",
theme_advanced_buttons3_add_before : "tablecontrols,separator",
theme_advanced_buttons3_add : "emotions,iespell,flash,advhr,separator,print,separator,ltr,rtl,separator,fullscreen",
theme_advanced_resize_horizontal : true,
theme_advanced_resizing : true,
theme_advanced_toolbar_location : "top",
theme_advanced_toolbar_align : "left",
theme_advanced_path_location : "bottom",
theme_advanced_fonts : "Arial=arial,helvetica,sans-serif;Courier New=courier new,courier,monospace",
width : "640"
});
</script>

</head>

<body>
    <div class="wrap">
            <?python
            post_title = ""
            post_content = ""
            edit = post != None
            title = "Write"
            if edit:
                title = "Edit"
                post_id = post.id
                post_title = post.title
                post_content = post.content
            ?>
        <h2 id="write-post"> ${title} Post </h2> 
        <div id="poststuff">
            <form method="POST" action="/blog_admin/new_post?bid=${blog.id}">
           <div id="moremeta">
                <fieldset style="position: relative; display: block;" id="slugdiv" class="dbx-box dbx-box-closed dbxid2">
                    <h3 title="click-down and drag to move this box" style="position: relative; display: block;" class="dbx-handle dbx-handle-cursor">Post slug <a title="click to open this box" class="dbx-toggle dbx-toggle-closed" href="javascript:void(null)" style="cursor: pointer;"> &nbsp; </a></h3>
                    <div class="dbx-content"> <input name="post_name" size="13" id="post_name" value="" type="text" /> </div>
                </fieldset>
            </div>
            <fieldset id="titlediv">
                <legend>Title</legend>
                <div> <input name="post_title" size="30" tabindex="1" value="${post_title}" id="title" type="text"/> </div>
            </fieldset>
            <fieldset id="postdivrich">
                <legend>Post</legend>
                <div>
                    <textarea style="display: none;" title="true" rows="10"  name="content" tabindex="2" id="content">${post_content}</textarea>
                </div>
            </fieldset>
            <p class="submit">
            <input name="submit" value="Save" style="font-weight: bold;" tabindex="4" type="submit"/>
            <input py:if="not edit" name="publish" id="publish" tabindex="5" accesskey="p" value="Publish" type="submit"/>
            <input py:if="edit" name="edit" id="edit" tabindex="6" accesskey="e" value="Edit" type="submit"/>
            <input py:if="edit" name="publishedit" id="publishedit" tabindex="7" accesskey="e" value="Edit and Publish" type="submit"/>
            <input py:if="edit" name="post_id" id="post_id" type="hidden" value="${post_id}"/>
            </p>
            <div style="position: relative; display: block;" id="advancedstuff" class="dbx-group">
                <fieldset style="position: relative; display: block;" class="dbx-box dbx-box-open dbxid1">
                    <h3 title="click-down and drag to move this box" style="position: relative; display: block;" class="dbx-handle dbx-handle-cursor"> Trackbacks <a title="click to close this box" class="dbx-toggle dbx-toggle-open" href="javascript:void(null)" style="cursor: pointer;"> &nbsp; </a></h3>

                    <div class="dbx-content"> Send trackbacks to: <input name="trackback_url" style="width: 415px;" id="trackback" tabindex="7" value="" type="text"/> (Separate multiple URIs with spaces) </div>

                </fieldset>

                <span style="overflow: hidden; display: block; width: 0pt; height: 0pt;" class="dbx-box dbx-dummy dbx-offdummy"> </span>
            </div>
        </form>
        </div>
   </div>
    </body>
</html>
