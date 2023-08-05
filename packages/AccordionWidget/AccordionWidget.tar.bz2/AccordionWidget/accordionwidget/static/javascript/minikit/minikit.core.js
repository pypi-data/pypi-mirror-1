/*
minikit :: core
a bag of javascript tricks, transparently compatible with mochikit.
Licenses are :
	nifty by Alessandro Fulciniti, public domain
	a few bits and bolts from yui, BSD
	cookies by http://www.quirksmode.org/js/cookies.html
	the rest by Troels Knak-Nielsen, public domain
*/
/*
global exports. this is the public html-hackers interface.
*/
var __EXPORT__ = function(self) {
	/** Selects elements with simple css selectors */
	self.getElementsBySelector = minikit.getElementsBySelector;

	/** useful mochikit(ish) exports */
	if (typeof(self.addLoadEvent) == "undefined") {
		self.addLoadEvent = minikit.addLoadEvent;
	}
	if (typeof(self.update) == "undefined") {
		self.update = minikit.update;
	}
	if (typeof(self.$) == "undefined") {
		self.$ = minikit.getElement;
	}
	if (typeof(self.forEach) == "undefined") {
		self.forEach = minikit.forEach;
	}
	if (typeof(self.bind) == "undefined") {
		self.bind = minikit.bind;
	}
	if (typeof(self.connect) == "undefined") {
		self.connect = minikit.connect;
	}
	if (typeof(self.disconnect) == "undefined") {
		self.disconnect = minikit.disconnect;
	}
	if (typeof(self.signal) == "undefined") {
		self.signal = minikit.signal;
	}
	if (typeof(self.createDOM) == "undefined") {
		self.createDOM = minikit.createDOM;
	}
	if (typeof(self.callLater) == "undefined") {
		self.callLater = minikit.callLater;
	}
}
if (typeof(minikit) == "undefined") {
	minikit = {};
}
minikit.extend = function(subClass, superconstructor) {
	var inlineSuper = function(){};
	inlineSuper.prototype = superconstructor.prototype;
	subClass.prototype = new inlineSuper();
	subClass.prototype.constructor = subClass;
	subClass.prototype.superconstructor = superconstructor;
	subClass.prototype.supertype = superconstructor.prototype;
}
/* lifted from yui */
minikit.setOpacity = function(el, val) {
	if (window.ActiveXObject && typeof el.style.filter == 'string') { // in case not appended
		el.style.filter = 'alpha(opacity=' + val * 100 + ')';
		if (!el.currentStyle || !el.currentStyle.hasLayout) {
			el.style.zoom = 1; // when no layout or cant tell
		}
	} else {
		el.style.opacity = val;
		el.style['-moz-opacity'] = val;
		el.style['-khtml-opacity'] = val;
	}
}
/** lifted from nifty */
minikit.getElementsBySelector = function(selector, /*optional*/ parent) {
	if (typeof(parent) == "undefined" || parent == null) {
		parent = document;
	}
	var j;
	var jl;
	var i;
	var s = [];
	var selid = "";
	var selclass = "";
	var tag = selector;
	var objlist = [];
	if (selector.indexOf(" ")>0) {  //descendant selector like "tag#id tag"
		s = selector.split(" ");
		var fs = s[0].split("#");
		if (fs.length == 1) {
			return objlist;
		}
		return parent.getElementById(fs[1]).getElementsByTagName(s[1]);
	}
	if (selector.indexOf("#")>0) { //id selector like "tag#id"
		s = selector.split("#");
		tag = s[0];
		selid = s[1];
	}
	if (selid != "") {
		objlist.push(parent.getElementById(selid));
		return objlist;
	}
	if (selector.indexOf(".")>0) {  //class selector like "tag.class"
		s = selector.split(".");
		tag = s[0];
		selclass = s[1];
	}
	var v = parent.getElementsByTagName(tag);  // tag selector like "tag"
	if (selclass == "") {
		return v;
	}
	var l = v.length;
	for (i=0;i<l;++i) {
		var cn = v[i].className.split(" ");
		jl = cn.length;
		for (j=0;j<jl;++j) {
			if (cn[j] == selclass) {
				objlist.push(v[i]);
				break;
			}
		}
	}
	return objlist;
}
/*
mochikit stubs.
supplies minimal versions of mochikit functions if not present.
if you want to use mochikit, load it before minikit.
*/
if (typeof(update) == "function") {
	minikit.update = update;
} else {
	minikit.update = function(self, obj/*, ... */) {
	    if (self === null) {
		self = {};
	    }
	    for (var i = 1; i < arguments.length; i++) {
		var o = arguments[i];
		if (typeof(o) != 'undefined' && o !== null) {
		    for (var k in o) {
			self[k] = o[k];
		    }
		}
	    }
	    return self;
	};
}

