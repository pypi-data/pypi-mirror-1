
function approve(id,slug){    
    aid = "comment_"+id+"_approval";
    $(aid).innerHTML = "Approving...";
    var url = '/'+slug+'/comment/approve/'+id;
    var d = loadJSONDoc(url);
    d.addCallbacks(
            function (data){ removeElement(aid); },
            function (data){ $(aid).innerHTML = "Approval Failed!"; }
            );
}
function displayStatusMessage(status, msg) {

    swapDOM("statusmessage", DIV({'id': 'statusmessage'}, DIV({'class': status}, msg)));

    callLater(5, swapDOM, "statusmessage", DIV({'id': 'statusmessage'}, null));

}
function saveHandler(result) {

    data = evalJSONRequest(result);

    if (data['status'] == "success") {

        displayStatusMessage(data['status'], data['msg']);
        getElement('articleId').value = data['id'];

    } else {
        if(data['status'] == "error") {
            displayStatusMessage(data['status'], data['msg']);
        } else {
            displayStatusMessage('fatal', 'There was an unknown error!');
        }
    }
}
