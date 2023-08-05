<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <link href="${tg.url('/static/css/admin.css')}" type="text/css" rel="stylesheet" />
    <title></title>
</head>

<body>
     <div class="wrap">
         <h2 id="edit_comment_title"> Edit Comment </h2> 
         <div id="commentstuff">
             ${form.display_with_params(form, params)}
         </div>
    </div>
</body>
</html>
