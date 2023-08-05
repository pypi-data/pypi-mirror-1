/*-
 * Copyright (c) 2006
 *      Thinker Li (thinker@branda.to).  All rights reserved.
 *
 * This code is provided by Thinker Li from Taiwan.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 4. The names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE PROVIDERS AND CONTRIBUTORS `AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 */

/* -----------------------------------------------------------------------
 * Convience functions
 */
function copy_into_array(a, b) {
	var i;

	for(i in b) {
		a.push(b[i]);
	}
}

function DOM_insert_after(n, o) {
	var p = o.parentNode;

	if(o.nextSibling == null) {
		p.appendChild(n);
	} else {
		p.insertBefore(n, o.nextSibling);
	}
}

function DOM_last_child(o) {
	return o.childNodes.item(o.childNodes.length - 1);
}

function max(n1, n2) {
	return (n1 > n2)? n1: n2;
}

function window_size() {
	return new Array(window.innerWidth, window.innerHeight);
}

function new_node(n) {
	return document.createElement(n);
}

function is_wide(o, w, h) {
	if(o.nodeName == "PRE" ||
	   (o.nodeName == "IMG" && o.width > w)) {
		return true;
	}
	return false;
}

function height_of(o) {
	var margin;
	var style;
	var h;

	style = window.getComputedStyle(o, "");
	if(o.previousSibling != null) {
		margin = max(parseFloat(style.marginTop),
				parseFloat(style.marginBottom));
	} else {
		margin = 0;
	}
	h = o.offsetHeight + margin;

	return h;
}

function show_nested_array(a) {
	var i, r;

	if(a instanceof Array) {
		r = "[";
		for(i in a) {
			r = r + show(a[i]);
		}
		r = r + "]";
	} else {
		r = "" + a;
	}
	return r;
}

function all_children(obj) {
	var all = new Array();

	for(i = 0; i < obj.childNodes.length; i++) {
		all.push(obj.childNodes.item(i));
	}
	return all;
}

/* -----------------------------------------------------------------------
 * Layout engine
 */

function split_node_in_vertical(o, h) {
	var no, parent = o.parentNode;
	var i, ac_h, child;
	var text;

	/*
	 * insert a new node before old one
	 */
	no = o.cloneNode(false);
	no.style.paddingBottom = "0";
	parent.insertBefore(no, o);

	ac_h = height_of(no);
	if(ac_h > h) {
		return null;
	}

	/*
	 * move child from old one to new one
	 * until overflow
	 */
	while(ac_h <= h) {
		child = o.childNodes.item(0);
		o.removeChild(child);
		no.appendChild(child);
		ac_h = height_of(no);
	}

	/*
	 * Try to split last child of new one
	 */
	child = DOM_last_child(no);
	if(child.nodeName == "#text") {
		text = child.data;
		i = text.length;
		while(ac_h > h) {
			i--;
			child.data = text.substring(0, i);
			ac_h = height_of(no);
		}
		child.data = text;
		if(i > 0) {
			child.splitText(i);
		}
		ac_h = height_of(no);
	}

	/*
	 * shrink new one until not overflow
	 */
	while(ac_h > h) {
		child = DOM_last_child(no);
		no.removeChild(child);
		o.insertBefore(child, o.firstChild);
		ac_h = height_of(no);
	}

	if(no.childNodes.length == 0) {
		return null;
	}
	return no;
}

function can_fit_without_bottom_padding(o, ac_h, h) {
	var padding;

	padding =  window.getComputedStyle(o, "").paddingBottom;
	padding = parseFloat(padding);
	return (height_of(o) - padding + ac_h) <= h;
}

function is_accumate_height_overflow(o, ac_h, h) {
	return (height_of(o) + ac_h) > h;
}

function make_a_chunk(all, w, h, start_pos) {
	var idx = start_pos;
	var ac_h, child, c_h;
	var padding;
	var new_split;
	var chunk = new Array();
	
	ac_h = 0;
	for(;idx < all.length; idx++) {
		child = all[idx];

		if(child.offsetHeight == null) {	// skip node
							// with-out height
			continue;
		}

		if(is_accumate_height_overflow(child, ac_h, h) &&
		   chunk.length > 0) {
			if(can_fit_without_bottom_padding(child, ac_h, h)) {
				child.paddingBottom = 0;
			} else {
				new_split = split_node_in_vertical(child, h - ac_h);
				if(new_split != null) {
					chunk.push(new_split);
				}
				break;
			}
		}
		c_h = height_of(child);
		chunk.push(child);
		ac_h = ac_h + c_h;
	}
	return new Array(chunk, idx);
}

function extract_narrow_wide_parts(all, w, h) {
	var i;
	var parts = new Array();
	var part;
	var o;

	part = new Array();
	for(i = 0; i < all.length; i++) {
		o = all[i];
		part.push(o);
		if(is_wide(o, w, h)) {
			if(part.length > 1) {
				part.pop();
				parts.push(part);
			}
			parts.push(new Array(o));
			part = new Array();
		}
	}
	parts.push(part);

	return parts;
}

function make_chunks(all, w, h) {
	var chunks = new Array();
	var chunk;
	var parts, part;
	var r;
	var ci, i;

	parts = extract_narrow_wide_parts(all, w, h);

	for(i = 0; i < parts.length; i = i + 2) {
		part = parts[i];
		for(ci = 0; ci < part.length;) {
			r = make_a_chunk(part, w, h, ci);
			chunk = r[0];
			ci = r[1];
			chunks.push(chunk);
		}
		if((i + 1) < parts.length) {
			chunk = new Array();
			chunk.push(parts[i + 1][0]);
			chunks.push(chunk);
		}
	}
	return chunks;
}

