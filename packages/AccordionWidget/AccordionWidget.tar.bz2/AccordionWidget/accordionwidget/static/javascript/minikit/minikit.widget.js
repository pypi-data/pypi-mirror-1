/*
minikit :: widget
a bag of javascript tricks, transparently compatible with mochikit.
json by dojo, Academic Free License version 2.1 or above OR the modified BSD license.
cookies by http://www.quirksmode.org/js/cookies.html
*/
if (typeof(minikit) == "undefined") {
	throw new Error("minikit.widget depends on minikit");
}
if (typeof(minikit.widget) == "undefined") {
	minikit.widget = {};
}
/*
global exports. this is the public html-hackers interface.
*/
var __EXPORT__ = function(self) {
	/** table [, height] */
	self.scrollTable = minikit.scrollTable;

	/** el, args [, options] */
	self.contextMessage = minikit.contextMessage;
	
	/** el, args [, options] */
	self.datePicker = minikit.datePicker;

	/** el, args [, options] */
	self.permissions = minikit.permissions;
	
	/** el, values [, options] */
	self.comboBox = minikit.comboBox;
}

minikit.json = {
	__m : {
		'\b': '\\b',
		'\t': '\\t',
		'\n': '\\n',
		'\f': '\\f',
		'\r': '\\r',
		'"' : '\\"',
		'\\': '\\\\'
	},

	unserialize: function(/* jsonString */ json) {
		// FIXME: should this accept mozilla's optional second arg?
		try {
			return eval("(" + json + ")");
		} catch (ex) {
			return null;
		}
	},

	serialize: function(x) {
		if (x instanceof Array) {
			return minikit.json.array(x);
		}
		f = minikit.json[typeof(x)];
		if (f) {
			return f(x);
		}
		return 'null';
	},
	
	'array': function(x) {
		var a = ['['], b, f, i, l = x.length, v;
		for (i = 0; i < l; i += 1) {
		    v = x[i];
		    f = minikit.json[typeof(v)];
		    if (f) {
			v = f(v);
			if (typeof(v) == 'string') {
			    if (b) {
				a[a.length] = ',';
			    }
			    a[a.length] = v;
			    b = true;
			}
		    }
		}
		a[a.length] = ']';
		return a.join('');
	},

	'object': function(x) {
		if (x) {
			if (x instanceof Array) {
				return minikit.json.array(x);
			}
			var a = ['{'], b, f, i, v;
			for (i in x) {
				v = x[i];
				f = minikit.json[typeof(v)];
				if (f) {
					v = f(v);
					if (typeof(v) == 'string') {
						if (b) {
							a[a.length] = ',';
						}
						a.push(minikit.json.string(i), ':', v);
						b = true;
					}
				}
			}
			a[a.length] = '}';
			return a.join('');
		}
		return 'null';
	},

	'boolean': function(x) {
		return String(x);
	},

	'null': function(x) {
		return "null";
	},

	'number': function(x) {
		return isFinite(x) ? String(x) : 'null';
	},

	'string': function(x) {
		if (/["\\\x00-\x1f]/.test(x)) {
			x = x.replace(/([\x00-\x1f\\"])/g, function(a, b) {
				var c = minikit.json.__m[b];
				if (c) {
					return c;
				}
				c = b.charCodeAt();
				return '\\u00' + Math.floor(c / 16).toString(16) + (c % 16).toString(16);
			});
		}
		return '"' + x + '"';
	}
           
}

/**
  * A namespace for cookies
  */
minikit.Cookie = function(name, serializer /* optional */) {
	this.serializer = serializer || minikit.json;
	this.name = name;
	this._data = this.serializer.unserialize(minikit.cookies.get(this.name));
	if (this._data == null) {
		this._data = {};
	}
}
minikit.Cookie.prototype.get = function(key) {
	if (typeof(this._data[key]) == "undefined") {
		return null;
	}
	return this._data[key];
}
minikit.Cookie.prototype.set = function(key, value) {
	this._data[key] = value;
	minikit.cookies.set(this.name, this.serializer.serialize(this._data));
}

/**
  * Abstract baseclass for widgets
  */
minikit.widget.Base = function(args) {
	this.view = {};
	this._signalCache = [];
}
/**
  * Attach the controller to a HTMLElement in the DOM.
  */
minikit.widget.Base.prototype.attach = function(element) {
	throw new Error("minikit.widget.Base.prototype.attach is abstract");
}
/**
  * Remove the widget from the DOM.
  */
minikit.widget.Base.prototype.detach = function() {
	for (var i = 0, l = this._signalCache.length; i < l; ++i) {
		try {
			disconnect(this._signalCache[i]);
		} catch (ex) { /* squelch */ }
	}
	delete(this._signalCache);
}
/**
  * Attaches an event. Use this method to ensure cleanup through detach
  */
minikit.widget.Base.prototype.connect = function(src, sig, slot) {
	this._signalCache.push(connect(src, sig, slot));
}

minikit.widget.ContextMessage = function(args) {
	this.superconstructor.apply(this, arguments);
	this.title = args.title;
	this.message = args.message;
	this.icon = true && args.icon;
	this.appendTarget = false;
	this.classNames = {};
	this.classNames["header"] = "minikit-contextmessage-header";
	this.classNames["footer"] = "minikit-contextmessage-footer";
	this.classNames["main"] = "minikit-contextmessage-main";
	this.classNames["button"] = "minikit-contextmessage-button";
	this.classNames["button-hover"] = "minikit-contextmessage-button-hover";
	this.classNames["icon"] = "minikit-contextmessage-icon";
}
minikit.extend(minikit.widget.ContextMessage, minikit.widget.Base);

minikit.contextMessage = function(el, args, options) {
	if (!el) {
		el = document.body;
	}
	var f = function() {
		var widget = new minikit.widget.ContextMessage(args);
		widget.attach($(el));
	}
	if (options && options.delay) {
		callLater(1, f);
	} else {
		f();
	}
}

minikit.widget.ContextMessage.prototype.attach = function(target) {
	var pos = minikit.getElementPosition(target);
	this.view.container = createDOM("div");

	this.view.header = createDOM("div");
	this.view.header.className = this.classNames["header"];
	this.view.header.style.verticalAlign = "middle";
	this.view.header.innerHTML = this.title;
	this.view.main = createDOM("div");
	this.view.main.className = this.classNames["main"];
	this.view.main.innerHTML = this.message.replace(/\n/, "<br>");
	this.view.button = createDOM("span");
	this.view.button.className = this.classNames["button"];
	this.view.button.style.position = "absolute";
	this.view.button.style.right = "8px";
	this.view.button.style.top = "8px";
	this.view.header.appendChild(this.view.button);

	if (this.icon) {
		this.view.icon = createDOM("span");
		this.view.icon.className = this.classNames["icon"];
		this.view.icon.style.verticalAlign = "middle";
		this.view.icon.style.paddingRight = "8px";
		this.view.header.insertBefore(this.view.icon, this.view.header.firstChild);
	}

	this.view.container.appendChild(this.view.header);
	this.view.container.appendChild(this.view.main);
	this.view.container.style.position = "absolute";
	this.view.container.style.left = (pos.x + 20) + "px";

	if (this.appendTarget) {
		target.parentNode.appendChild(this.view.container);
	} else {
		document.body.appendChild(this.view.container);
	}
	this.view.container.style.top = (pos.y - this.view.container.offsetHeight - 24) + "px";
	
	this.view.footer = createDOM("div");
	this.view.footer.className = this.classNames["footer"];
	this.view.footer.style.height = "24px";
	this.view.footer.style.width = this.view.container.offsetWidth + "px";
	this.view.footer.appendChild(document.createTextNode(" "));
	this.view.container.appendChild(this.view.footer);

	this.connect(this.view.container, "onmouseover", bind(function() {
		this.view.button.className = this.classNames["button-hover"];
	}, this));
	this.connect(this.view.container, "onmouseout", bind(function() {
		this.view.button.className = this.classNames["button"];
	}, this));
	this.connect(this.view.container, "onclick", bind(function() {
		this.detach();
	}, this));

	return this.view.container;
}

minikit.widget.ContextMessage.prototype.detach = function() {
	this.supertype.detach.apply(this, arguments);
	this.view.container.parentNode.removeChild(this.view.container);
}

/**
  * A cross-browser datepicker widget.
  *
  * Copyright (c) 2004,2005,2006 Troels Knak-Nielsen
  *
  * License: public domain
  *
  * Version : 18. sep 2006
  */
minikit.widget.DatePicker = function(args) {
	this.superconstructor.apply(this, arguments);

	this.i18n = {};
	this.i18n.nullValue = "Not supplied";
	this.i18n.months = [
		"January", "February", "March", "April", "May", "June", "July",
		"August", "September", "October", "November", "December"
	];

	if (args) {
		this.mode = (args.mode) ? args.mode : minikit.widget.DatePicker.MODE_DATE;
		if (args.nullable) {
			this.nullable = true;
		}
		if (args.i18n) {
			for (var key in args.i18n) {
				this.i18n[key] = args.i18n[key];
			}
		}
	}

	// default values to start out with
	this.setValue(new Date());
	this.startYear = this.date.getRealYear() - 10;
	this.endYear = this.date.getRealYear() + 10;
}
minikit.extend(minikit.widget.DatePicker, minikit.widget.Base);

minikit.widget.DatePicker.MODE_DATE = 1;
minikit.widget.DatePicker.MODE_DATE_TIME = 2;
minikit.widget.DatePicker.MODE_DATE_TIME_SECONDS = 3;

minikit.datePicker = function(el, args, options) {
	var f = function() {
		var widget = new minikit.widget.DatePicker(args);
		widget.attach($(el));
	}
	if (options && options.delay) {
		callLater(1, f);
	} else {
		f();
	}
}

minikit.widget.DatePicker.extendDate = function(obj) {
	if (obj._extendedDate) return obj;
	obj.getRealYear = function() {
		if (this.getFullYear) {
			return parseInt(this.getFullYear());
		} else {
			var y = parseInt(this.getYear());
			if (y < 100) return y + 1900;
		}
		return y;
	};
	obj.setFromString = function(s) {
		var patternShort = new RegExp("^([0-9]{4})-([0-9]{2})-([0-9]{2})$");
		var patternFull = new RegExp("^([0-9]{4})-([0-9]{2})-([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})$");
		if (s.match(patternShort)) {
			pattern = patternShort;
		} else if (s.match(patternFull)) {
			pattern = patternFull;
		} else {
			throw new Error("Input string must be ISO 8601 formated date");
		}
		var matches = pattern.exec(s);
		if (this.setFullYear) {
			this.setFullYear(matches[1]);
		} else {
			this.setYear(matches[1]);
		}
		this.setMonth(matches[2] - 1);
		this.setDate(matches[3]);
		if (matches.length > 4) {
			this.setHours(matches[4]);
			this.setMinutes(matches[5]);
			this.setSeconds(matches[6]);
		}
	}
	obj._extendedDate = true;
	return obj;
}

minikit.widget.DatePicker.prototype.setValue = function(d) {
	if (d == null) {
		this.setValue(new Date());
		this.date = null;
		return;
	}
	if (d instanceof Date) {
		if (!d._extendedDate) {
			this.date = minikit.widget.DatePicker.extendDate(d);
		} else {
			this.date = d;
		}
	} else {
		this.date = minikit.widget.DatePicker.extendDate(new Date());
		this.date.setFromString(d);
	}
	if (this.date.getRealYear() < this.startYear) this.startYear = this.date.getRealYear();
	if (this.date.getRealYear() > this.endYear) this.endYear = this.date.getRealYear();
}

/**
  * Returns an ISO formatted datetime-string
  */
minikit.widget.DatePicker.prototype.getValue = function() {
	if (this.date == null) {
		return "";
	}
	var intToString = function(n) {
		if (n  < 10) return "0" + n;
		else return "" + n;
	};
	var str = this.date.getRealYear() + "-" + intToString(this.date.getMonth()+1) + "-" + intToString(this.date.getDate());
	if (this.mode == minikit.widget.DatePicker.MODE_DATE_TIME) {
		str += " " + intToString(this.date.getHours()) + ":" + intToString(this.date.getMinutes()) + ":00";
	} else 	if (this.mode == minikit.widget.DatePicker.MODE_DATE_TIME_SECONDS) {
		str += " " + intToString(this.date.getHours()) + ":" + intToString(this.date.getMinutes()) + ":" + intToString(this.date.getSeconds());
	}
	return str;
}

minikit.widget.DatePicker.prototype.attach = function(elm) {
	this.view = {};

	this.view.field = elm;
	if (elm.type.toLowerCase() != "hidden") {
		elm.style.display = "none";
	}
	var useDate;
	if (this.nullable && this.view.field.value == "") {
		this.setValue(new Date());
		useDate = this.date;
		this.date = null;
	} else {
		this.setValue(this.view.field.value);
		useDate = this.date;
	}

	var extendSelect = function(obj) {
		obj._removeItem = function(value) {
			var len = this.length;
			for (var i=0; i<len ; i++) {
				if (this.options[i] != null) {
					if (this.options[i].value == value) {
						this.options[i] = null;
						return true;
					}
				}
			}
			return false;
		}

		obj._addItem = function(value, key) {
			this._removeItem(value);
			if (!key) key = value;
			this.options[this.length] = new Option(key, value);
		}

		obj._selectItem = function(value) {
			var len = this.length;
			for (var i=0; i<len ; i++) {
				if (this.options[i].value == value) {
					this.options[i].selected = true;
					return true;
				}
			}
			return false;
		}

		obj._getSelectedValue = function() {
			return this.options[this.selectedIndex].value;
		}
		return obj;
	}

	var container = createDOM("DIV");
	container.className = "minikit-datepicker";
	this.view.container = container;
	this.view.field.parentNode.insertBefore(container, this.view.field);

	this.view.inputs = {};
	this.view.inputs.day = extendSelect(createDOM("SELECT"));
	for (var i=1; i <= 31; i++) {
		var option = createDOM("OPTION");
		option.setAttribute("value", i);
		option.appendChild(document.createTextNode(i));
		this.view.inputs.day.appendChild(option);
	}
	this.view.container.appendChild(this.view.inputs.day);
	this.connect(this.view.inputs.day, "onchange", bind(this.viewChanged, this));
	this.view.inputs.day._selectItem(useDate.getDate());

	this.view.container.appendChild(document.createTextNode(" "));

	this.view.inputs.month = extendSelect(createDOM("SELECT"));
	for (var i=1; i <= 12; i++) {
		var option = createDOM("OPTION");
		option.setAttribute("value", i);
		option.appendChild(document.createTextNode(this.i18n.months[i-1]));
		this.view.inputs.month.appendChild(option);
	}
	this.view.container.appendChild(this.view.inputs.month);
	this.connect(this.view.inputs.month, "onchange", bind(this.viewChanged, this));
	this.view.inputs.month._selectItem(useDate.getMonth()+1);

	this.view.container.appendChild(document.createTextNode(" "));

	this.view.inputs.year = extendSelect(createDOM("SELECT"));
	for (var i = this.startYear; i <= this.endYear; i++) {
		var option = createDOM("OPTION");
		option.setAttribute("value", i);
		option.appendChild(document.createTextNode(i));
		this.view.inputs.year.appendChild(option);
	}
	this.view.container.appendChild(this.view.inputs.year);
	this.connect(this.view.inputs.year, "onchange", bind(this.viewChanged, this));
	this.view.inputs.year._selectItem(useDate.getRealYear());

	if (this.mode == minikit.widget.DatePicker.MODE_DATE_TIME || this.mode == minikit.widget.DatePicker.MODE_DATE_TIME_SECONDS) {
		var keyDownHandler = function(event) {
			var flag = false;
			if (event.key().code == 40) {
				this.value = parseInt(parseFloat(this.value)) - 1;
				signal(this, "onchange");
				flag = true;
			}
			if (event.key().code == 38) {
				this.value = parseInt(parseFloat(this.value)) + 1;
				signal(this, "onchange");
				flag = true;
			}
			if (event.key().code == 34) {
				this.value = parseInt(parseFloat(this.value)) - 10;
				signal(this, "onchange");
				flag = true;
			}
			if (event.key().code == 33) {
				this.value = parseInt(parseFloat(this.value)) + 10;
				signal(this, "onchange");
				flag = true;
			}

			if (flag) {
				try {
					if (document.selection && document.selection.createRange) { // ie
						var txtrange = this.createTextRange();
						txtrange.moveStart("character", 0);
						txtrange.select();
					} else {
						this.selectionStart = 0;
						this.selectionEnd = this.value.length;
					}
				} catch (ex) {}
				event.stop();
			}
		}

		this.view.container.appendChild(document.createTextNode(" "));
		this.view.inputs.hour = createDOM("INPUT", {type: "text", size: 2, maxlength: 2});
		this.view.inputs.hour.style.width = "2em";
		this.view.container.appendChild(this.view.inputs.hour);
		this.connect(this.view.inputs.hour, "onchange", bind(this.viewChanged, this));
		this.connect(this.view.inputs.hour, "onkeydown", bind(keyDownHandler, this.view.inputs.hour));
		this.view.inputs.hour.value = useDate.getHours();

		this.view.container.appendChild(document.createTextNode(" "));
		this.view.inputs.minute = createDOM("INPUT", {type: "text", size: 2, maxlength: 2});
		this.view.inputs.minute.style.width = "2em";
		this.view.container.appendChild(this.view.inputs.minute);
		this.connect(this.view.inputs.minute, "onchange", bind(this.viewChanged, this));
		this.connect(this.view.inputs.minute, "onkeydown", bind(keyDownHandler, this.view.inputs.minute));
		this.view.inputs.minute.value = useDate.getMinutes();

		if (this.mode == minikit.widget.DatePicker.MODE_DATE_TIME) {
			this.view.inputs.second = createDOM("INPUT", {type: "hidden"});
			this.view.container.appendChild(this.view.inputs.second);
		} else {
			this.view.container.appendChild(document.createTextNode(" "));
			this.view.inputs.second = createDOM("INPUT", {type: "text", size: 2, maxlength: 2});
			this.view.inputs.second.style.width = "2em";
			this.view.container.appendChild(this.view.inputs.second);
			this.connect(this.view.inputs.second, "onkeydown", bind(keyDownHandler, this.view.inputs.second));
		}
		this.connect(this.view.inputs.second, "onchange", bind(this.viewChanged, this));
		this.view.inputs.second.value = useDate.getSeconds();
	}
	if (this.nullable) {
		this.view.inputs.isnull = createDOM("INPUT", {type: "checkbox", id: this.view.field.id + "-null"});
		if (this.date == null) {
			this.view.inputs.isnull.setAttribute("checked", true);
		}
		this.view.label = createDOM("LABEL", {"for": this.view.field.id + "-null"});
		this.view.label.className = "minikit-datepicker-label";
		this.connect(this.view.inputs.isnull, "onchange", bind(this.onNullChange, this));
		var doBlur = bind(function() { this.blur(); }, this.view.inputs.isnull);
		this.connect(this.view.inputs.isnull, "onclick", doBlur);
		this.connect(this.view.label, "onclick", doBlur);
		this.view.label.appendChild(document.createTextNode(this.i18n.nullValue));
		this.view.container.appendChild(this.view.inputs.isnull);
		this.view.container.appendChild(this.view.label);
	}


	this.viewChanged();
	return this.view.container;
}

minikit.widget.DatePicker.prototype.onNullChange = function() {
	if (!this.view.inputs.isnull.checked) {
		this.setValue(new Date());
		this.viewChanged();
	} else {
		this.setValue(null);
		this.view.field.value = this.getValue();
		this.viewChanged();
	}
}

minikit.widget.DatePicker.prototype.viewChanged = function() {
	if (this.date == null) {
		this.view.inputs.day.disabled = true;
		this.view.inputs.month.disabled = true;
		this.view.inputs.year.disabled = true;
		if (this.view.inputs.hour) {
			this.view.inputs.hour.disabled = true;
			this.view.inputs.minute.disabled = true;
			this.view.inputs.second.disabled = true;
		}
		return;
	}
	this.view.inputs.day.disabled = false;
	this.view.inputs.month.disabled = false;
	this.view.inputs.year.disabled = false;
	if (this.view.inputs.hour) {
		this.view.inputs.hour.disabled = false;
		this.view.inputs.minute.disabled = false;
		this.view.inputs.second.disabled = false;
	}

	var day = this.view.inputs.day._getSelectedValue();
	var month = this.view.inputs.month._getSelectedValue();
	var year = this.view.inputs.year._getSelectedValue();

	this.view.inputs.day._addItem(29);
	this.view.inputs.day._addItem(30);
	this.view.inputs.day._addItem(31);

	// short month
	if (month == 4 || month == 6 || month == 9 || month == 11) {
		this.view.inputs.day._removeItem(31);
	}
	// february
	if (month == 2) {
		this.view.inputs.day._removeItem(31);
		this.view.inputs.day._removeItem(30);
	}
	// leap year
	var isLeap = (year % 4) == 0;
	if (month == 2 && !isLeap) {
		this.view.inputs.day._removeItem(29);
	}

	this.view.inputs.day._selectItem(day);

	this.date.setDate(day);
	this.date.setMonth(month - 1);
	if (this.date.setFullYear) {
		this.date.setFullYear(year);
	} else {
		this.date.setYear(year);
	}

	if (this.mode == minikit.widget.DatePicker.MODE_DATE_TIME || this.mode == minikit.widget.DatePicker.MODE_DATE_TIME_SECONDS) {
		var num = parseInt(parseFloat(this.view.inputs.hour.value));
		if (isNaN(num)) num = 0;
		if (num > 23) num = 0;
		if (num < 0) num = 23;
		if (num < 10) num = "0" + num;
		this.view.inputs.hour.value = num;
		this.date.setHours(num);

		num = parseInt(parseFloat(this.view.inputs.minute.value));
		if (isNaN(num)) num = 0;
		if (num > 59) num = 0;
		if (num < 0) num = 59;
		if (num < 10) num ="0" + num;
		this.view.inputs.minute.value = num;
		this.date.setMinutes(num);

		num = parseInt(parseFloat(this.view.inputs.second.value));
		if (isNaN(num)) num = 0;
		if (num > 59) num = 0;
		if (num < 0) num = 59;
		if (num < 10) num ="0" + num;
		this.view.inputs.second.value = num;
		this.date.setSeconds(num);
	}
	this.view.field.value = this.getValue();
}

minikit.widget.DatePicker.prototype.detach = function() {
	this.supertype.detach.apply(this, arguments);
	this.view.container.parentNode.removeChild(this.view.container);
	if (this.view.field.type.toLowerCase() != "hidden") {
		this.view.field.style.display = "";
	}
}

/**
  * A widget for controlling unix-type permissions
  *
  * Copyright (c) 2005,2006 Troels Knak-Nielsen
  *
  * License: public domain
  *
  * Version : 18. mar 2006
  */
minikit.widget.Permissions = function(args) {
	this.superconstructor.apply(this, arguments);
	this.i18n = {};
	this.i18n.user = "User";
	this.i18n.group = "Group";
	this.i18n.world = "World";
	this.i18n.read = "read";
	this.i18n.write = "write";
	this.i18n.execute = "execute";

}
minikit.extend(minikit.widget.Permissions, minikit.widget.Base);

minikit.widget.Permissions.PRIVILEGE_READ = 4;
minikit.widget.Permissions.PRIVILEGE_WRITE = 2;
minikit.widget.Permissions.PRIVILEGE_EXTENDED = 1;

minikit.permissions = function(el, args, options) {
	var f = function() {
		var widget = new minikit.widget.Permissions(args);
		widget.attach($(el));
	}
	if (options && options.delay) {
		callLater(1, f);
	} else {
		f();
	}
}

minikit.widget.Permissions.prototype._parseToStruct = function() {
	var mode = parseInt(this.view.field.value).toString(8);
	for (var l=mode.length;l < 3;++l) {
		mode = "0" + mode;
	}
	return {
		user : this._parseModeToStruct(mode.charAt(0)),
		group : this._parseModeToStruct(mode.charAt(1)),
		world : this._parseModeToStruct(mode.charAt(2))
	};
}

minikit.widget.Permissions.prototype._parseModeToStruct = function(mode) {
	return {
		read : (mode & minikit.widget.Permissions.PRIVILEGE_READ),
		write : (mode & minikit.widget.Permissions.PRIVILEGE_WRITE),
		execute : (mode & minikit.widget.Permissions.PRIVILEGE_EXTENDED)
	};
}

minikit.widget.Permissions.prototype.updateFromStruct = function(struct) {
	var perms = "";
	for (var subject in struct) {
		var val = 0;
		if (struct[subject].read) {
			val += minikit.widget.Permissions.PRIVILEGE_READ;
		}
		if (struct[subject].write) {
			val += minikit.widget.Permissions.PRIVILEGE_WRITE;
		}
		if (struct[subject].execute) {
			val += minikit.widget.Permissions.PRIVILEGE_EXTENDED;
		}
		perms += val.toString(8);
	}
	this.view.field.value = parseInt(perms, 8);
}

minikit.widget.Permissions.prototype.onboxchange = function(args) {
	var struct = this._parseToStruct();
	struct[args.subject][args.mode] = args.checked;
	this.updateFromStruct(struct);
}

minikit.widget.Permissions.prototype.updateView = function() {
	var struct = this._parseToStruct();
	for (subject in struct) {
		for (mode in struct[subject]) {
			this.view[subject][mode].checked = struct[subject][mode];
		}
	}
}

minikit.widget.Permissions.prototype.attach = function(field) {
	this.view = {};

	this.view.field = field;
	if (field.type != "hidden") {
		field.style.display = "none";
	}


	var container = createDOM("DIV");
	this.view.container = container;
	this.view.field.parentNode.insertBefore(container, this.view.field);


	addsToBox = function(target, obj, subject, mode) {
		this.connect(target, "onclick", function(e) {
			obj.onboxchange({ subject : subject, mode : mode, checked : target.checked });
		});
	}

	var struct = this._parseToStruct();
	for (subject in struct) {
		this.view[subject] = {};
		this.view[subject].fieldset = createDOM("FIELDSET");
		var legend = this.view[subject].fieldset.appendChild(createDOM("LEGEND"));
		legend.appendChild(document.createTextNode(this.i18n[subject]));
		this.view[subject].fieldset.style.width = "5em";
		this.view[subject].fieldset.style.display = "inline";
		this.view[subject].fieldset.style.margin = ".5em";
		for (mode in struct[subject]) {
			var id = this.view.field.id + "-chk-"+subject+"-"+mode;
			this.view[subject][mode] = this.view[subject].fieldset.appendChild(createDOM("INPUT", {type: "checkbox", id: id}));
			var label = this.view[subject].fieldset.appendChild(createDOM("LABEL", {"for": id}));
			addsToBox(this.view[subject][mode], this, subject, mode);
			label.appendChild(document.createTextNode(" "+this.i18n[mode]));
			this.view[subject].fieldset.appendChild(createDOM("BR"));
		}
		container.appendChild(this.view[subject].fieldset);
	}

	this.connect(this.view.field, "onchange", bind(this.updateView, this));
	this.updateView();
	return this.view.container;
}

minikit.widget.Permissions.prototype.detach = function() {
	this.supertype.detach.apply(this, arguments);
	this.view.container.parentNode.removeChild(this.view.container);
	if (this.view.field.type.toLowerCase() != "hidden") {
		this.view.field.style.display = "";
	}
}

/**
  * Copyright (c) 2006 Troels Knak-Nielsen
  *
  * License: public domain
  *
  * Makes a regular table tbody-scrollable
  */
minikit.scrollTable = function(table, /* optional */ options) {
	table = $(table);
	if (options && options.height) {
		var height = height;
	} else {
		var height = "10em";
	}
	var table2 = createDOM("table", {"class": table.className});
	var thead = table.getElementsByTagName("thead").item(0);

	var ws = [];
	forEach(
		thead.getElementsByTagName("tr").item(0).getElementsByTagName("th"),
		function(th) {
			ws.push(minikit.getElementDimensions(th).w);
		}
	);

	var tbodies = table.getElementsByTagName("tbody");
	for (var i=0; i < tbodies.length; ++i) {
		table2.appendChild(table.removeChild(tbodies[i]));
	}

	var container = createDOM("div");
	container.appendChild(table2);
	container.style.overflow = "auto";
	container.style.height = height;

	var lastWidth = -1;
	var renderView = function(init) {
		var tableWidth = minikit.getElementDimensions(table).w;
		if (lastWidth == -1 || tableWidth != lastWidth) {
			forEach(
				[table, table2],
				function(t) {
					forEach(
						t.getElementsByTagName("tr"),
						function(tr) {
							var i = 0;
							forEach(
								tr.childNodes,
								function(node) {
									if (node.nodeName && (node.nodeName.toLowerCase() == "th" || node.nodeName.toLowerCase() == "td")) {
										node.style.width = ws[i] + "px";
										++i;
									}
								}
							);
						}
					)
				}
			);
			container.style.width = tableWidth + "px";
		}
		lastWidth = tableWidth;
		callLater(1, renderView);
	}
	var parent = table.parentNode;
	parent.insertBefore(container, table);
	parent.removeChild(table);
	parent.insertBefore(table, container);
	renderView(true);
}

/**
  * Copyright (c) 2004,2005,2006 Troels Knak-Nielsen
  *
  * License: public domain
  *
  * Combobox widget
  */
minikit.widget.ComboBox = function(values, options) {
	this.superconstructor.apply(this, arguments);
	this.values = values || [];
	// would be real nice to have a way to figure this out
	this.buttonWidth = 19;
	if (options && options.buttonWidth) {
		this.buttonWidth = options.buttonWidth;
	}
}
minikit.extend(minikit.widget.ComboBox, minikit.widget.Base);

minikit.comboBox = function(el, values, options) {
	var f = function() {
		var widget = new minikit.widget.ComboBox(values, options);
		widget.attach($(el));
	}
	if (options && options.delay) {
		callLater(1, f);
	} else {
		f();
	}
}

minikit.widget.ComboBox.prototype.attach = function(elm) {
	this.view = {};
	this.view.textfield = elm;
	elm.setAttribute("autocomplete", "off");

	this.connect(elm, "onkeyup", bind("completeTyping", this));
	this.connect(elm, "onkeydown", bind("txtKeyDown", this));
	elm.style.marginRight = (this.buttonWidth + 1) + "px";

	var select = createDOM("select");
	this.view.select = select;
	this.connect(select, "onchange", bind("takeValueFromPopup", this));
	select.tabIndex = -1;
	select.style.visibility = "hidden";
	select.style.position = "absolute";
	forEach(this.values,
		function(value) {
			var option = createDOM("option");
			option.value = value;
			option.appendChild(document.createTextNode(value));
			select.appendChild(option);
		}
	);
	elm.parentNode.appendChild(select);
	this.takeValueFromTextfield();

	select.style.width = (minikit.getElementDimensions(elm).w + this.buttonWidth) + "px";
	var dims = minikit.getElementDimensions(select);
	select.style.clip = 'rect(0px ' + dims.w + 'px ' + dims.h + 'px ' + (dims.w - this.buttonWidth) + 'px)';
	select.style.visibility = 'visible';
	this.positionSelect();

}

minikit.widget.ComboBox.prototype.detach = function() {
	this.supertype.detach.apply(this, arguments);
	this.view.select.parentNode.removeChild(this.view.select);
}

minikit.widget.ComboBox.prototype.positionSelect = function() {
	var s = this.view.select;

	var dims = minikit.getElementDimensions(this.view.select);
	var dimt = minikit.getElementDimensions(this.view.textfield);
	var post = minikit.getElementPosition(this.view.textfield);
	
	s.style.top = post.y + "px";
	s.style.left = ((post.x + dimt.w) - (dims.w - this.buttonWidth) - 1) + "px";
	
	callLater(1, bind("positionSelect", this));
}

minikit.widget.ComboBox.prototype.takeValueFromPopup = function() {
	this.view.textfield.value = this.view.select.value;
}

minikit.widget.ComboBox.prototype.takeValueFromTextfield = function() {
	var t = this.view.textfield;
	var s = this.view.select;
	for (var idx=0; idx < s.options.length; idx++) {
		if (s.options[idx].text == t.value) {
			s.selectedIndex = idx;
			return;
		}
	}
	s.selectedIndex=-1;
}

minikit.widget.ComboBox.prototype.completeTyping = function(e) {
	var code = e.key().code;
	//window.status="key = "+code;
	if (code < 0x2f && code != 32) {
		return;
	}
	var t = this.view.textfield;
	var s = this.view.select;

	var text = t.value;
	var options = s.options;
	var i;
	var utext = text.toUpperCase();
	for (i=0;i<options.length;i++) {
		var newtxt = options[i].text;
		var uopt = newtxt.toUpperCase();
		if (uopt != utext && 0 == uopt.indexOf(utext)) {
			t.value = text + newtxt.substr(text.length);
			if (document.selection && document.selection.createRange) { // ie
				var txtrange = t.createTextRange();
				txtrange.moveStart("character", text.length);
				txtrange.select();
			} else {
				t.selectionStart = text.length;
				t.selectionEnd = newtxt.length;
			}
			this.takeValueFromTextfield();
			break;
		}
	}
}

minikit.widget.ComboBox.prototype.txtKeyDown = function(e) {
	var code = e.key().code;
	// Down Arrow
	if (code == 40) {
		var s = this.view.select;
		if (s.selectedIndex < s.options.length-1) {
			s.selectedIndex += 1;
		}
		this.takeValueFromPopup();
	}
	// Up Arrow
	if (code == 38) {
		var s = this.view.select;
		if (s.selectedIndex > 0) {
			s.selectedIndex -= 1;
		} else if (s.selectedIndex == -1) {
			s.selectedIndex = s.options.length-1;
		}
		this.takeValueFromPopup();
	}
}

__EXPORT__(window);