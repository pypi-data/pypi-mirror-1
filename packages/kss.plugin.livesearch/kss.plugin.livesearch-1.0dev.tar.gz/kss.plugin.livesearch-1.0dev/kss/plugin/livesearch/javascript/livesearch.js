/*

// 
// Copyright (c) 2006 Plone Foundation
// Copyright (c) 2006 Balazs Ree <ree@greenfinity.hu>
//
// Original license conditions apply.
//


// +----------------------------------------------------------------------+
// | Copyright (c) 2004 Bitflux GmbH                                      |
// +----------------------------------------------------------------------+
// | Licensed under the Apache License, Version 2.0 (the "License");      |
// | you may not use this file except in compliance with the License.     |
// | You may obtain a copy of the License at                              |
// | http://www.apache.org/licenses/LICENSE-2.0                           |
// | Unless required by applicable law or agreed to in writing, software  |
// | distributed under the License is distributed on an "AS IS" BASIS,    |
// | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or      |
// | implied. See the License for the specific language governing         |
// | permissions and limitations under the License.                       |
// +----------------------------------------------------------------------+
// | Author: Bitflux GmbH <devel@bitflux.ch>                              |
// +----------------------------------------------------------------------+

*/
kukit.LiveSearch = function() {};

kukit.LiveSearch.prototype.liveSearchReq = false;
kukit.LiveSearch.prototype.t = null;
kukit.LiveSearch.prototype.liveSearchLast = "";

kukit.LiveSearch.prototype.searchInput = null; 
kukit.LiveSearch.prototype.resultNode = null; 

kukit.LiveSearch.prototype.isIE = false;

kukit.LiveSearch.prototype.widthOffset=1;

//kukit.LiveSearch.prototype.calculateWidth = function(){
//}

kukit.LiveSearch.prototype.getElementDimensions = function(base) {
    var offsetTrail = base;
    var offsetLeft = 0;
    var offsetTop = 0;
    var width = 0;
    
    while (offsetTrail) {
        offsetLeft += offsetTrail.offsetLeft;
        offsetTop += offsetTrail.offsetTop;
        offsetTrail = offsetTrail.offsetParent;
    }
    if (navigator.userAgent.indexOf("Mac") != -1 &&
        typeof document.body.leftMargin != "undefined") {
        offsetLeft += document.body.leftMargin;
        offsetTop += document.body.topMargin;
    }

    if(!this.isIE){
    width =  base.offsetWidth-this.widthOffset*2;
    }
    else {
    width = base.offsetWidth;
    }

    return { left:offsetLeft, 
         top:offsetTop, 
         width: width, 
             height: base.offsetHeight,
         bottom: offsetTop + base.offsetHeight, 
         right : offsetLeft + width};
};

