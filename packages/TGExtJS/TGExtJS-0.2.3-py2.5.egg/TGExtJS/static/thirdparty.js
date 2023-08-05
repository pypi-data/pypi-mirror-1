/**
 * This is to store all the generated components in order to make them
 * accessible from within custom scripts.
 */
var ExtJSInst = {
	Tab: {},
	Grid: {},
	DataStore: {}
}

function convert_to_ExtJS_tab(id) {
	Ext.onReady(function() {
		ExtJSInst.Tab[id] = new Ext.TabPanel(id);
		var i = 0;
		$$('#'+id+' div.tabbertab').each(function(tc) {
			var title = tc.firstChild.innerHTML;
			tc.removeChild(tc.firstChild);
			if(tc.id == "") {
				tc.id = id + '_' + i++;
			}
			ExtJSInst.Tab[id].addTab(tc.id, title);
		});
		ExtJSInst.Tab[id].activate(0);
	} );
}

/**
 * @class Ext.grid.TableGrid
 * @extends Ext.grid.Grid
 * A Grid which creates itself from an existing HTML table element.
 * @constructor
 * @param {String/HTMLElement/Ext.Element} table The table element from which this grid will be created -
 * The table MUST have some type of size defined for the grid to fill. The container will be
 * automatically set to position relative if it isn't already.
 * @param {Object} config A config object that sets properties on this grid and has two additional (optional)
 * properties: fields and columns which allow for customizing data fields and columns for this grid.
 * @history
 * 2007-03-01 Original version by Nige "Animal" White
 * 2007-03-10 jvs Slightly refactored to reuse existing classes
 */
Ext.grid.TableGrid = function(table, config) {
	config = config || {};
	var cf = config.fields || [], ch = config.columns || [];
	table = Ext.get(table);

	var ct = table.insertSibling();

	var fields = [], cols = [];
	var headers = table.query("thead th");
	for (var i = 0, h; h = headers[i]; i++) {
		var text = h.innerHTML;
		var name = 'tcol-'+i;

		fields.push(Ext.applyIf(cf[i] || {}, {
			name: name,
			mapping: 'td:nth('+(i+1)+')/@innerHTML'
		}));

		cols.push(Ext.applyIf(ch[i] || {}, {
			'header': text,
			'dataIndex': name,
			'width': h.offsetWidth,
			'tooltip': h.title,
			'sortable': true
		}));
	}

	var ds = new Ext.data.Store({
		reader: new Ext.data.XmlReader({
			record:'tbody tr'
		}, fields)
	});

	ds.loadData(table.dom);
	ExtJSInst.DataStore[table] = ds;

	var cm = new Ext.grid.ColumnModel(cols);

	if(config.width || config.height){
		ct.setSize(config.width || 'auto', config.height || 'auto');
	}
	if(config.remove !== false){
		table.remove();
	}

	Ext.grid.TableGrid.superclass.constructor.call(this, ct,
		Ext.applyIf(config, {
			'ds': ds,
			'cm': cm,
			'sm': new Ext.grid.RowSelectionModel(),
			autoHeight:true,
			autoWidth:true
		}
	));
};

Ext.extend(Ext.grid.TableGrid, Ext.grid.Grid);

function convert_to_ExtJS_Grid(id) {
	Ext.onReady(function() {
		ExtJSInst.Grid[id] = new Ext.grid.TableGrid(id);
		ExtJSInst.Grid[id].render();
	} );
}

function construct_json_grid(container_id, data_url, per_page_limit,
			     metadata, recordType, columnModel,
			     display_message, no_items_message) {

	var ds = new Ext.data.Store({
		proxy: new Ext.data.HttpProxy({
			url: data_url
			}),
		reader: new Ext.data.JsonReader(metadata, recordType),
		remoteSort: true
		});

	var cm = new Ext.grid.ColumnModel(columnModel);
	cm.defaultSortable = true;

	var grid = new Ext.grid.Grid(container_id, {
		ds: ds,
		cm: cm,
		enableColLock:false,
		loadMask: true
		});

	var bl = Ext.BorderLayout.create({
		center: {
			margins:{left:3,top:3,right:3,bottom:3},
			panels: [new Ext.GridPanel(grid)]
		}
	}, container_id+'_panel');

	grid.render();

	var gridFoot = grid.getView().getFooterPanel(true);
		var paging = new Ext.PagingToolbar(gridFoot, ds, {
		pageSize: per_page_limit,
		displayInfo: true,
		displayMsg: display_message,
		emptyMsg: no_items_message
		});

	ds.load({params:{start:0, limit:per_page_limit}});
	ExtJSInst.DataStore[container_id] = ds;
	ExtJSInst.Grid[container_id] = grid;
}

function json_grid_from_url_values(container_id, data_url, per_page_limit, property_url) {
	new Ajax.Request(property_url, {
		requestHeaders: ['Content-Type', 'application/x-www-form-urlencoded'],
		onComplete: function(r) {
			var result = r.responseText.evalJSON();
			construct_json_grid(container_id, data_url, per_page_limit,
				result['metadata'], result['recordType'], result['columnModel'],
				result['display_message'], result['no_items_message']);
		}
	})
}
