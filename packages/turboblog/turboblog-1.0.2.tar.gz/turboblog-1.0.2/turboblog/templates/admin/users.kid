<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title></title>
    <script>

    var hideAll = function () {
        hideElement("userEditor");
        hideElement("userCreator");
        hideElement("message");
    };
function prepareUserQuery(form,k,v){
            var params = [ 'fullname','email','psw','psw2','groups'];
            var e = getElement(form);
            var ps = [];
            for (pcheck in keys(e.groups))
            {
            if (e.groups[pcheck])
            if (e.groups[pcheck].checked){
                 ps.push(e.groups[pcheck].value);
                }
            }
            var pardata = [ e.fullname.value, e.email.value, e.psw.value, e.psw2.value , ps ];
            params.push(k);
            pardata.push(v);
            var q = queryString(params,pardata);
            return q;
}
addLoadEvent(hideAll);
function editUser(uid){
    showElement("userEditor");
    hideElement("userCreator");
    hideElement("message");
    var d = loadJSONDoc("/admin/user_info/"+uid);
    d.addCallbacks(function(udata){
            data = udata["user"];
            var sb = INPUT({"type":"submit","value":"Commit changes"});
            sb.onclick = function () {
            var qstring = prepareUserQuery("userEditorForm",'uid',data.id);
                var d = loadJSONDoc("/admin/user_update?"+qstring);
                d.addCallbacks(function (){
                    hideElement("userEditor");
                    replaceChildNodes("message", "Updated!");
                    showElement("message");
                    },
                    function (){
                    hideElement("userEditor");
                    replaceChildNodes("message", "Updated failed!");
                    showElement("message");
                    });
                };            
            var allgroups = udata['allgroup'];
            opt = []
            for(group in allgroups){
            zl = LABEL({"for":group},allgroups[group]['desc']);
            iparam = {
                       "value":group,
                       "type":"checkbox",
                       "name":"groups"
            };
            forEach (data['groups'],function (z){
                if (z == group){
                    iparam['checked'] = 1;
                }
            });
            z = INPUT(iparam,group);
            opt.push( TR({}, TD({},z) , TD({},zl))); 
            }
            var form = DIV({},FORM({"name":"userEditorForm","id":"userEditorForm"},
                TABLE({},
                    TR({},TD({},"Edititing user:"),TD({},data["userId"])),
                    TR({},
                       TD({},LABEL({"for":"fullname"},"Full name:")),
                       TD({},INPUT({"type":"text","name":"fullname","value":data["display_name"]}))),
                    TR({},
                       TD({},LABEL({"for":"email"},"Email:")),
                       TD({},INPUT({"type":"text","name":"email","value":data["email_address"]}))),
                    TR({},
                       TD({},LABEL({"for":"psw"},"Password:")),
                       TD({},INPUT({"type":"password","name":"psw","value":data["password"]}))),
                    TR({},
                       TD({},LABEL({"for":"psw2"},"Confirm Password:")),
                       TD({},INPUT({"type":"password","name":"psw2","value":data["password"]})))
                    ),
                opt),sb);
    replaceChildNodes("userEditor",form);
    });

}
function addUser(){
    hideElement("userEditor");
    hideElement("message");
    showElement("userCreator");
}
function deleteUser(uid){
    if (confirm('Are you sure you want to delete?')){
    var d = loadJSONDoc("/admin/user_delete?uid="+uid);
    d.addCallbacks(function (data){                    
    forEach(getElement('usersList').childNodes, 
            function(e) {
            if(e.id == 'li_id'+uid){
               getElement('usersList').removeChild(e);
             }
            }
        );
    },function(){ alert('Cannot delete!'); }
    );
    }
}
function addNewUser(){
        var qstring = prepareUserQuery("newUserForm",'login',getElement('newUserForm').login.value);
        var d = loadJSONDoc("/admin/user_create?"+qstring);
        d.addCallbacks(function (data){
                hideElement("userCreator");
                replaceChildNodes("message", "Created!");
                showElement("message");
                a = A({'href':'#'},data['display_name']);
                a.onclick = function () { editUser(data['userId']); };
                a2 = A({'href':'#'},'[ Delete ]');
                a2.onclick = function () { deleteUser(data['userId']); };
                getElement('usersList').appendChild( LI({'id':'li_id'+data['userId']}, a, " ", a2));
                },
                function (){
                hideElement("userCreator");
                replaceChildNodes("message", "Create failed!");
                showElement("message");
                });
    }

    </script>
</head>

<body>
    <div class="wrap">

        <h2>User managment</h2>

        <h3>These are the members of your blog:</h3>
        <table border="1"><tr>
                <td width="10%">
                    <a onClick="addUser();" href="#">Add new user</a>
                    <ol id='usersList'>
                        <li py:for="u in users" id="li_id${u.id}">
                        <a onClick="editUser(${u.id});" href="#">${u.display_name}</a>  
                        <a onClick="deleteUser(${u.id});" href="#">[ Delete ]</a>
                        </li>
                    </ol>
                </td>
                <td width="90%">
                    <div id="userEditor" />
                        <div id="userCreator">
                            <form id="newUserForm">
                                Create new user:<br/>
                                <table><tr>
                                        <td><label for="login">Login:</label></td>
                                        <td><input type="text" name="login" /></td>
                                    </tr>
                                    <tr>
                                        <td><label for="fullname">Full name:</label></td>
                                        <td><input type="text" name="fullname" /></td>
                                    </tr>
                                    <tr>
                                        <td><label for="psw">Password:</label></td>
                                        <td><input type="password" name="psw" /></td>
                                    </tr>
                                    <tr>
                                        <td><label for="psw2">Confirm Password:</label></td>
                                        <td><input type="password" name="psw2" /></td>
                                    </tr>
                                    <tr>
                                        <td><label for="email">Email:</label></td>
                                        <td><input type="text" name="email" /></td>
                                    </tr>
                                    <tr py:for="group in groups">
                                        <td><label for="p1">${group.display_name}</label></td>
                                        <td><input type="checkbox" name="groups" value="${group.group_name}" /></td>
                                    </tr>
 
                                </table>
                            </form>
                            <div id="submit">
                                <input onClick="addNewUser();" type="submit" value="Create!" />
                            </div>
                        </div>
                    <div id="message" />
                </td>
            </tr>
        </table>
        <div style="clear: both">&nbsp;
            <br clear="all" />
        </div>
    </div>
</body>
</html>
