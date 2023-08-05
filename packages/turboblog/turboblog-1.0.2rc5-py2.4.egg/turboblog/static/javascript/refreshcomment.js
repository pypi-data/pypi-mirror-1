//
// a small helper for the comments edition with submodal
// author: Florent AIDE, <florent.aide@gmail.com>
// date: March 6th, 2007
//

function shownewvalue(result) {
	var new_value = result["comment_content"];
	getElement("commentp-" + result["comment_id"]).innerHTML = new_value;
}

function refreshcomment() {
	var myuri = document.refreshuri;
    var d = loadJSONDoc(myuri);
	d.addCallback(shownewvalue);
}

function refresh() {
    // this function is just a hack because
    // if I put directly refreshcomment as my
    // callback in showPopWin it does not work
    // I don't know why this was just an instinct
    // to add this intermediate function
    var d = callLater(0, refreshcomment)
}

function showmymodal(url, width, height, refreshuri) {
    document.refreshuri = refreshuri;
    showPopWin(url, width, height, refresh);
}

