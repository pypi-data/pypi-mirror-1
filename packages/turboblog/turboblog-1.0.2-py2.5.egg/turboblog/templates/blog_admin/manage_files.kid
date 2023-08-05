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
          <h2>Files ( <a href="${tg.url('/blog_admin/add_file?bid=%s' % bid)}"> add new </a> )</h2>
          <br style="clear: both; " />
          <table id="the-list-x" cellpadding="3" cellspacing="3" width="100%">                    
              <tbody>
                  <tr>                            
                      <th scope="col">ID</th>
                      <th scope="col">Name</th>
                      <th scope="col">Display URL</th>
                      <th scope="col">Download URL</th>
                      <th scope="col">Actions</th>
                  </tr>
                  <tr class="${i%2 and 'alternate' or ''}" py:for="i,item in enumerate(files)">
                      <th scope="row">${item.id}</th>
                      <td>${item.filename}</td>
                      <td>
                          <a href="${tg.url('/show_file?bid=%s;file_id=%s' % (bid, item.id))}"
                              target="_blank">${tg.url('/show_file?bid=%s;file_id=%s' % (bid, item.id))}</a>
                      </td>

                      <td><a href="${tg.url('/download_file?bid=%s;file_id=%s' % (bid, item.id))}"
                              >${tg.url('/download_file?bid=%s;file_id=%s' % (bid, item.id))}</a>
                      </td>

                      <td><a href="${tg.url('/blog_admin/delete_file?bid=%s;file_id=%s' % (bid, item.id))}"
                              onclick="return confirm('You are about to delete the file ${item.filename}.' );" class="delete">Delete</a></td>
                  </tr>
              </tbody>
          </table>
      </div>
      <div class="wrap">
          <p>
          <strong> Note: </strong>
          <br/> Deleting a file may cripple some of your posts that refer to it. Make sure you know what you are doing
          </p>
      </div>


</body>
</html>