function rearrange_to_eq_hight_cols(row, cols, colw) {
	var h, ac_h;
	var all = new Array();
	var new_row;
	var i, j, idx;

	for(i = 0; i < row.length; i++) {
		for(j = 0; j < row[i].length; j++)
			all.push(row[i][j]);
	}

	h = 0;
	for(i = 0; i < all.length; i++) {
		h = h + height_of(all[i]);
	}

	h = h / cols;
	new_row = make_chunks(all, colw, h);
	for(i = cols; i < new_row.length; i++) {
		for(j = 0; j < new_row[i].length; j++) {
			new_row[cols - 1].push(new_row[i][j]);
		}
	}
	while(new_row.length > cols) {
		new_row.pop();
	}

	return new_row;
}

function make_chunks_to_rows(chunks, cols, colw, colh) {
	var rows = new Array();
	var row;
	var ac_row;
	var chunk;
	var i;

	for(i = 0; i < chunks.length;) {
		row = new Array();
		for(ac_row = 0; ac_row < cols && i < chunks.length; ac_row++, i++) {
			chunk = chunks[i];
			row.push(chunk);

			if(is_wide(chunk[0], colw, colh)) {
				if(ac_row > 0) {
					row.pop();
					row = rearrange_to_eq_hight_cols(row, cols,
					   colw);
				} else {
					if(rows.length > 0) {
						rows[rows.length - 1] =
rearrange_to_eq_hight_cols(rows[rows.length - 1], cols, colw);
					}
					i++;
				}
				break;
			}
		}
		rows.push(row);
	}

	return rows;
}

function move_img_to_top(obj, colw, colh) {
	var p, np;
	var img, o;
	var i, j;

	for(i = 0; i < obj.childNodes.length; i++) {
		if(obj.childNodes.item(i).nodeName != "P") {
			continue;
		}

		p = obj.childNodes.item(i);
		for(j = 0; j < p.childNodes.length; j++) {
			if(p.childNodes.item(j).nodeName != "IMG")
				continue;

			img = p.childNodes.item(j);

			if(img.offsetWidth <= colw)
				continue;

			p.removeChild(img);
			
			DOM_insert_after(img, p);

			np = new_node("P");
			while(j < p.childNodes.length) {
				o = p.childNodes.item(j);
				p.removeChild(o);
				np.appendChild(o);
			}
			if(np.childNodes.length > 0) {
				DOM_insert_after(np, img);
			}

			/* remove empty para */
			if(p.childNodes.length == 0) {
				p.parentNode.removeChild(p);
			}
		}
	}
}

function create_mcol_table_from_rows(rows, cols, colw, colh) {
	var tb, tr, td, div_o, row;
	var i, j, k;

	tb = new_node('table');
	tb.cellSpacing = "20px";

	for(i = 0; i < rows.length; i++) {
		row = rows[i];
		tr = new_node("tr");
		tb.appendChild(tr);

		if(is_wide(row[0][0], colw, colh)) {
			td = new_node("td");
			td.style.textAlign = "center";
			td.colSpan = cols;
			td.appendChild(row[0][0]);
			tr.appendChild(td);
			continue;
		}

		for(j = 0; j < row.length; j++) {
			div_o = new_node("div");
			div_o.style.width = "" + colw + "px";
			div_o.style.display = "block";
			//div_o.style.height = "" + colh + "px";
			div_o.style.padding = "0 0 0 0";
			div_o.style.margin = "0 0 0 0";

			for(k = 0; k < row[j].length; k++) {
				div_o.appendChild(row[j][k]);
			}

			td = new_node("td");
			td.style.verticalAlign = "top";
			td.appendChild(div_o);
			tr.appendChild(td);
		}
	}

	return tb;
}

function move_text_to_para(obj) {
	var child;
	var p;
	var i;

	for(i = 0; i < obj.childNodes.length; i++) {
		child = obj.childNodes.item(i);
		if(child.nodeName == "UL" || child.nodeName == "OL" || child.nodeName == "P" || child.nodeName == "PRE") {
			continue;
		}

		p = new_node("p");
		obj.insertBefore(p, child);
		i++;
		while( i < obj.childNodes.length && child.nodeName != "UL"
&& child.nodeName != "OL" && child.nodeName != "P" && child.nodeName != "PRE") {
			obj.removeChild(child);
			p.appendChild(child);
			child = obj.childNodes.item(i);
		}
	}
}

function make_columns(obj, cols, colw, colh) {
	var chunks, all, rows;
	var parent;
	var tb;

	move_text_to_para(obj);
	move_img_to_top(obj, colw, colh);

	obj.style.display = "block";
	obj.style.width = "" + colw + "px";

	all = all_children(obj);

	chunks = make_chunks(all, colw, colh);

	rows = make_chunks_to_rows(chunks, cols, colw, colh);
	
	parent = obj.parentNode;

	tb = create_mcol_table_from_rows(rows, cols, colw, colh);
	
	parent.insertBefore(tb, obj);
	parent.removeChild(obj);
	tb.className = obj.className;
	tb.id = obj.id;
}
