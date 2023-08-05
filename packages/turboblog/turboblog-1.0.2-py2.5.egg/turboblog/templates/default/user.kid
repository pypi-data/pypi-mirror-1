<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
 >
    <head>
    <script src="${tg.url('/static/javascript/editinplace.js')"></script>
    <script src="${tg.url('/static/javascript/approveinplace.js')"></script>
    <script src="${tg.url('/static/javascript/taginplace.js')"></script>
   </head>
<body>
    <pre>
        User details:<br/>
        id = ${user.user_name}
        name = ${user.display_name}
        email = ${user.email_address}
        avatar = <img py:if="user.avatar_link()" src="${user.avatar_link()}" />
    </pre>
</body>
</html>