kukit.LiveSearch.prototype.bind_searchbox = function(name, func_to_bind, oper) {
    oper.evaluateParameters(['submit'], {
            'highlightId': 'LSHighlight', 
            'rowClass': 'LSRow',
            'complete': 'false',
            'separator': ',',
            'useSeparator': 'false',
            'numCharsToIgnore': '2'}, 'livesearch-searchbox event binding');
    oper.evalBool('submit', 'livesearch-searchbox event binding');
    oper.evalBool('complete', 'livesearch-searchbox event binding');
    oper.evalInt('numCharsToIgnore', 'livesearch-searchbox event binding');
    var searchInput = oper.node;
    if (this.searchInput != null) {
        throw 'livesearch-searchbox event binder can only be bound to a single node; ';
    }
    if (searchInput == null) {
        throw 'livesearch-input event must be bound to a node.';
    }
    this._cache = new Object();
    this.searchInput = searchInput;
    this.parms = oper.parms;
    // Make additional event funcs for binding
    var self = this;
    var func_keyPress = function(evt) {
        self.keyPress(evt);
    }
    var func_hide = function(evt) {
        self.hide();
    }
    var func_hideDelayed = function(evt) {
        self.hideDelayed();
    }
    var func_submit = function(evt) {
        return self.submit();
    }

//  Only keypress catches repeats in moz/FF but keydown is needed for
//  khtml based browsers.
    if (navigator.userAgent.indexOf("KHTML") > 0) {
        searchInput.addEventListener("keydown",func_keyPress,false);
        searchInput.addEventListener("focus",func_to_bind,false);
        searchInput.addEventListener("blur",func_hideDelayed, false);
    } else if (searchInput.addEventListener) {
        searchInput.addEventListener("keypress",func_keyPress,false);
        searchInput.addEventListener("blur",func_hideDelayed,false);
    } else {
        searchInput.attachEvent("onkeydown",func_keyPress);
        searchInput.attachEvent("onblur",func_hideDelayed);
        this.isIE = true;
    }

    // Also do the onSubmit
    if (oper.parms.submit) {
        var form = new kukit.fo.CurrentFormLocator(searchInput).getForm();
        if (!form) {
            throw 'No form found in livesearch-searchinput event binder';
        }
        form.onsubmit = func_submit;
    }

//  Why doesn't this work in konq, setting it inline does.
    searchInput.setAttribute("autocomplete","off");

    this.liveSearchRoot = '';
    this.liveSearchRootSubDir = '';

    //this.finish_binding();
};

/*
kukit.LiveSearch.prototype.finish_binding = function() {
    // This is called when all nodes are bound.
    if (this.searchInput && this.resultNode) {
        var pos = this.getElementDimensions(this.searchInput); 
        pos.left = pos.left - this.resultNode.offsetParent.offsetLeft + pos.width;
        this.resultNode.style.display='none';
    }
};
*/

kukit.LiveSearch.prototype.hideDelayed = function() {
    var self = this;
    var func = function() {
        self.hide();
    }
    var timer = new kukit.ut.TimerCounter(400, func)
    timer.start();
};

kukit.LiveSearch.prototype.getFirstHighlight = function() {
    var set = this.getHits();
    if (set.length == 0) {
        return null;
    } else {
        return set[0];
    }
};

kukit.LiveSearch.prototype.getLastHighlight = function() {
    var set = this.getHits();
    if (set.length == 0) {
        return null;
    } else {
        return set[set.length-1];
    }
};

kukit.LiveSearch.prototype.getHits = function() {
    var set;
    if (this.resultNode != null) {
        set = this.resultNode.getElementsByTagName('li');
    } else {
        set = [];
    }
    return set
};

/*
kukit.LiveSearch.prototype.findChild = function(obj, specifier) {
    var cur = obj.firstChild;
    try {
        while (cur != undefined) {
            cur = cur.nextSibling;
            if (specifier(cur) == true) return cur;
        }
    } catch(e) {};
    return null;
    
};
*/

kukit.LiveSearch.prototype.findNext = function(obj, specifier) {
    var cur = obj;
    try {
        while (cur != undefined) {
            cur = cur.nextSibling;
            if (cur.nodeType==3) cur=cur.nextSibling;
        
            if (cur != undefined) {
                if (specifier(cur) == true) return cur;
            } else { break }
        }
    } catch(e) {};
    return null;
};

kukit.LiveSearch.prototype.findPrev = function(obj, specifier) {
    var cur = obj;
    try {
        cur = cur.previousSibling;
        if (cur.nodeType==3) cur=cur.previousSibling;
        if (cur!=undefined) {
            if (specifier(cur) == true) 
                return cur;
        } 
    } catch(e) {};
    return null;
};

kukit.LiveSearch.prototype.preventDefault = function(e) {
    // W3C style
    if (e.preventDefault)
        e.preventDefault();
    // MS style
    try { e.returnValue = false; } catch (exc2) {}
};


/*
kukit.LiveSearch.prototype.preventBubbling = function(e) {
    if (!e) var e = window.event;
    e.cancelBubble = true;
    if (e.stopPropagation) e.stopPropagation();
};
*/

