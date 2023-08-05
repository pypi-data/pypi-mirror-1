<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
</head>

<body>
     <div class="wrap">
         <h2 id="write-post"> Post </h2> 
         <div id="poststuff">
             ${writepost_form.display_with_params(writepost_form, params)}
         </div>
    </div>
</body>
</html>
