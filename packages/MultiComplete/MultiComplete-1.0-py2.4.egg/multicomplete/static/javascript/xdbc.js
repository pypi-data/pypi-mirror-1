           /*3OGGO3(^
       ~Q@@@BBBBB@#(B@@S/
     O@@BBBBBBBBBB@O R@B@@O
    O@BBB@@@@@@BBB@G S@@@@@O		XDBC::AJAX Codebase 2.01
  /B@BBB@t    /#@B@( //     /		Controlled by Hakan Bilgin © 2006
 ~@BBB@R(       BB~   /tC/  %@/		http://www.challenger.se
 O@BB@#CCQ##s  /R(  e#@@O  C@@s
/@BBBBBBBBB@O (@( /@#7 /6R@@BB@/
%@BBBBBBB@B~ KR    ^(CG3   t@B@%
3@BBBBBB@O (@R   Q@@@@Q^ /#@BB@%
%@BBBBB@#  K@e   K@@BC  tR@BBB@t
^B@B@SC3  »%   ^^ /sB@BBBBB@R^R
 %KC/      //(     C@@BBBBBBB@t
  QQQ#G    e@@/     C@BBBBBB@R
   K@@#   sRRB@%S@@@(C@BBBB@Q
    (B@K 7@BBBBBBBB@S6@BB@R/
     ~R@G e@BBBBBBB@GS@B@#/			This code is licensed under a Creative Commons License.
        (#@S#@BBBB@#Q@Q(			http://creativecommons.org/licenses/LGPL/2.1/
             ^/~~/*/


/*	EXTENDS STRING	*/
String.prototype.trim			= function()	{return this.replace(/(^\s*)|(\s*$)/g,'');}
String.prototype.fill			= function(i,c)	{var str = this; c = c || ' '; for (; str.length<i; str+=c){}; return str;}
String.prototype.friendlyHTML	= function()	{return this.replace(/<scrip.*?>|<\/script>|<applet.*?>|<\/applett>|<embe.*?>|<objec.*?>.*?<\/object>/ig, '').replace(/ on.+?=.+?>/ig, '>').replace(/ href=.javascript:.+?.>/ig, '>');}
String.prototype.stripHTML		= function()	{return this.replace(/<.*?>/g, '');}
String.prototype.stripNS		= function()	{return this.replace(/<hbi:.*?>|<\/hbi:.*?>/g, '');}

/*	ENVIRONMENT	*/
env = {
	avbl : ['sv', 'tr', 'en'],
	ie : /msie/i.test(navigator.userAgent),		//	Internet Explorer
	gk : /gecko/i.test(navigator.userAgent),	//	Gecko based browsers
	ff : /firefox/i.test(navigator.userAgent),	//	Firefox browsers
	sf : /safari/i.test(navigator.userAgent),	//	Safari
	ax : typeof(ActiveXObject) == 'function',	//	Is ActiveXObject supported
	xhr : typeof(XMLHttpRequest) == 'function'	//	Is XMLHttpRequest supported
}
env.lng = (new RegExp(navigator.userLanguage,'i').test(env.avbl))? navigator.userLanguage : 'en';

