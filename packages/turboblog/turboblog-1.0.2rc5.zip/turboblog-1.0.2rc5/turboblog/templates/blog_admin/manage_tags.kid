<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

    <head>
<script type="text/javascript">
<!--
function addtag(bid){
    t = prompt("please enter tag name:");
    if(t){
        window.location="/blog_admin/add_tag?bid="+bid+";tag="+t;
    }
}
function changetag(bid,tid){
    t = prompt("please enter new tag name:");
    if(t){
        window.location="/blog_admin/rename_tag?bid="+bid+";tag="+t+";tid="+tid;
    }
}

//-->
</script>

    <title></title>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
</head>

<body>
      ${submenu} 

      <div class="wrap">
          <h2>Tags ( <a href="#" onClick="return addtag(${blog.id});"> add new </a> )</h2>
          <br style="clear: both; " />
          <table id="the-list-x" cellpadding="3" cellspacing="3" width="100%">                    
              <tbody>
                  <tr>                            
                      <th scope="col">ID</th>
                      <th scope="col">Name</th>                        
                      <th scope="col">Actions</th>
                  </tr>
                  <tr class="${i%2 and 'alternate' or ''}" py:for="i,item in enumerate(blog.tags)">
                      <th scope="row">${item.id}</th>
                      <td>${item.name}</td>
                      <td><a href="#" onClick="return changetag(${blog.id},${item.id});">Edit</a></td>
                      <td><a href="/blog_admin/delete_tag?bid=${blog.id};tid=${item.id}"
                              onclick="return confirm('You are about to delete the tag ${item.name}.  All of its posts will go as Untagged.OK to delete, Cancel to stop.' );" class="delete">Delete</a></td>
                  </tr>
              </tbody>
          </table>
      </div>
      <div class="wrap">
          <p>
          <strong> Note: </strong>
          <br/> Deleting a category does not delete posts from that category, it will just set them back to the default category
          <strong> Untagged </strong>
          . </p>
      </div>
      

</body>
</html>