if (typeof(getElement) == "function") {
	minikit.getElement = getElement;
} else {
	minikit.getElement = function(el) {
		if (typeof el == 'string') return document.getElementById(el);
		return el;
	}
}

if (typeof(forEach) == "function") {
	minikit.forEach = forEach;
} else {
	minikit.forEach = function(iterable, func, self /* optional */) {
		if (!self) self = window;
		for(var i=0;i<iterable.length;i++) func.apply(self, [iterable[i]]);
	}
}

if (typeof(bind) == "function") {
	minikit.bind = bind;
} else {
	minikit.bind = function(fnc, object) {
		if (typeof(fnc) == "string") {
			fnc = object[fnc];
		}
		var args = [];
		for (var i=2; i<arguments.length; ++i) {
			args.push(arguments[i]);
		}
		return function() {
			var args2 = [];
			for (var i = 0; i < arguments.length; i++) {
				args2.push(arguments[i]);
			}
			return fnc.apply(object, args.concat(args2));
		}
	}
}
if (typeof(computedStyle) == "function") {
	minikit.computedStyle = computedStyle;
} else {
	minikit.computedStyle = function(elem, cssProperty) {
		var arr = cssProperty.split('-');
		var cssProperty = arr[0];
		for (var i = 1; i < arr.length; i++) {
			cssProperty += arr[i].charAt(0).toUpperCase() + arr[i].substring(1);
		}
		if (cssProperty == 'opacity' && elem.filters) { // IE opacity
			try {
				return elem.filters.item('DXImageTransform.Microsoft.Alpha').opacity / 100;
			} catch(e) {
				try {
					return elem.filters.item('alpha').opacity / 100;
				} catch(e) {}
			}
		}
		if (elem.currentStyle) {
			return elem.currentStyle[cssProperty];
		}
		if (typeof(document.defaultView) == 'undefined') {
			return undefined;
		}
		if (document.defaultView === null) {
			return undefined;
		}
		var style = document.defaultView.getComputedStyle(elem, null);
		if (typeof(style) == 'undefined' || style === null) {
			return undefined;
		}
		var selectorCase = cssProperty.replace(/([A-Z])/g, '-$1').toLowerCase();
		return style.getPropertyValue(selectorCase);
	}
}
if (typeof(createDOM) == "function") {
	minikit.createDOM = createDOM;
} else {
	minikit.createDOM = function(name, attrs) {
		if (!attrs) {
			attrs = [];
		}
		if (window.ActiveXObject) {
			var contents = "";
			if ('name' in attrs) {
				contents += ' name="' + minikit.escapeHTML(attrs.name) + '"';
			}
			if (name == 'input' && 'type' in attrs) {
				contents += ' type="' + minikit.escapeHTML(attrs.type) + '"';
			}
			if (name == 'label' && 'for' in attrs) {
				contents += ' for="' + minikit.escapeHTML(attrs["for"]) + '"';
			}
			if (contents) {
				name = "<" + name + contents + ">";
			}
		}
		var elem = document.createElement(name);
		if (attrs) {
			if (window.ActiveXObject) {
				var renames = {
					"class": "className",
					"checked": "defaultChecked",
					"usemap": "useMap",
					"for": "htmlFor",
					"readonly": "readOnly"
				}
				for (k in attrs) {
					v = attrs[k];
					var renamed = renames[k];
					if (k == "style" && typeof(v) == "string") {
						elem.style.cssText = v;
					} else if (typeof(renamed) == "string") {
						elem[renamed] = v;
					} else {
						elem.setAttribute(k, v);
					}
				}
			} else {
				for (var k in attrs) {
					elem.setAttribute(k, attrs[k]);
				}
			}
		}
		return elem;
	}
}
if (typeof(escapeHTML) == "function") {
	minikit.escapeHTML = escapeHTML;
} else {
	minikit.escapeHTML = function(s) {
		return s.replace(/&/g, "&amp;"
			).replace(/"/g, "&quot;"
			).replace(/</g, "&lt;"
			).replace(/>/g, "&gt;");
	}
}
if (typeof(getElementDimensions) == "function") {
	minikit.getElementDimensions = getElementDimensions;
} else {
	minikit.getElementDimensions = function(elem) {
		if (typeof(elem.w) == 'number' || typeof(elem.h) == 'number') {
			return {w: elem.w || 0, h: elem.h || 0};
		}
		if (!elem) {
			return undefined;
		}
		if (minikit.computedStyle(elem, 'display') != 'none') {
			return {w: elem.offsetWidth || 0, h: elem.offsetHeight || 0};
		}
		var s = elem.style;
		var originalVisibility = s.visibility;
		var originalPosition = s.position;
		s.visibility = 'hidden';
		s.position = 'absolute';
		s.display = '';
		var originalWidth = elem.offsetWidth;
		var originalHeight = elem.offsetHeight;
		s.display = 'none';
		s.position = originalPosition;
		s.visibility = originalVisibility;
		return {w: originalWidth, h: originalHeight};
	}
}
if (typeof(callLater) == "function") {
	minikit.callLater = callLater;
} else {
	minikit.callLater = function(seconds, func) {
		setTimeout(func, 1000 * seconds);
	}
}
if (typeof(addLoadEvent) == "function") {
	minikit.addLoadEvent = addLoadEvent;
} else {
	minikit.addLoadEvent = function(func) {
		if (window.onload) {
			var previous = window.onload;
		}
		window.onload = function(e) {
			func.apply(window, [e]);
			if (previous) {
				previous.apply(window, [e]);
			}
		}
	}
}