/*	EXTENDS GECKO	*/
if (env.ff) {
	Node.prototype.setCapture =				function()		{}
	Node.prototype.releaseCapture =			function()		{}
	Node.prototype.fireEvent =				function(eType) {var e = document.createEvent('MouseEvents'); e.initEvent(eType.slice(2), true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null); this.dispatchEvent(e);}
	Node.prototype.attachEvent =			function(e, h)	{this.addEventListener(e.slice(2), h, false);};
	Node.prototype.detachEvent =			function(e, h)	{this.removeEventListener(e.slice(2), h, false);};
	Document.prototype.selectNodes =		function(XPath, XNode) {if(!XNode) XNode = this; this.ns = this.createNSResolver(this.documentElement); this.qI = this.evaluate(XPath, XNode, this.ns, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null); aResult = []; for(i=0; i<this.qI.snapshotLength; i++) aResult[i] = this.qI.snapshotItem(i); return aResult;}
	Document.prototype.selectSingleNode =	function(XPath, XNode) {if(!XNode) XNode = this; this.xI = this.selectNodes(XPath, XNode); return (this.xI.length > 0)? this.xI[0] : null ;}
	Element.prototype.selectNodes =			function(XPath) {return this.ownerDocument.selectNodes(XPath, this);}
	Element.prototype.selectSingleNode =	function(XPath) {return this.ownerDocument.selectSingleNode(XPath, this);}
	
	Node.prototype.__defineGetter__('xml',			function()		{return (new XMLSerializer()).serializeToString(this);});
	Node.prototype.__defineGetter__('outerHTML',	function()		{return (new XMLSerializer()).serializeToString(this);});
	Node.prototype.__defineSetter__('outerHTML',	function(s)		{var rng = this.ownerDocument.createRange(); rng.setStartBefore(this); cFrag = rng.createContextualFragment(s); this.parentNode.replaceChild(cFrag, this);});
	Node.prototype.__defineSetter__('innerText',	function(s)		{this.innerHTML = s.replace(/</g, '&lt;').replace(/\n/g, '<br>');});
	Node.prototype.__defineGetter__('currentStyle', function()		{return getComputedStyle(this, null);});
	Node.prototype.__defineSetter__('onreadystatechange', function(b) {this.readyState = 'complete'; this.onload = b;});
	/* Event */
	Event.prototype.__defineGetter__('event',		function()		{return this;});
	Event.prototype.__defineGetter__('clientY',		function()		{return this.pageY;});
	Event.prototype.__defineGetter__('clientX',		function()		{return this.pageX;});
	Event.prototype.__defineGetter__('offsetY',		function()		{return this.layerY;});
	Event.prototype.__defineGetter__('offsetX',		function()		{return this.layerX;});
	Event.prototype.__defineGetter__('srcElement',	function()		{var node = this.target; while (node && node.nodeType != 1) node = node.parentNode; return node;});
	Event.prototype.__defineSetter__('cancelBubble',function(b)		{if (b) this.stopPropagation();});
	Event.prototype.__defineSetter__('returnValue',	function(b)		{if (!b) this.preventDefault();});
	
	$e = ['click', 'dblclick', 'mouseover', 'mouseout', 'mousedown', 'mouseup', 'mousemove', 'keydown', 'keypress', 'keyup', 'focus', 'blur'];
	for (i=0; i<$e.length; i++) document.addEventListener($e[i], function(e) {window.event=e;}, true);
}

/*	DOM EXPLORERS	*/
function $(s) {
	return (typeof(s) == 'string')? document.getElementById(s) : s ;
}
function getSrcIndex($el) {
	var i=0;
	while ($el.previousSibling) {
		$el=$el.previousSibling;
		if ($el.nodeType != 3) i++;
	}
	return i;
}
function getChildren(el, a, v) {
	var ar = new Array();
	var ac = $(el).getElementsByTagName('*');
	for (c=0; c<ac.length; c++) if (v? (ac[c][a] == v || ac[c].getAttribute(a) == v) : (ac[c][a] || ac[c].getAttribute(a))) {
		ar.push(ac[c]);
	}
	return ar;
}
function getParent(el, a, v) {
	while (v? (el && el[a] != v && el.getAttribute(a) != v) : (el && !el[a] && !el.getAttribute(a))) {
		if (el == document.firstChild) return null;
		el = el.parentNode;
	}
	return el;
}
function getDim(el, a, v) {
	var a = a || 'nodeName';
	var v = v || 'BODY';
	var point = {w:el.offsetWidth, h:el.offsetHeight, t:0, l:0}
	while (el && el[a] != v && el.getAttribute(a) != v) {
		if (el == document.firstChild) return null;
		point.t += el.offsetTop;
		point.l += el.offsetLeft;
		el = el.offsetParent;
	}
	point.obj = el;
	return point;
}

