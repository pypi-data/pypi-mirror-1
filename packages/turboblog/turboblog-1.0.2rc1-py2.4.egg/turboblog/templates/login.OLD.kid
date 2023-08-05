<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://purl.org/kid/ns#"
    >

    <head>
        <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
        <title>Login to TurboBlog</title>
        <link rel="stylesheet" href="/static/css/admin.css" type="text/css" />
        <script type="text/javascript">
            function focusit() {
                document.getElementById('log').focus();
            }
window.onload = focusit;
</script>
    </head>

    <body>
        <div id="login">
            <h1>Welcome to TurboBlog</h1>
            <form name="loginform" id="loginform" action="${previous_url}" method="post">
                ${message}
                <p><label>Username:<br /><input type="text" name="user_name" id="log" size="20" tabindex="1" /></label></p>
                <p><label>Password:<br /> <input type="password" name="password" id="pwd" value="" size="20" tabindex="2" /></label></p>
                <p class="submit">
                <input type="submit" name="submit" id="submit" value="Login &raquo;" tabindex="4" />
                </p>
            </form>
            <ul>
                <li><a href="${previous_url}" title="Are you lost?">&laquo; Back to blog</a></li>
                <li><a href="/lostpassword" title="Password Lost and Found">Lost your password?</a></li>
                <li><a href="/signup" title="New Here?">Sign Up!</a></li>
            </ul>
        </div>
        
    </body>
</html>
