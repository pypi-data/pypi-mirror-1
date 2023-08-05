           /*3OGGO3(^
       ~Q@@@BBBBB@#(B@@S/
     O@@BBBBBBBBBB@O R@B@@O
    O@BBB@@@@@@BBB@G S@@@@@O		WOCO - Word Complete 1.01
  /B@BBB@t    /#@B@( //     /		Controlled by Hakan Bilgin © 2005
 ~@BBB@R(       BB~   /tC/  %@/		http://www.challenger.se
 O@BB@#CCQ##s  /R(  e#@@O  C@@s
/@BBBBBBBBB@O (@( /@#7 /6R@@BB@/
%@BBBBBBB@B~ KR    ^(CG3   t@B@%
3@BBBBBB@O (@R   Q@@@@Q^ /#@BB@%
%@BBBBB@#  K@e   K@@BC  tR@BBB@t
^B@B@SC3  %BB%   ^^ /sB@BBBBB@R^
 %KC/      //(     C@@BBBBBBB@t
  QQQ#G    e@@/     C@BBBBBB@R
   K@@#   sRRB@%S@@@(C@BBBB@Q
    (B@K 7@BBBBBBBB@S6@BB@R/
     ~R@G e@BBBBBBB@GS@B@#/			The sourcecode is licensed under a Creative Commons License.
        (#@S#@BBBB@#Q@Q(			http://creativecommons.org/licenses/LGPL/2.1/
             ^/~~/*/

woco = {
	init : function(dbSrc, oEl) {
		if (!document.all) return woco_moz.init(dbSrc, oEl);
		var oEl = (typeof(oEl) == 'string')? document.getElementById(oEl) : oEl;
		if (!oEl) return;
		oEl.onkeypress = woco.doKey;
		oEl.onkeydown = woco.doSysKey;
		xdbc.load(dbSrc, woco.xHandler, true);
	},
	xHandler : function(xWocoObj) {
    	woco.active = true;
        woco.charCase = false;
        woco.speChars = "";
        woco.rgx = new RegExp('[\\w'+ woco.speChars +']', 'ig');
        woco.db = ' ' + xWocoObj["data"].join(" ") + ' ';
	},
	doKey : function() {
		if (event.ctrlKey || !woco.active) return;
		var tKey = String.fromCharCode(event.keyCode);
		if (!event.shiftKey) tKey = tKey.toLowerCase();
		if (!tKey.match(woco.rgx)) return;
		rng = document.selection.createRange();
		crng = rng.duplicate();
		crng.moveEnd('character');
		if (document.selection.type == 'Text') document.selection.clear();
		if (crng.text.match(woco.rgx)) return;
		rng.text = tKey;
		rng.moveStart('word', -1);
		rgx = new RegExp(' '+ rng.text.trim() +'[\\w'+ woco.speChars +']+', 'ig');
		woco.match = woco.db.match(rgx);
		if (woco.match && woco.match != 'null') {
			woco.mInt = 0;
			woco.complete();
		}
		woco.cancelEvent();
	},
	complete : function() {
		var suggestedWord = woco.match[woco.mInt].trim().substr(rng.text.length);
		woco.rng = document.selection.createRange();
		woco.rng.text = suggestedWord;
		woco.rng.moveStart('character', -suggestedWord.length);
		woco.rng.select();
		woco.cancelEvent();
	},
	cancelEvent	: function() {
		event.returnValue = null;
		event.cancelBubble = true;
	},
	doSysKey : function() {
		switch (event.keyCode) {
			case 9:
				if (woco.rng && woco.match) {
					woco.cancelEvent();
					if (woco.charCase) {
						woco.rng.moveStart('word', -1);
						woco.rng.expand('word');
						woco.rng.text = woco.match[woco.mInt].trim();
					} else woco.rng.text = woco.rng.text +' ';
					woco.rng.select();
				}
				break;
			case 27:
				woco.active = !woco.active;
				break;
			case 38:
				if (!woco.match) return;
				woco.mInt--;
				if (woco.mInt < 0) woco.mInt = woco.match.length-1;
				woco.complete();
				return;
			case 40:
				if (!woco.match) return;
				woco.mInt++;
				if (woco.mInt >= woco.match.length) woco.mInt = 0;
				woco.complete();
				return;
		}
		woco.match = null;
	}
}

