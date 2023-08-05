/*
minikit :: fx
a bag of javascript tricks, transparently compatible with mochikit.
Licenses are :
	mochikit by Bob Ippolito, MIT
	moo.fx by Valerio Proietti, MIT
	math functions by Robert Penner, BSD
	nifty by Alessandro Fulciniti, public domain
	a few bits and bolts from yui, BSD
	the rest by Troels Knak-Nielsen, public domain
*/
if (typeof(minikit) == "undefined") {
	throw new Error("minikit.fx depends on minikit");
}
if (typeof(minikit.fx) == "undefined") {
	minikit.fx = {};
}
/*
global exports. this is the public html-hackers interface.
*/
var __EXPORT__ = function(self) {

	/** Makes an accordion from two arrays of headers + content divs */
	self.makeAccordion = function (togglers, elements, options) {
		new minikit.fx.Accordion(togglers, elements, options);
	};

	/** Rounds corners on a block element */
	self.niftyRound = minikit.fx.niftyRound;
}
/*
moo.fx, simple effects library by Valerio Proietti (http://mad4milk.net)
*/
minikit.fx.Base = function(){};
minikit.fx.Base.prototype.setOptions = function(options) {
	this.options = update({
		duration: 500,
		onComplete: '',
		transition: minikit.fx.sinoidal
	}, options);
};
minikit.fx.Base.prototype.step = function() {
	var time  = (new Date).getTime();
	if (time >= this.options.duration+this.startTime) {
		this.now = this.to;
		clearInterval (this.timer);
		this.timer = null;
		if (this.options.onComplete) setTimeout(bind(this.options.onComplete, this), 10);
	} else {
		var Tpos = (time - this.startTime) / (this.options.duration);
		this.now = this.options.transition(Tpos) * (this.to-this.from) + this.from;
	}
	this.increase();
};
minikit.fx.Base.prototype.custom = function(from, to) {
	if (this.timer != null) return;
	this.from = from;
	this.to = to;
	this.startTime = (new Date).getTime();
	this.timer = setInterval (bind(this.step, this), 13);
};
minikit.fx.Base.prototype.hide = function() {
	this.now = 0;
	this.increase();
};
minikit.fx.Base.prototype.clearTimer = function() {
	clearInterval(this.timer);
	this.timer = null;
};

minikit.fx.Layout = function(el, options) {
	this.el = minikit.getElement(el);
	options = options || {};
	this.el.style.overflow = "hidden";
	this.iniWidth = this.el.offsetWidth;
	this.iniHeight = this.el.offsetHeight;
	this.setOptions(options);
};
minikit.extend(minikit.fx.Layout, minikit.fx.Base);

/** height stretcher */
minikit.fx.Height = function(el, options) {
	this.superconstructor.apply(this, arguments);
};
minikit.extend(minikit.fx.Height, minikit.fx.Layout);
minikit.fx.Height.prototype.increase = function() {
	this.el.style.height = this.now + "px";
};
minikit.fx.Height.prototype.toggle = function() {
	if (this.el.offsetHeight > 0) this.custom(this.el.offsetHeight, 0);
	else this.custom(0, this.el.scrollHeight);
};

/** width stretcher */
minikit.fx.Width = function(el, options) {
	this.superconstructor.apply(this, arguments);
};
minikit.extend(minikit.fx.Width, minikit.fx.Layout);
minikit.fx.Width.prototype.increase = function() {
	this.el.style.width = this.now + "px";
};
minikit.fx.Width.prototype.toggle = function() {
	if (this.el.offsetWidth > 0) this.custom(this.el.offsetWidth, 0);
	else this.custom(0, this.iniWidth);
};

/** fader */
minikit.fx.Opacity = function(el, options) {
	this.superconstructor.apply(this, arguments);
	this.el = minikit.getElement(el);
	options = options || {};
	this.now = 1;
	this.increase();
	this.setOptions(options);
};
minikit.extend(minikit.fx.Opacity, minikit.fx.Base);
minikit.fx.Opacity.prototype.increase = function() {
	if (this.now == 1 && (/Firefox/.test(navigator.userAgent))) this.now = 0.9999;
	this.setOpacity(this.now);
};
minikit.fx.Opacity.prototype.setOpacity = function(opacity) {
	if (opacity == 0 && this.el.style.visibility != "hidden") this.el.style.visibility = "hidden";
	else if (this.el.style.visibility != "visible") this.el.style.visibility = "visible";
	minikit.setOpacity(this.el, opacity);
};
minikit.fx.Opacity.prototype.toggle = function() {
	if (this.now > 0) this.custom(1, 0);
	else this.custom(0, 1);
};

minikit.fx.sinoidal = function(pos){
	return ((-Math.cos(pos*Math.PI)/2) + 0.5);
	//this transition is from script.aculo.us
}
minikit.fx.linear = function(pos){
	return pos;
}
minikit.fx.cubic = function(pos){
	return Math.pow(pos, 3);
}
minikit.fx.circ = function(pos){
	return Math.sqrt(pos);
}