if (typeof(connect) == "function") {
	minikit.connect = connect;
	minikit.disconnect = disconnect;
} else {
	minikit._signalCache = [];
	minikit.connect = function(src, signal, fnc) {
		if (!src) return;
		var cache = [];
		if (src.addEventListener) {
			var wrapper = function(e) {
				var evt = {
					stop : function() {
						if (e.cancelable) {
							e.preventDefault();
						}
						e.stopPropagation();
					},
					key : function() {
						return {code: e.keyCode}
					}
				}
				fnc(evt);
			}
			var name = signal.replace(/^(on)/, "");
			src.addEventListener(name, wrapper, false);
			cache = [src, name, wrapper];
		} else if (src.attachEvent) {
			var wrapper = function() {
				var e = window.event;
				var evt = {
					stop : function() {
						e.cancelBubble = true;
						e.returnValue = false;
					},
					key : function() {
						return {code: e.keyCode}
					}
				}
				fnc(evt);
			}
			src.attachEvent(signal, wrapper);
			cache = [src, signal, wrapper];
		}
		if (!src._signals) {
			src._signals = [];
		}
		if (!src._signals[signal]) {
			src._signals[signal] = [];
		}
		src._signals[signal].push(fnc);
		cache.push(fnc);
		minikit._signalCache.push(cache);
		return minikit._signalCache.length - 1;
	}
	minikit.disconnect = function(ident) {
		var cache = minikit._signalCache[ident];
		if (cache == null) {
			return;
		}
		var src = cache[0];
		var name = cache[1];
		var wrapper = cache[2];
		if (src.addEventListener) {
			src.removeEventListener(name, wrapper);
		} else if (src.attachEvent) {
			src.detachEvent(signal, wrapper);
		}

		var fnc = cache[3];
		var sigs = src._signals[signal];
		for (var i=0; i < sigs.length; ++i) {
			if (sigs[i] == fnc) {
				sigs[i] = null;
			}
		}
		minikit._signalCache[ident] = null;
	}
}
if (typeof(signal) == "function") {
	minikit.signal = signal;
} else {
	minikit.signal = function(src, signal) {
		try {
			var sigs = src._signals[signal];
			var args = [];
			for (var i=2; i < arguments.length; i++) {
				args.push(arguments[i]);
			}
			for (var i=0; i < sigs.length; i++) {
				if (sigs[i] != "") {
					try {
						sigs[i].apply(src, args);
					} catch (e) { /* squelch */ }
				}
			}
		} catch (e) { /* squelch */ }
	}
}

if (typeof(getElementPosition) == "function") {
	minikit.getElementPosition = getElementPosition;
} else {
	minikit.getElementPosition = function(obj) {
		var curleft = curtop = 0;
		if (obj.offsetParent) {
			curleft = obj.offsetLeft
			curtop = obj.offsetTop
			while (obj = obj.offsetParent) {
				curleft += obj.offsetLeft
				curtop += obj.offsetTop
			}
		}
		return {x: curleft, y: curtop};
	}
}
if (typeof(minikit.cookies) == "undefined") {
	minikit.cookies = {};
}
minikit.cookies.set = function(name, value, days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	} else {
		var expires = "";
	}
	document.cookie = name+"="+escape(value)+expires+"; path=/";
}

minikit.cookies.get = function(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') {
			c = c.substring(1,c.length);
		}
		if (c.indexOf(nameEQ) == 0) {
			var raw = c.substring(nameEQ.length,c.length);
			return unescape(raw).replace(/\+/g, " ");
		}
	}
	return null;
}

minikit.cookies.erase = function(name) {
	minikit.cookies.set(name,"",-1);
}
__EXPORT__(window);