
function tag(postid, field, slug ){    
    if ($(field).selectedIndex != 0){
    tagname = $(field).options[$(field).selectedIndex].value;
    var url = '/'+slug+'/tag_post/'+escape(tagname)+'/'+postid;
    var d = loadJSONDoc(url);
    d.addCallbacks(function (data){ 
        $(field).remove($(field).selectedIndex); 
        $('taglist').innerHTML += " "+tagname;
    } ); }
}