/*	XDBC	*/
xdbc = {
	debug		: false,
	escStr		: ['"=$34;', '\'=$39;', '<=$60;', '>=$62;'],
	xslPath		: '/include/xsl/',
	xslt		: function($xslId)	{return xdbc.ledger.selectSingleNode('//_doc[@title=\'doctype\']/*[@id='+ $xslId +']').getAttribute('data');},
	createNode	: function(name)	{return !env.xhr? xdbc.que.parentNode.createNode(1, name, '') : xdbc.que.parentNode.createElement(name);},
	flushQue	: function()		{while (xdbc.que.firstChild) xdbc.que.removeChild(xdbc.que.firstChild);},
	cmd			: function($cmdId)	{return xdbc.ledger.selectSingleNode('//*[@_cmdId=\''+ $cmdId +'\']').cloneNode(false);},
	uniqId : function (l) {
		var l = l || 16;
		var a = 'abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890';
		var s = a.charAt((Math.random()*50));
		var d = new Date().valueOf();
		var k = Math.random().toString().slice(2);
		for (r=0; r<l; r++) s += a.charAt((Math.random()*256)%a.length);
		return s.slice(0,l);
	},
	init : function() {
		xdbc.prefix();
		xdbc.xslDoc = new Array();
		xdbc.que = xdbc.load('<data></data>').documentElement;
	},
	load : function(xSrc, xCallback, wantJSON) {
		if (xSrc.indexOf('<') > -1) {
			if (env.ax) {
				var xDom = new ActiveXObject(xdbc.otype['DomDocument']);
				if (xDom.loadXML(xSrc)) return xDom;
			} else if (env.gk) {
				var xDom = new DOMParser().parseFromString(xSrc, 'text/xml');
				if (xDom.firstChild.nodeName != 'parsererror') return xDom;
			}
			xdbc.ctrlXml(false, xSrc);
		} else {
			var xhr = {
				src		 : xSrc,
				callback : (typeof(xCallback) == 'function')? xCallback : null,
				async	 : (typeof(xCallback) != 'undefined'),
				http	 : env.ax? new ActiveXObject(xdbc.otype['XmlHttp']) : new XMLHttpRequest()
			};
			xhr.http.open('GET', xSrc +'?tg_random='+ xdbc.uniqId(), xhr.async);
			xhr.http.send('');
			if (xhr.async) {
				if (xhr.http.readyState == 4) {
				    if (wantJSON) {
				        if (xhr.callback) {
				            js_obj = eval('(' + xhr.http.responseText + ')');
				            xhr.callback(js_obj);
				        }
				    } else {
    					xhr.dom = xdbc.ctrlXml(xhr.http.responseXML, xhr.src);
    					if (xhr.callback) xhr.callback(xhr.dom);
    				}
					return xhr;
				} else {
					xhr.http.onreadystatechange = function() {
						if (xhr.http.readyState != 4) return;
    				    if (wantJSON) {
    				        if (xhr.callback) {
    				            js_obj = eval('(' + xhr.http.responseText + ')');
    				            xhr.callback(js_obj);
    				        }
    				    } else {
        					xhr.dom = xdbc.ctrlXml(xhr.http.responseXML, xhr.src);
        					if (xhr.callback) xhr.callback(xhr.dom);
        				}
					}
					return xhr;
				}
			} else return xdbc.ctrlXml(xhr.http.responseXML, xhr.src);
		}
	},
	ctrlXml : function(xObj, xSrc) {
		xSrc = xSrc || '';
		if (!env.ie && xObj == null || xObj.xml.indexOf('<parsererror') > 0) xObj = false;
		return (typeof(xObj) == 'object' && xObj.xml != '')? xObj : xdbc.doError('Invalid XML structure:\n'+ xSrc);
	},
	prefix : function() {
		xdbc.otype = new Array();
		var t = ['DomDocument', 'XmlHttp'];
		var b = ['Microsoft', 'MSXML', 'MSXML2', 'MSXML3'];
		for (n=0; n<t.length; n++) {
			for (p=0; p<b.length; p++) {
				try {
					new ActiveXObject(b[p] +'.'+ t[0]);
					xdbc.otype[t[n]] = b[p] +'.'+ t[n];
				}
				catch (e) {/* REPORT TO DOERROR? */}
			}
		}
	},
	xml2str : function(xDom) {
		if (xDom.xml) return xDom.xml;
		else return (new XMLSerializer()).serializeToString(xDom);
	},
	xslRam : function($src, $callback) {
		if (xdbc.xslDoc[$src]) return xdbc.xslDoc[$src];
		else {
			var callback = $callback || true;
			xdbc.xslDoc[$src] = xdbc.load(xdbc.xslPath + $src +'.xsl', callback);
			return xdbc.xslDoc[$src];
		}
	},
	htmlChar : function(sFrag) {
		sFrag = sFrag.replace(/<\?xml.+?\?>/i, '');
		sFrag = sFrag.replace(/&amp;/ig, '&');
		sFrag = sFrag.replace(/&lt;/ig, '<');
		sFrag = sFrag.replace(/&gt;/ig, '>');
		return sFrag;
	},
	transform : function($xml, $xsl, $el, $callback) {
		if (typeof($xml) == 'string') $xml = xdbc.load($xml, true);
		if (typeof($xsl) == 'string') $xsl = xdbc.xslRam($xsl);
		if (!$xml.dom && $xml.documentElement || $xml.xml) $xml = {dom:$xml}
		if (!$xsl.dom && $xsl.documentElement) $xsl = {dom:$xsl}
		if (!$xml.dom || !$xsl.dom) {
			setTimeout(function() {
				xdbc.transform($xml, $xsl, $el, $callback);
			}, 500);
			return;
		}
		xdbc.transform.recentXML = $xml.dom;
		$el = $($el);
		if (env.ax) {
			var frg = $xml.dom.transformNode($xsl.dom.documentElement);
			if (typeof($el) == 'function') $el(xdbc.htmlChar(frg));
			else $el.innerHTML = xdbc.htmlChar(frg);
		} else {
			var xslPrc = new XSLTProcessor();
			xslPrc.importStylesheet($xsl.dom);
			var frg = xdbc.htmlChar(xslPrc.transformToFragment($xml.dom, document).xml);
			
			if (typeof($el) == 'function') $el(frg);
			else {
				var rng = $el.ownerDocument.createRange();
				rng.setStartBefore($el);
				while ($el.firstChild) $el.removeChild($el.firstChild);
				$el.appendChild(rng.createContextualFragment(frg));
			}
		}
		if ($callback) {
			var $cb_param = ($callback.indexOf('(') > -1)? '' : '(xdbc.transform.recentXML);';
			try {eval($callback + $cb_param);}
			catch (e) {/* REPORT TO DOERROR? */};
		}
		$xml = $xsl = null;
	},
	escape : function($iStr) {
		for ($e=0; $e<xdbc.escStr.length; $e++) 
			$iStr = $iStr.replace(new RegExp(xdbc.escStr[$e].slice(0,1), 'g'), xdbc.escStr[$e].slice(2));
		return $iStr;
	},
	unescape : function(xml) {
		var xAll = xml.selectNodes('//*');
		for (x=0; x<xAll.length; x++) {
			if (!xAll[x].attributes) continue;
			for (a=0; a<xAll[x].attributes.length; a++) {
				xVal = unescape(xAll[x].attributes.item(a).value);
				xAll[x].attributes.item(a).value = xVal;
			}
		}
	},
	normalize : function(str) {
		str = escape(str);
		str = str.replace(/%20/ig, ' ');
		str = str.replace(/%3A/ig, ':');
		return str;
	},
	prepQue : function() {
		var qAll = xdbc.que.selectNodes('//*');
		for (x=0; x<qAll.length; x++) {
			for (a=0; a<qAll[x].attributes.length; a++) {
				var qNodeVal = qAll[x].attributes.item(a).value;
				qAll[x].attributes.item(a).value = (qAll[x].attributes.item(a).name.slice(0,1) == '_')?
													xdbc.escape(qNodeVal) : xdbc.normalize(qNodeVal);
			}
		}
	},
	addQue : function($pNode) {
		if (typeof($pNode) != 'object') return;
		var $pNode = $pNode.cloneNode(false);
		var $nAttr = $pNode.getAttribute('_selby');
		if ($nAttr) {
			for ($a=1; $a<arguments.length; $a++) $nAttr = $nAttr.replace(new RegExp('\\$prm'+ ($a), 'g'), arguments[$a]);
			$pNode.setAttribute('_selby', $nAttr);
		}
		if (xdbc.token) $pNode.setAttribute('_token', xdbc.token);
		return xdbc.que.appendChild($pNode);
	},
	doError : function(xhr) {
		if (typeof(xhr) == 'object') {
			if (xhr.xml) xhr = {dom:xhr}
			with (xhr.dom.firstChild) {
				var code = getAttribute('code');
				var desc = getAttribute('description');
				var text = text;
			}
			xdbc.recentError = 'ERROR ['+ code +']: ';
			xdbc.recentError += desc +'\n-------\n';
			xdbc.recentError += text +'\n-------';
		} else {
			xdbc.recentError = '\n-------\n'+ xhr.replace(/>/g, '>\n') 
			xdbc.recentError +='\n-------';
		}
		if (xdbc.debug) return alert(xdbc.recentError);
		if (typeof(xhr.callback) == 'function') xhr.callback();
	},
	exec : function() {
		if (!xdbc.que.childNodes.length) return (typeof(arguments[0]) == 'function')? arguments[0]() : xdbc.doError('Nothing qued!');
		xdbc.prepQue();
		var xhr = {
			src		 : xdbc.path,
			callback : (typeof(arguments[0]) == 'function')? arguments[0] : null,
			async	 : (typeof(arguments[0]) == 'function' || typeof(arguments[0]) == 'boolean'),
			http	 : (env.ax? new ActiveXObject(xdbc.otype['XmlHttp']) : new XMLHttpRequest())
		};
		xhr.http.open('POST', xdbc.path, xhr.async);
		xhr.http.send(xdbc.que.parentNode);
		xdbc.flushQue();
		if (xhr.async) {
			xhr.http.onreadystatechange = function() {
				if (xhr.http.readyState != 4) return;
				xhr.dom = xdbc.ctrlXml(xhr.http.responseXML.documentElement, xhr.src);
				if (!xhr.dom) return xdbc.doError(xhr.http.responseText);
				else if (xhr.dom.hasChildNodes() && xhr.dom.firstChild.nodeName == 'error') return xdbc.doError(xhr);
				xdbc.unescape(xhr.dom);
				if (xhr.callback) xhr.callback(xhr.dom);
			}
			return xhr;
		}
		xhr.dom = xdbc.ctrlXml(xhr.http.responseXML.documentElement, xhr.src);
		
		if (!xhr.dom) return xdbc.doError(xhr.http.responseText);
		else if (xhr.dom.hasChildNodes && xhr.dom.firstChild.nodeName == 'error') return xdbc.doError(xhr.dom);
		else {
			xdbc.unescape(xhr.dom);
			return xhr.dom;
		}
	}
}
xdbc.init();
