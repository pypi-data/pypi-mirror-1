
function gindoc_parser(kw_url, attach_url) {
    this.kw_url = kw_url;
    this.attach_url = attach_url;
}

gindoc_parser.prototype = {
    fmt_int: function(n, w) {
	var i, t = n;
	var r = "";
	for(i = 1; i < w; i++) {
	    t = t / 10;
	    if(t < 1) break;
	}
	while(i < w) {
	    r = r + "0";
	    i++;
	}
	return r + n;
    },
    code_proc: function(msg, kws) {
	var lines = msg.split('\n');
	var line;
	var idx;
	var reg = new RegExp("(^|[^0-9a-zA-Z_])(" + kws.join('|') + ")([^0-9a-zA-Z_]|$)", "g");
	
	for(idx = 0; idx < lines.length; idx++) {
	    line = lines[idx];
	    line = line.replace(reg, "$1<span class=\"code_kw\">$2</span>$3");
	    lines[idx] = this.fmt_int(idx + 1, 3) + "\t" + line;
	}
	return lines.join('\n');
    },
    cpp_proc: function(msg) {
	var reg_func = new RegExp("([a-zA-Z_][0-9a-zA-Z_]*[ \n\r\t\\*]+)([a-zA-Z_][0-9a-zA-Z_:]*)(\\([^\\)]*\\)[ \n\r\t]*[{;])", "g");
	var reg_class = new RegExp("(class[ \n\r\t]+)([a-zA-Z_][0-9a-zA-Z_]*)([ \n\r\t]*[;{])", "g");
	
	msg = msg.replace(/\$\$/g, "CPPdolar");
	msg = msg.replace(/\$/g, "");
	msg = msg.replace(/CPPdolar/g, "$");
	msg = msg.replace(/</g, "&lt;");
	msg = msg.replace(/>/g, "&gt;");
	msg = msg.replace(reg_func, "$1<span CPPCODE_class=\"code_func\">$2</span>$3");
	msg = msg.replace(reg_class, "$1<span CPPCODE_class=\"code_func\">$2</span>$3");
	msg = this.code_proc(msg, ["class", "int", "float", "unsigned", "struct", "return", "if", "else", "for", "while", "do", "char", "long", "double", "public", "private", "protected", "void", "switch", "case", "default", "throw", "try", "catch", "namespace", "template", "typename"]);
	msg = msg.replace(/ CPPCODE_class=/g, " class=");
	return msg;
    },
    python_proc: function(msg) {
	var reg = new RegExp("( )([a-zA-Z_][0-9a-zA-Z_]*)(\\([^\\)]*\\):)", "g")
	msg = msg.replace(/</g, "&lt;");
	msg = msg.replace(/>/g, "&gt;");
	msg = msg.replace(reg, "$1<span PYCODE_class=\"code_func\">$2</span>$3");
	msg = this.code_proc(msg, ["class", "def", "return", "import", "from", "while", "break", "continue", "if", "for", "else", "elif", "in", "raise", "except", "yield"]);
	msg = msg.replace(/ PYCODE_class=/g, " class=");
	return msg;
    },
    raw_proc: function(msg) {
	msg = msg.replace(/</g, "&lt;");
	msg = msg.replace(/>/g, "&gt;");
	return msg;
    },
    replace_keywords: function(msg) {
	var re = /\$[^\t\n$]*\$/g;
	var m;
	var result = "";
	var start, end;
	
	// alert(msg);
	m = re.exec(msg);
	start = end = 0;
	while(m) {
	    end = RegExp.leftContext.length;
	    if(start != end) result += msg.substring(start, end);
	    if(RegExp.lastMatch == "$$")
		result += "$";
	    else {
		m = RegExp.lastMatch.substring(1, RegExp.lastMatch.length - 1);
		result += "<a href='"+ this.kw_url + m + "'>" + m + "</a>";
	    }
	    start = re.lastIndex;
	    m = re.exec(msg);
	}
	end = msg.length;
	if(start != end) result += msg.substring(start, end);
	
	return result;
    },
    replace_style: function(msg) {
	var len = msg.length;
	var i, ni, oi;
	var c;
	var result = "";
	
	for(i = oi = 0; i < len; i++) {
	    c = msg.charAt(i);
	    switch(c) {
	    case '`':
		if(oi != i) result += msg.substring(oi, i);
		if(msg.substring(i, i + 3) == '```') {
		    oi = i + 3;
		    ni = msg.indexOf('\'\'\'');
		    if(ni >= 0) {
			result += "<div class='quote'>" + msg.substring(oi, ni) + "</div>";
			oi = ni + 3;
			i = ni + 2;
		    } else {
			result += '```';
			i = i + 2;
		    }
		} else {
		    oi = i + 1;
		    ni = msg.indexOf('\'', i);
		    if(ni >= 0) {
			i = ni;
			result += "<b>" + msg.substring(oi,i) + "</b>";
			oi = i + 1;
		    } else {
			result += '`';
		    }
		}
		break;
	    default:
		break;
	    }
	}
	if(len != oi) result += msg.substring(oi, i);
	return result;
    },
    replace_url: function(msg) {
	var re = /(linkname:([^ ]+|\[[^\]]*\])\ |\[)?((https?:\/\/|ftp:\/\/|attach:|amazon_isbn:|amazon_thumb:)[^ \n\t\]]+\]?)/gi;
	var result = "";
	var start = 0;
	var end = 0;
	var mo, m, r;
	var url;
	var override_txt = "";
	
	mo = re.exec(msg);
	while(mo) {
	    end = RegExp.leftContext.length;
	    m = RegExp.lastMatch;
	    if(m.charAt(0) != '[') {
		url = m;
	    } else {
		url = mo[3];
		url = url.substring(0, url.length - 1);
	    }
	    txt = m;
	    if(url.substring(0, 9) == "linkname:") {
		override_txt = mo[1].substring(9, mo[1].length - 1)
		    if(override_txt.charAt(0) == '[')
			override_txt = override_txt.substring(1, override_txt.length - 1);
		url = mo[3]
	    }
	    if(url.substring(0, 7) == "attach:") {
		txt = url.substring(7);
		}
	    if(url.substring(0, 12) == "amazon_isbn:") {
		txt = url.substring(12);
	    }
	    if(url.substring(0, 13) == "amazon_thumb:") {
		txt = url.substring(13);
	    }
	    if(url.substring(0, 7) == "attach:") {
		url = this.attach_url + txt;
	    }
	    if(url.substring(0, 12) == "amazon_isbn:") {
		url = "http://www.amazon.com/gp/product/" + txt;
		txt = "ISBN:" + txt;
	    }
	    if(url.substring(0, 13) == "amazon_thumb:") {
		url = "http://images.amazon.com/images/P/" + txt + ".01._SCTHUMBZZZ_.jpg";
	    }
	    if(override_txt != "") txt = override_txt;
	    if(m.charAt(0) != '[')
			r = "<a href=\"" + url + "\">" + txt + "</a>";
	    else
		r = "<img src=\"" + url + "\">";
		result += this.replace_keywords(this.replace_style(msg.substring(start, end)));
	    result += r;
	    start = re.lastIndex;
	    mo = re.exec(msg);
	}
	if(start != msg.length)
	    result += this.replace_keywords(this.replace_style(msg.substring(start, msg.length)));
	return result;
    },
    show_msg: function(msg) {
	var i, oi, j, len;
	var sp = 0;
	var c;
	var lst_lvl = 0;
	var lst_lvl_sp = new Array();
	var lst_lvl_type = new Array();
	var result = "";
	var preflag = 0;
	
	len = msg.length;
	for(i = oi = 0; i < len; i++) {
	    c = msg.charAt(i);
	    switch(c) {
		case ' ':
		sp++;
		break;
	    case '\r':
		break;
	    case '\n':
		while(lst_lvl > 0) {
		    if(lst_lvl_type[lst_lvl - 1] == '*')
			result += '</ul>\n';
		    else
			result += '</ol>\n';
		    lst_lvl--;
		}
		if(sp == 0 && preflag == 0) {
		    if(oi != i) result += this.replace_url(msg.substring(oi, i));
		    result += '<p/>\n';
		    oi = i + 1
		}
		sp = 0;
		break;
	    case '=':
		if(oi != i) result += this.replace_url(msg.substring(oi, i));
		while(lst_lvl > 0) {
		    if(lst_lvl_type[lst_lvl - 1] == '*')
			result += '</ul>\n';
		    else
			result += '</ol>\n';
		    lst_lvl--;
		}
		for(j = 0; j < 3; j++, i++) {
		    if(msg.charAt(i) != '=')
			break;
		}
		result += '<H' + j + '>';
		oi = i;
		i = msg.indexOf('=', i);
		if(i == -1) i = len;
			result += this.replace_url(msg.substring(oi, i));
		result += '</H' + j + '>';
		i += j - 1;
		oi = i + 1;
		break;
	    case '*':
	    case '#':
		if(oi != i) result += this.replace_url(msg.substring(oi, i));
		if(lst_lvl == 0 || lst_lvl_sp[lst_lvl - 1] < sp) {
		    if(c == '*')
			result += '<ul>\n';
		    else
			result += '<ol>\n';
		    lst_lvl_type[lst_lvl] = c;
		    lst_lvl_sp[lst_lvl++] = sp;
		} else {
		    while(lst_lvl_sp[lst_lvl - 1] > sp) {
			if(lst_lvl_type[lst_lvl - 1] == '*')
			    result += '</ul>\n';
			else
			    result += '</ol>\n';
			lst_lvl--;
		    }
		}
		result += '<li>';
		i++;
		oi = i;
		i = msg.indexOf('\n', i);
		if(i == -1) i = len;
		result += this.replace_url(msg.substring(oi, i)) + '\n';
		sp = 0;
		oi = i + 1;
		break;
	    case '{':
		if(oi != i) result += this.replace_url(msg.substring(oi, i));
		oi = i;
		if(msg.substring(i, i + 3) == "{{{") {
		    result +=  "<pre>";
		    
		    i += 3;
		    oi = i;
		    j = i + msg.substring(i).search("\n}}}");
		    if(msg.substring(i, i + "#!python\n".length) == "#!python\n") {
			i += "#!python\n".length;
			sub_msg = msg.substring(i, j);
			sub_msg = sub_msg.replace(/\$(.)/g, "$1");
			result += this.python_proc(sub_msg);
			i = j;
		    } else if(msg.substring(i, i + "#!cpp\n".length) == "#!cpp\n") {
			i += "#!cpp\n".length;
			sub_msg = msg.substring(i, j);
			sub_msg = sub_msg.replace(/\$(.)/g, "$1");
			result += this.cpp_proc(sub_msg);
			i = j;
		    } else if(msg.substring(i, i + "#!raw\n".length) == "#!raw\n") {
			i += "#!raw\n".length;
			sub_msg = msg.substring(i, j);
			sub_msg = sub_msg.replace(/\$(.)/g, "$1");
			result += this.raw_proc(sub_msg);
			i = j;
		    } else {
			for(; i < j; i++) {
			    c = msg.charAt(i);
			    if(c == "<") {
				result += this.replace_url(msg.substring(oi, i));
				result += "&lt;";
				oi = i + 1;
			    } else if(c == "&" && msg.charAt(i+1) != '#') {
				// &#????; should be avoid
				result += this.replace_url(msg.substring(oi, i));
				result += "&amp;";
				oi = i + 1;
			    }
			}
			result += this.replace_url(msg.substring(oi, i));
		    }
		    result += "</pre>\n";
		    i += 3;
		    oi = i + 1;
		    break;
		}
	    default:
		while(lst_lvl > 0) {
		    if(lst_lvl_type[lst_lvl - 1] == '*')
			result += '</ul>\n';
		    else
			result += '</ol>\n';
		    lst_lvl--;
		}
		i = msg.indexOf('\n', i);
		if(i == -1) i = len;
		sp = 0;
		break;
	    }
	}
	if(oi != i)
	    result += this.replace_url(msg.substring(oi, i));
	while(lst_lvl > 0) {
	    if(lst_lvl_type[lst_lvl - 1] == '*')
		result += '</ul>\n';
	    else
		result += '</ol>\n';
	    lst_lvl--;
	}
	// alert(result);
	return result;
    }
}
