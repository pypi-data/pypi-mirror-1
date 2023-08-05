<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

    <head>
    <title></title>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
</head>

<body>
      ${submenu}
 
      <div class="wrap">
          ${file_upload_form.display_with_params(file_upload_form, params)}
      </div>
      

</body>
</html>
