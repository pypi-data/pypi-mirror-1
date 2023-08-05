var times = 0;

function init_mcol() {
	var bdy = document.getElementById("body");
	var r, w, h;
	var ua;

	ua = window.navigator.userAgent.toLowerCase();
	if(ua.indexOf('gecko') == -1) {
		alert("This only work for Firefox/Mozilla");
		return;
	}
	if(times > 0) {
		return;
	}
	times = 1;

	r = window_size();
	w = r[0];
	h = r[1];

	make_columns(bdy, 2, 300, h * 9 / 10);
}
//init_funcs.push(init_mcol);
