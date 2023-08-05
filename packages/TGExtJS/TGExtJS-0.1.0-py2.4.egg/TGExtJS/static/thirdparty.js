var ExtJSTabs = new Object();

function convert_to_ExtJS_tab(id) {
	YAHOO.util.Event.onContentReady(id, function(p_oEvent) {
		var tc = YAHOO.util.Dom.getElementsByClassName("tabbertab", "div", id);
		ExtJSTabs[id] = new Ext.TabPanel(id);
		for(var i = 0; i < tc.length; i++) {
			var title = tc[i].firstChild.innerHTML;
			tc[i].removeChild(tc[i].firstChild);
			if(tc[i].id == "") {
				tc[i].id = id + '_' + i;
			}
			ExtJSTabs[id].addTab(tc[i].id, title);
		}
		ExtJSTabs[id].activate(0);
	} );
}
