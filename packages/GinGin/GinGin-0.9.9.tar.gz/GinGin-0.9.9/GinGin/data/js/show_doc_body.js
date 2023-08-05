function init_body() {
    var data = "";
    var parser = new gindoc_parser(gingin_url + "/show_kw_docs/", gingin_url + "/get_afile/" + doc_id + "/");
    var i;
    
    data = rawbody.value;
    
    body.removeChild(rawbody);
    body.innerHTML = parser.show_msg(data);
    body.className = "text";
}

init_funcs.push(init_body);