/*
moo.fx pack, effects extensions for moo.fx
*/

/** smooth scroll */
minikit.fx.Scroll = function(options) {
	this.superconstructor.apply(this, arguments);
	this.setOptions(options);
};
minikit.extend(minikit.fx.Scroll, minikit.fx.Base);
minikit.fx.Scroll.prototype.scrollTo = function(el) {
	var dest = minikit.getElementPosition(minikit.getElement(el)).y;
	var client = window.innerHeight || document.documentElement.clientHeight;
	var full = document.documentElement.scrollHeight;
	var top = window.pageYOffset || document.body.scrollTop || document.documentElement.scrollTop;
	if (dest+client > full) this.custom(top, dest - client + (full-dest));
	else this.custom(top, dest);
};
minikit.fx.Scroll.prototype.increase = function() {
	window.scrollTo(0, this.now);
};


/** text size modify, now works with pixels too */
minikit.fx.Text = function(el, options) {
	this.superconstructor.apply(this, arguments);
	this.el = minikit.getElement(el);
	options = options || {};
	this.setOptions(options);
	if (!this.options.unit) this.options.unit = "em";
};
minikit.extend(minikit.fx.Text, minikit.fx.Base);
minikit.fx.Text.prototype.increase = function() {
	this.el.style.fontSize = this.now + this.options.unit;
};

/** composition effect: widht/height/opacity */
minikit.fx.Combo = function(el, options) {
	this.el = minikit.getElement(el);
	options = options || {};
	this.setOptions(options);
	if (this.options.opacity) {
		this.o = new minikit.fx.Opacity(el, options);
		options.onComplete = null;
	}
	if (this.options.height) {
		this.h = new minikit.fx.Height(el, options);
		options.onComplete = null;
	}
	if (this.options.width) this.w = new minikit.fx.Width(el, options);
};
minikit.fx.Combo.prototype.setOptions = function(options) {
	this.options = update({
		opacity: true,
		height: true,
		width: false
	}, options);
};
minikit.fx.Combo.prototype.toggle = function() {
	this.checkExec('toggle');
};
minikit.fx.Combo.prototype.hide = function() {
	this.checkExec('hide');
};
minikit.fx.Combo.prototype.clearTimer = function() {
	this.checkExec('clearTimer');
};
minikit.fx.Combo.prototype.checkExec = function(func) {
	if (this.o) this.o[func]();
	if (this.h) this.h[func]();
	if (this.w) this.w[func]();
};
minikit.fx.Combo.prototype.resizeTo = function(hto, wto) {
	if (this.h && this.w) {
		this.h.custom(this.el.offsetHeight, this.el.offsetHeight + hto);
		this.w.custom(this.el.offsetWidth, this.el.offsetWidth + wto);
	}
};
minikit.fx.Combo.prototype.customSize = function(hto, wto) {
	if (this.h && this.w) {
		this.h.custom(this.el.offsetHeight, hto);
		this.w.custom(this.el.offsetWidth, wto);
	}
};

/** the famous accordion widget */
minikit.fx.Accordion = function(togglers, elements, options) {
	this.elements = elements;
	this.setOptions(options);
	options = options || {};
	this.fxa = [];
	if (options && options.onComplete) {
		options.onFinish = options.onComplete;
	}
	var accordion = this;
	var i = 0;
	forEach(elements,
		function(el) {
			var j = i; i++;
			if ((minikit.computedStyle(el, "paddingTop") != "0px") || (minikit.computedStyle(el, "paddingBottom") != "0px")) {
				throw new Error("Accordion stretchers can't have padding.");
			}
			options.onComplete = function() {
				if (el.offsetHeight > 0) {
					el.style.height = '1%';
				}
				if (options.onFinish) {
					options.onFinish(el);
				}
			}
			this.fxa[j] = new minikit.fx.Combo(el, options);
			this.fxa[j].hide();
		}
		,this
	);
	var i = 0;
	forEach(togglers,
		function(togg) {
			var j = i; i++;
			connect(togg, "onclick", function(e) {
				accordion.showThisHideOpen(elements[j]);
			});
		}
	);
	var found = false;
	if (options.hash) {
		var i = 0;
		forEach(togglers, function(togg) {
			if (togg.title && (new RegExp("^(.*)#" + togg.title + "$")).test(window.location.href)) {
				accordion.showThisHideOpen(elements[i]);
				found = true;
			}
			i++;
		});
	}
	if (!found) {
		this.showThisHideOpen(elements[0]);
	}
};

minikit.fx.Accordion.prototype.setOptions = function(options) {
	this.options = {
		delay: 100,
		opacity: false
	}
	if (options) {
		for (property in options) {
			this.options[property] = options[property];
		}
	}
};
minikit.fx.Accordion.prototype.showThisHideOpen = function(toShow) {
	var i = 0;
	forEach(
		this.elements,
		function(el) {
			var j = i; i++;
			if (el.offsetHeight > 0 && el != toShow) this.clearAndToggle(el, j);
			if (el == toShow && toShow.offsetHeight == 0) {
				setTimeout(
					bind(function() {
						this.clearAndToggle(toShow, j);
					}, this),
					this.options.delay
				);
			}
			
		},
		this
	);
};
minikit.fx.Accordion.prototype.clearAndToggle = function(el, i) {
	this.fxa[i].clearTimer();
	this.fxa[i].toggle();
};

