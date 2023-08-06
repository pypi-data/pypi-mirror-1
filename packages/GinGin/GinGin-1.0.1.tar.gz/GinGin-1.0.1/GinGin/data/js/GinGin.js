function show_hot_kws() {
	 var i;
	 
	 document.write("重要關鍵字(" + new String(hot_kws.length) + ")\n<ul>\n");
	 for(i = 0; i < hot_kws.length; i++) {
	       kw = hot_kws[i];
	       document.write("<li><a href=\"" + gingin_url + "/show_kw_docs/"
			+ kw[0] + "\">" + kw[0] + " (" + kw[1] + ")</a></li>\n");
	 }
	 document.write("</ul>\n<a href=" + gingin_url + "/show_all_kws>所有關鍵字</a>");
}

/* -------------------------------------------------------------------
 * Draw box
 */
function draw_box_top(img_url) {
	 document.write("<tr>\n");
	 document.write("<td><img src=\"" + img_url + "luc.jpg\"></td>\n");
	 document.write("<td background=\"" + img_url + "ub.jpg\"></td>\n");
	 document.write("<td><img src=\"" + img_url + "ruc.jpg\"></td>\n");
	 document.write("</tr>\n");
}

function draw_box_buttom(img_url) {
	 document.write("<tr>\n");
	 document.write("<td><img src=\"" + img_url + "lbc.jpg\"></td>\n");
	 document.write("<td style=\"background-repeat: repeat-x;\" background=\"" + img_url + "bb.jpg\"></td><td><img src=\"" + img_url + "rbc.jpg\"></td>\n");
	 document.write("</tr>\n");
}

function draw_bar_head(name, img_url) {
	 document.write("<table cellpadding=0 cellspacing=0 id=\"" + name + "\">\n");
	 draw_box_top(img_url);
	 document.write("<tr>\n");
	 document.write("<td style=\"background-repeat: repeat-x;\" background=\"" + img_url + "bg.jpg\"></td>\n");
	 document.write("<td width=100% style=\"background-repeat: repeat-x;\" background=\"" + img_url + "bg.jpg\">");
}

function draw_bar_tail(img_url) {
	 document.write("</td>\n");
	 document.write("<td style=\"background-repeat: repeat-x;\" background=\"" + img_url + "bg.jpg\"></td>\n");
	 document.write("</tr>\n");
	 draw_box_buttom(img_url);
	 document.write("</table>\n");
}

function draw_box_head(name, img_url) {
	 document.write("<table cellpadding=0 cellspacing=0 id=\"" + name + "\">\n");
	 draw_box_top(img_url);
	 document.write("<tr>\n");
	 document.write("<td style=\"background-repeat: repeat-y;\" background=\"" + img_url + "lb.jpg\"></td>\n");
	 document.write("<td width=100%>");
}

function draw_box_tail(img_url) {
	 document.write("</td>\n");
	 document.write("<td style=\"background-repeat: repeat-y;\" background=\"" + img_url + "rb.jpg\"></td>\n");
	 document.write("</tr>\n");
	 draw_box_buttom(img_url);
	 document.write("</table>\n");
}

/* ---------------- End of draw box ------------------------------------ */

function left_bar() {
	 var base_url = gingin_url.substring(0, gingin_url.length - 13);
	 var img_url = base_url + "images/green_bar/";

	 document.write("<div id=left_bar>\n");

	 draw_bar_head("last_docs", img_url);
	 show_last_docs();
	 draw_bar_tail(img_url);

	 draw_bar_head("hot_kws", img_url);
	 show_hot_kws();
	 draw_bar_tail(img_url);

	 document.write("</div> <!-- left_bar -->\n");
}

function edit() {
	window.location.href = gingin_url + "/edit_id_doc/" +
			new String(doc_id);
}

function new_doc() {
	window.location.href = gingin_url + "/new_doc";
}

function query(kw) {
	window.location.href = gingin_url + "/show_kw_docs/" +
		kw;
}

function all_kws() {
	window.location.href = gingin_url + "/show_all_kws";
}

function show_afiles() {
	window.location.href = gingin_url + "/show_afiles/" +
		new String(doc_id);
}

function show_edit_comment() {
    if(doc_id > 0) {
	window.location.href = gingin_url + "/edit_comment/" +
	    new String(doc_id);
    } else {
	alert("This page is not allowed to leavel comments.");
    }
}

function open_trackback (c) {
    window.open(c,
                    'trackback',
                    'width=480,height=480,scrollbars=yes,status=yes');
}

function del_afile(afkey) {
	var o;

	o = document.getElementById("del_afkey");
	o.setAttribute("value", afkey);

	o = document.getElementById("del_form");
	o.submit();
}

