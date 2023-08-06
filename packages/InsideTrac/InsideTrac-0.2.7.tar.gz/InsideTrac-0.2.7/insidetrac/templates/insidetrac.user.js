// ==UserScript==
// @name           InsideTrac - ${addname}
// @namespace      http://www.insidetrac.org/
// @description    InsideTrac - Issue Tracking Notification Script
// @include        *
// ==/UserScript==

(function () {
    var trachost = '${abs_href.base}';
	
    String.prototype.trim = function() {
	return this.replace(/^\s+|\s+$/g,"");
    }

    function createLink(linktext, href) {
	var textNode = document.createTextNode(linktext);
	var a = document.createElement('a');
	a.setAttribute('href', href);
	a.appendChild(textNode);
	return a;
    }
	
    function createTableCellLink(elname, linktext, href, className) {
	className = className ? className : "";

	var a = createLink(linktext, href);
	td = document.createElement(elname);
	td.appendChild(a);
	if (className) {
	    td.setAttribute('class', className);
	}
	return td;
    }
	
    function getTextNodes(root) {
	ret = "";
	for (var i=0; i<root.childNodes.length; i++) {
	    el = root.childNodes[i];
	    if (el.nodeType == 3) { ret = ret + " " + el.nodeValue; }
	    if (el.childNodes.length > 0) { ret = ret + " " + getTextNodes(el); }
	}
	return ret.trim();
    }
	
    function getLinkRef(root) {
	ret = "";
	for (var i=0; i<root.childNodes.length; i++) {
	    el = root.childNodes[i];
	    if (el.nodeName == "A") { return el.href; }
	    if (el.childNodes.length > 0) {
		ret = getLinkRef(el);
		if (ret) { return ret; };
	    }
	}
	return ret.trim();
    }
	
    // sourceforge
    var sfnet = new RegExp("sf.net$|sourceforge.net$");
    var m = sfnet.exec(location.host);
    if (m != null) {
	els = document.getElementsByClassName('tracker');
	for (var i=0; i<els.length; i++) {
	    tbl = els[i];
	    theads = tbl.getElementsByTagName('thead');
	    if (theads.length >= 1) {
		thead = theads[0];
		trs = thead.getElementsByTagName('tr');
		if (trs.length >= 2) {
		    th1 = createTableCellLink(
					      'th',
					      'IT:${addname}',
					      trachost,
					      ''
					      );
		    th2 = createTableCellLink(
					      'th',
					      'IT:${addname}',
					      trachost,
					      ''
					      );
		    trs[0].appendChild(th1);
		    trs[1].appendChild(th2);
		}
	    }
	    tbodies = tbl.getElementsByTagName('tbody');
	    if (tbodies.length >= 1) {
		tbody = tbodies[0];
		trs = tbody.getElementsByTagName('tr');
		for (var j=0; j<trs.length; j++) {
		    tr = trs[j]
			tds = tr.getElementsByTagName('td');
		    aid = getTextNodes(tds[0]);
		    title = getTextNodes(tds[1]);
		    href = escape(getLinkRef(tds[1]));
		    summary = escape("SF: " + aid + ", " + title);
		    td = createTableCellLink(
					     'td',
					     'IT:${addname}',
					     trachost + "/newticket?preview=Preview&summary=" + summary + "&description=" + href,
					     'p5'
					     );
		    trs[j].appendChild(td);
		}
	    }
	}
    }

    // bitbucket.org support
    var sfnet = new RegExp("bitbucket.org$");
    var m = sfnet.exec(location.host);
    if (m != null) {
	el = document.getElementById('issues-list');
	tables = el.getElementsByTagName('table');
	if (tables.length > 0) {
	    tbodies = tables[0].getElementsByTagName('tbody');
	    if (tbodies.length > 0) {
		trs = tbodies[0].getElementsByTagName('tr');
		if (trs.length > 0) {
		    tr = trs[0];
		    tr.appendChild(createTableCellLink(
						       'th',
						       'IT:${addname}',
						       trachost,
						       'issues-list-milestone'
						       ));
		    for (var i=1; i<trs.length; i++) {
			tds = trs[i].getElementsByTagName('td');
			aid = getTextNodes(tds[0]);
			title = getTextNodes(tds[1]);
			href = escape(getLinkRef(tds[0]));
			summary = escape("BB: " + aid + ", " + title);
			td = createTableCellLink(
						 'td',
						 'IT:${addname}',
						 trachost + "/newticket?preview=Preview&summary=" + summary + "&description=" + href,
						 ''
						 );
			trs[i].appendChild(td);
		    }
		}
	    }
	}
    }

    // trac instance support
    metanav = document.getElementById('metanav');
    mainnav = document.getElementById('mainnav');
    if ((metanav != null) && (mainnav != null)) {
	els = document.getElementsByClassName('tickets');
	if (els.length > 0) {
	    theads = els[0].getElementsByTagName('thead');
	    if (theads.length > 0) {
		trs = theads[0].getElementsByTagName('tr');
		for (var i=0; i<trs.length; i++) {
		    trs[i].appendChild(createTableCellLink(
							   'th',
							   'IT:${addname}',
							   trachost,
							   ''
							   ));
		}
	    }
	    tbodies = els[0].getElementsByTagName('tbody');
	    if (tbodies.length > 0) {
		trs = tbodies[0].getElementsByTagName('tr');
		for (var i=0; i<trs.length; i++) {
		    tds = trs[i].getElementsByTagName('td');
		    aid = getTextNodes(tds[0]);
		    title = getTextNodes(tds[1]);
		    href = escape(getLinkRef(tds[0]));
		    summary = escape("Trac: " + aid + ", " + title);
		    trs[i].appendChild(createTableCellLink(
							   'td',
							   'IT:${addname}',
							   trachost + "/newticket?preview=Preview&summary=" + summary + "&description=" + href,
							   'date'
							   ));
						   
		}
	    }
	}
    }
})();