/*
Easing Equations (c) 2003 Robert Penner, http://www.robertpenner.com/easing_terms_of_use.html
*/

//expo
minikit.fx.expoIn = function(pos){
	return Math.pow(2, 10 * (pos - 1));
}
minikit.fx.expoOut = function(pos){
	return (-Math.pow(2, -10 * pos) + 1);
}

//quad
minikit.fx.quadIn = function(pos){
	return Math.pow(pos, 2);
}
minikit.fx.quadOut = function(pos){
	return -(pos)*(pos-2);
}

//circ
minikit.fx.circOut = function(pos){
	return Math.sqrt(1 - Math.pow(pos-1,2));
}
minikit.fx.circIn = function(pos){
	return -(Math.sqrt(1 - Math.pow(pos, 2)) - 1);
}

//back
minikit.fx.backIn = function(pos){
	return (pos)*pos*((2.7)*pos - 1.7);
}
minikit.fx.backOut = function(pos){
	return ((pos-1)*(pos-1)*((2.7)*(pos-1) + 1.7) + 1);
}

//sine
minikit.fx.sineOut = function(pos){
	return Math.sin(pos * (Math.PI/2));
}
minikit.fx.sineIn = function(pos){
	return -Math.cos(pos * (Math.PI/2)) + 1;
}
minikit.fx.sineInOut = function(pos){
	return -(Math.cos(Math.PI*pos) - 1)/2;
}

/**
  * Based on nifty by Alessandro Fulciniti, http://www.html.it/articoli/nifty/index.html
  */
minikit.fx.__styles = {
	all: {display: "block", height: "1px", overflow: "hidden"},
	r1: {margin: "0 5px"},
	r2: {margin: "0 3px"},
	r3: {margin: "0 2px"},
	r4: {margin: "0 1px", height: "2px"},
	rs1: {margin: "0 5px"},
	rs2: {margin: "0 5px"}
};

minikit.fx.applyStyle = function(el, style) {
	var st = minikit.fx.__styles.all;
	for (var key in st) {
		el.style[key] = st[key];
	}
	st = minikit.fx.__styles[style];
	for (var key in st) {
		el.style[key] = st[key];
	}
}

minikit.fx.niftyRound = function(element, options) {
	options = options || {};
	options.backgroundColor = options.backgroundColor || null;
	options.color = options.color || minikit.computedStyle(element, 'backgroundColor');
	options.size = options.size || null;
	options.edge = options.edge || "both";
	if (options.backgroundColor == null) {
		options.backgroundColor = minikit.computedStyle(element.parentNode, 'backgroundColor');
		if (options.backgroundColor == 'transparent') {
			options.backgroundColor = 'white';
		}
	}

	minikit.fx.splitBoxModel(element);
	if (options.edge == "both" || options.edge == "top") {
		minikit.fx.addTop(element, options.backgroundColor, options.color, options.size);
	}
	if (options.edge == "both" || options.edge == "bottom") {
		minikit.fx.addBottom(element, options.backgroundColor, options.color, options.size);
	}
}

minikit.fx.splitBoxModel = function(element) {
	var divInner = document.createElement(element.nodeName);
	while (element.hasChildNodes()) {
		divInner.appendChild(element.removeChild(element.firstChild));
	}
	element.appendChild(divInner);
	forEach(
		["paddingLeft", "paddingRight", "paddingTop", "paddingBottom"],
		function(identifier) {
			divInner.style[identifier] = minikit.computedStyle(element, identifier);
			element.style[identifier] = "0px";
		}
	);
}

minikit.fx.addTop = function(el, bk, color, size) {
	var i;
	var d = document.createElement("b");
	var cn = "r";
	var lim = 4;
	if (size && size == "small") {
		cn = "rs";
		lim = 2;
	}
	d.style.display = "block";
	d.style.backgroundColor = bk;
	for (i=1;i<=lim;++i) {
		var x = document.createElement("b");
		minikit.fx.applyStyle(x, cn + i);
		x.style.backgroundColor = color;
		d.appendChild(x);
	}
	el.insertBefore(d,el.firstChild);
}

minikit.fx.addBottom = function(el, bk, color, size) {
	var i;
	var d = document.createElement("b");
	var cn = "r";
	var lim = 4;
	if (size && size == "small") {
		cn = "rs";
		lim = 2;
	}
	d.style.display = "block";
	d.style.backgroundColor = bk;
	for (i=lim;i>0;--i) {
    		var x = document.createElement("b");
    		minikit.fx.applyStyle(x, cn + i);
    		x.style.backgroundColor = color;
    		d.appendChild(x);
	}
	el.appendChild(d,el.firstChild);
}
__EXPORT__(window);