woco_moz = {
	init : function(dbSrc, oEl) {
		var oEl = (typeof(oEl) == 'string')? document.getElementById(oEl) : oEl;
		oEl.addEventListener('keypress', woco_moz.doKey, false);
		xdbc.load(dbSrc, woco_moz.xHandler, true);
	},
	xHandler : function(xWocoObj) {
	    if (xWocoObj) {
        	woco_moz.active = true;
            woco_moz.charCase = false;
            woco_moz.speChars = "";
            woco_moz.rgx = new RegExp('[\\w'+ woco_moz.speChars +']', 'ig');
            woco_moz.db = ' ' + xWocoObj["data"].join(" ") + ' ';
        }
	},
	doKey : function(e) {
		if (!woco_moz.active) return;
		oEl = e.target;
		tKey = String.fromCharCode(e.charCode);
		if (!tKey.match(woco_moz.rgx)) return woco_moz.doSysKey(e);
		
		rngStart = oEl.selectionStart;
		rngEnd = oEl.selectionEnd;
		selEnd = (rngStart != rngEnd)? rngEnd : null ;
		if (!selEnd && oEl.value.substring(rngStart, rngStart+1).match(woco_moz.rgx)) return;
		
		frgStart = rngStart;
		while (frgStart > 0 && oEl.value.substring(frgStart-1, frgStart).match(woco_moz.rgx)) frgStart--;
		wordFragment = oEl.value.substring(frgStart, rngStart) + tKey;
		rgx = new RegExp(' '+ wordFragment +'[\\w]+', 'ig');
		woco_moz.match = woco_moz.db.match(rgx);
		
		if (woco_moz.match && woco_moz.match != 'null') {
			woco_moz.mInt = 0;
			woco_moz.complete(e);
		}
	},
	doSysKey : function(e) {
		oEl = e.target;
		switch (e.keyCode) {
			case 9:
				if (!woco_moz.match) return;
				if (woco_moz.charCase) {
					frgStart = oEl.selectionStart;
					while (frgStart > 0 && oEl.value.substring(frgStart-1, frgStart).match(woco_moz.rgx)) frgStart--;
					nValue = oEl.value.substring(0, frgStart);
					nValue += woco_moz.match[woco_moz.mInt].trim();
					nValue += oEl.value.substring(oEl.selectionEnd, oEl.value.length);
					oEl.value = nValue;
					cPos = frgStart + woco_moz.match[woco_moz.mInt].trim().length;
					oEl.setSelectionRange(cPos, cPos);
				} else oEl.setSelectionRange(oEl.selectionEnd, oEl.selectionEnd);
				woco_moz.cancelEvent(e);
				break;
			case 27:
				woco_moz.active = !woco_moz.active;
				break;
			case 38:
				if (!woco_moz.match) return;
				woco_moz.mInt--;
				if (woco_moz.mInt < 0) woco_moz.mInt = woco_moz.match.length-1;
				tKey = '';
				rngStart = oEl.selectionStart;
				selEnd = oEl.selectionEnd;
				woco_moz.complete(e);
				return;
			case 40:
				if (!woco_moz.match) return;
				woco_moz.mInt++;
				if (woco_moz.mInt >= woco_moz.match.length) woco_moz.mInt = 0;
				tKey = '';
				rngStart = oEl.selectionStart;
				selEnd = oEl.selectionEnd;
				woco_moz.complete(e);
				return;
		}
		woco_moz.match = null;
	},
	complete : function(e) {
		if (!woco_moz.match) return;
		var oEl = e.target;
		var swFrag = woco_moz.match[woco_moz.mInt].trim().substr(rngStart-frgStart+tKey.length);
		selEnd = selEnd || rngStart;
		nValue = oEl.value.substring(0, rngStart);
		nValue += tKey + swFrag;
		nValue += oEl.value.substring(selEnd, oEl.value.length);
		oEl.value = nValue;
		var cPos = rngStart + tKey.length;
		oEl.setSelectionRange(cPos, cPos + swFrag.length);
		woco_moz.cancelEvent(e);
	},
	cancelEvent	: function(e) {
		e.stopPropagation();
		e.preventDefault();
	}
}