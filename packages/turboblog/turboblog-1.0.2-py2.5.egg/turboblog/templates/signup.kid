<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://purl.org/kid/ns#"
    >

    <head>
        <meta content="text/html; charset=UTF-8"
        http-equiv="content-type" py:replace="''"/>
        <title>Login to TurboBlog</title>
        <link rel="stylesheet"   href="${tg.url('/static/css/register.css')}" type="text/css"/>
    </head>

    <body><div class="fixcenter">
              
        <div class="register-input page-body">
            <h2>Create Your TurboBlog Account:</h2>
            <div class="register-hint">
                Fields marked with an asterisk <span class="required-input">*</span> are required.
                <font color="red">${tg_flash}</font>
            </div>
            <div class="register-input-fixcenter">
            <form enctype="multipart/form-data" 
                action="${tg.url('/create_user')}"
                    method="POST">


                        <div class="register-input-left">
                        <div>
                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Handle:
                            </div>
                            <input type="text" name="userid"></input>
                        </div>
                        <div>
                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Email :
                            </div>
                            <input type="text" name="email"></input>

                        </div>

                        <div>
                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Password:
                            </div>

                            <input type="password" name="psw"></input>
                        </div>

                        <div>
                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Confirm:
                            </div>

                            <input type="password" name="psw2"></input>
                        </div>

                        <div>

                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Full name:
                            </div>

                            <input type="text" name="fullname"></input>
                        </div>
                        <div>
                            <div class="register-input-label">
                                <span class="required-input">*</span>
                                Enter this code:</div>
                            <img src="${tg.url('/get_antispam_image')}"/><br/>
                            <input maxlength="25" type="text" id="code" name="code" />  </div>
                    </div>
                    <div class="register-input-right">

                        <div>

                            <strong>Summary: </strong>

                            <p>

                            What should we show when people view your profile? 
                            </p>

                            <textarea name="summary"></textarea>

                        </div>

                        <div>

                            <p>
                            <strong>Upload your image!</strong>  Turboblog will show
                            your image when people check out your profile.
                            </p>


                            <input type="file" name="image"></input><br/>
                            <input type="checkbox" name="usegravatar">Fetch Image from <a href="http://www.gravatar.com">Gravatar</a></input>
                        </div>

                    </div>

                    <div class="register-submit">
                        <input type="submit" value="Sign me up baby!" />
                    </div>

                </form>
                </div>


            </div>
        </div>



        </body>
    </html>
