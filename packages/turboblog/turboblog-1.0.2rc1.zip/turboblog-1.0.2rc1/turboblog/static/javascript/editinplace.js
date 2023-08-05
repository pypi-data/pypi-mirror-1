
function makeEditable(id, blogslug){
    var cid =  id.slice(id.indexOf('_')+1,id.lastIndexOf('_'));
    var url = "/"+blogslug+"/comment/source/"+cid;
    var d = loadJSONDoc(url);
    d.addCallbacks(function (data){ edit(id,data['content'],blogslug); } );
}

function edit(obj,src, slug){
    hideElement(obj);
    var params = "'"+obj+"','"+slug+"'";
    var newdiv = DIV({'id':  obj + '_editor'},
    TEXTAREA({'id': obj + '_edit', 'name': obj, 'rows':"4", 'cols':"60"}, src),
    INPUT({'id':obj + '_save', 'type':'button', 'value':"SAVE",'onclick':'saveChanges('+params+')'}),
    " OR ",
    INPUT({'id':obj + '_cancel', 'type':'button', 'value':"CANCEL",'onclick':'cleanUp('+params+')'})
    );
    appendChildNodes(obj+"_holder", newdiv);
}

function cleanUp(obj, keepEditable){
    removeElement(obj+'_editor');
    showElement(obj);
}

function saveChanges(obj, slug){
    var new_content = escape($(obj+'_edit').value);

    $(obj).innerHTML = "Saving...";
    cleanUp(obj, true);

    var url = '/'+slug+'/comment/edit/' + obj.slice(obj.indexOf('_')+1,obj.lastIndexOf('_'))
     + '?content=' + new_content;
    var d = loadJSONDoc(url);
    d.addCallbacks(function (data){ editComplete(data, obj, new_content); }, function (data){editFailed(data,obj);});
}

function editComplete(data,objid,content){
    obj=$(objid);
    obj.innerHTML = unescape(content);
    showAsEditable(obj.id, true);
}

function editFailed(data,objid){
    obj=$(objid);
    obj.innerHTML = 'Sorry, the update failed.';
    cleanUp(objid);
}