kukit.LiveSearch.prototype.moveInMenu = function(highlight, find1, findmore) {
    if (!highlight) {
        highlight = find1.call(this);
    } else {
        highlight.removeAttribute("id");
        var self = this;
        highlight = findmore.call(this, highlight, function (o) {return o.className == self.parms.rowClass;});
    }
    if (highlight) {
        highlight.setAttribute("id", this.parms.highlightId);
        this.doCompletion()
    }
};

kukit.LiveSearch.prototype.keyPress = function(event) {
    var highlight = document.getElementById(this.parms.highlightId);
    var kc = event.keyCode;
    // If we allowed completion, and a row is highlighted
    // we want to prevent tab and enter from happening.
    if (this.parms.complete && highlight) {
        // tab OR enter
        if ( kc == 9 || kc == 13) {
            this.preventDefault(event);
            this.hide();
            // We return and permit neither the navigation nor
            // the search start from happening.
            return;
        }
    }
    if (kc == 39 && this.parms.complete)
    //KEY RIGHT: enters the menu, if there is a menu and we are not in yet.
    {
        // also if there are no actual results, don't catch the key
        if (! highlight && this.getHits().length > 0) {
            this.moveInMenu(highlight, this.getFirstHighlight, this.findNext);
            this.preventDefault(event);
        }
    } 
    else if (kc == 40)
    //KEY DOWN
    {
        this.moveInMenu(highlight, this.getFirstHighlight, this.findNext);
        this.preventDefault(event);
    } 
    //KEY UP
    else if (kc == 38) {
        this.moveInMenu(highlight, this.getLastHighlight, this.findPrev);
        this.preventDefault(event);
    } 
    //ESC
    else if (kc == 27) {
        if (highlight) {
            highlight.removeAttribute("id");
        }
        this.hide();
    } 
    //
    // Now we call start!
    this.start(event)
};

kukit.LiveSearch.prototype.doCompletion = function(highlight) {
    if (! this.parms.complete) return;
    // do completion based on result
    //
    if (typeof(highlight) == 'undefined') {
        var highlight = document.getElementById(this.parms.highlightId);
    }
    // Use textual content of highliglted item
    var value =  kukit.dom.textContent(highlight, true);
    // remove whitespaces
    value = kukit.tk._ParserBase.prototype.dewhitespaceAndTrim(value);
    //
    // This is supposed to be more generic. But for now: we keep everything
    // before the last comma, and replace things after.
    // (this can be controlled by the separator and useSeparator evt parms.)
    var orig = this.searchInput.value;
    var commapos = -1;
    if (this.parms.separator != null) {
        commapos = orig.lastIndexOf(this.parms.separator);
    }
    orig = (commapos != -1) ? (orig.substring(0, commapos + 1) + ' ') : '';
    // set the value
    this.searchInput.value = orig + value;
};

kukit.LiveSearch.prototype.start = function(event) {
    if (this.t) {
        this.t.clear();
    }
    var code = event.keyCode;
    if (code!=40 && code!=38 && code!=27 && code!=37 && code!=39) {
        var self = this;
        var func = function() {
            self.doSearch();
        }
        this.t = new kukit.ut.TimerCounter(200, func)
        this.t.start();
    } 
};

kukit.LiveSearch.prototype.doSearch = function() {
    var searchInput = this.searchInput.value;
    // only send part after the separator if that is active
    if (this.parms.separator != null) {
        var commapos = searchInput.lastIndexOf(this.parms.separator);
        searchInput = searchInput.substr(commapos + 1).replace(/^[ ]+/, '')
    }

    // Do nothing as long as we have less then two characters - 
    // the search results makes no sense, and it's harder on the server.
    if (! searchInput || searchInput.length < this.parms.numCharsToIgnore) {
        this.hide();
        return false;
    }

    // Do we have cached results
    var result = this._cache[searchInput];
    if (result) {
        this.showResult(result); 
        return;
    }
    // Send the request to the server, by triggering the event.
    this.__continueEvent_allNodes__('searchbox', {'q': searchInput});

};

kukit.LiveSearch.prototype.hide = function() { 
    if (this.resultNode) {
        var parentNode = this.resultNode.parentNode;
        parentNode.removeChild(this.resultNode);
        this.resultNode = null;
    }
};

kukit.LiveSearch.prototype.showResult = function(result) {
    this.hide();
    // always append after the search input
    var parentNode = this.searchInput.parentNode;
    result = kukit.dom.forceToDom(result);
    var element = result.firstChild;
    parentNode.appendChild(element);
    this.resultNode = parentNode.lastChild;

    if (this.parms.complete) {
        // Bind the resuls
        // we could do this from kss, but for now it is just javascript.
        // We use cssQuery and limit ourselves to the result node.
        //
        var nodes = cssQuery('.' + this.parms.rowClass, this.resultNode);
        var self = this;
        var func_clickResult = function(evt) {
            self.doClickResult(evt);
        };
        for (var i=0; i<nodes.length; i++) {
            var node = nodes[i];
            if (! this.isIE) {
                node.addEventListener("click", func_clickResult, false);
            } else {
                node.attachEvent("onclick", func_clickResult);
            }
        }
    }
};

kukit.LiveSearch.prototype.doClickResult = function(evt) {
    var node = kukit.pl.getTargetForBrowserEvent(evt);
    this.doCompletion(node);
    this.preventDefault(evt);
    //kukit.dom.focus(this.searchInput);
    this.focusAndPosToEnd(this.searchInput);
};

kukit.LiveSearch.prototype.focusAndPosToEnd = function(obj) {
    // Focus, and position the object to the end.
    // This is needed on IE, where focus jumps to the beginning.
    //kukit.dom.focus(obj);
    var len = obj.value.length;
    this.setCaretTo(obj, len);
};

/* Taken from:
 *      http://parentnode.org/javascript/working-with-the-cursor-position/
 */
kukit.LiveSearch.prototype.setCaretTo = function(obj, pos) { 
    if(obj.createTextRange) { 
        /* Create a TextRange, set the internal pointer to
           a specified position and show the cursor at this
           position
        */ 
        var range = obj.createTextRange(); 
        range.move("character", pos); 
        range.select(); 
    } else if(obj.selectionStart) { 
        /* Gecko is a little bit shorter on that. Simply
           focus the element and set the selection to a
           specified position
        */ 
        obj.focus(); 
        obj.setSelectionRange(pos, pos); 
    } 
};

kukit.LiveSearch.prototype.exec_insert = function(name, oper) {
    oper.evaluateParameters(['html'], {}, 'livesearch-insert event execution');
    var parms = oper.parms;
    parms.html = kukit.dom.forceToDom(parms.html);
    this.showResult(parms.html);
    this._cache[this.liveSearchLast] = parms.html;
};

kukit.LiveSearch.prototype.submit = function() {
    var highlight = document.getElementById(this.parms.highlightId);
    
    if (highlight){
        var targets = highlight.getElementsByTagName('a');
        if (targets.length == 0)
            return true;
        var target = targets[0].href;
        if (!target)
            return true;
        if ((this.liveSearchRoot.length > 0) && (target.substring(0, this.liveSearchRoot.length) != this.liveSearchRoot)) {
            window.location = this.liveSearchRoot + this.liveSearchRootSubDir + target;
        } else {
            window.location = target;
        }
        return false;
    } else {
        return true;
    }
};

kukit.eventsGlobalRegistry.register('livesearch', 'searchbox', kukit.LiveSearch, 'bind_searchbox', null);
kukit.eventsGlobalRegistry.register('livesearch', 'insert', kukit.LiveSearch, null, 'exec_insert');

