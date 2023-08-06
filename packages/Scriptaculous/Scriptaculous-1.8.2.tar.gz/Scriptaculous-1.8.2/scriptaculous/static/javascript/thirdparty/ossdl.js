/*
 * @author	W-Mark Kubacki; kubacki@hurrikane.de
 */

function display_error(text) {
	if(typeof(window['Modalbox']) != "undefined") {
		Modalbox.MessageBox.alert(catgets(0), text);
	} else {
		alert(text);
	}
}

var AJAJForms = {
	/* storage for forms' data with form's id as key */
	_decoratedForms: {},

	unlistNonexistendForms: function() {
		/* remove non-existend forms */
		var new_deco_forms = {};
		for(var fid in AJAJForms._decoratedForms) {
			if(!!$(fid)) {
				new_deco_forms[fid] = AJAJForms._decoratedForms[fid];
			}
		}
		AJAJForms._decoratedForms = new_deco_forms;
	},

	updateMemorizedFields: function(form_id) {
		AJAJForms._decoratedForms[form_id] = $(form_id).serialize(true);
	},

	_inputObserver: function() {
		var form_id = $(this).form.identify();
		if($(this).getValue() == AJAJForms._decoratedForms[form_id][$(this).name]) {
			$(this).removeClassName('changed');
			$(this).removeClassName('errorous');
		} else {
			$(this).addClassName('changed');
		}
		/* remove adjacent fielderror */
		fe = $(this).siblings().reverse().detect(function(el) {
			return el.tagName == 'SPAN' && el.hasClassName('fielderror');
		});
		if(fe) {
			fe.remove();
		}
	},

	decorateForm: function(form) {
		var form_id = form.identify();
		if(!AJAJForms._decoratedForms[form_id]) {
//				Event.observe(form, 'submit', function() {return false;});
			AJAJForms.updateMemorizedFields(form_id);
			form.getElements().each(function(input) { // getInputs doesn't give SELECT and TEXTAREA
				if(input.type != 'submit' && input.type != 'reset') {
					Event.observe(input, 'change', AJAJForms._inputObserver);
				} else if(input.type == 'submit') {
					if(!input.onclick) {
						Event.observe(input, 'click', AJAJForms.submit);
					}
				}
			});
		}
		return form_id;
	},

	decorateForms: function() {
		AJAJForms.unlistNonexistendForms();
		/* decorate present forms, if needed */
		$$('form.AJAJForm').each(AJAJForms.decorateForm);
	},

	/* helper function for TG for displaying errors and their inputs in one style */
	decorateErrors: function() {
		$$('span.fielderror').each(function(item) {
			p = item.parentNode.parentNode;
			p.descendants().each(function(item) {
				if(item.tagName == 'INPUT') {
					item.addClassName('errorous');
				}
			});
		});
	},

	/* mark inputs with errors and display error message next to them */
	displayErrorsFor: function(form_id, fielderrors) {
		$$('#'+form_id+' span.fielderror').invoke('remove');
		$(form_id).getElements().each(function(item) {
			if(fielderrors[item.name]) {
				item.removeClassName('changed');
				item.addClassName('errorous');
				item.parentNode.insert('<span class="fielderror">'+fielderrors[item.name]+'</span>');
			} else {
				item.removeClassName('errorous');
			}
		});
	},

	/*
	 * @param	options		"me" set to "this" if you happen to set the submit() handler yourself
	 * 				"onValidInput" callback, called if no validation errors occured; first parameter is the entire JSON response,
	 * 				"onInvalidInput" -''-
	 * @returns	always false
	 */
	submit: function(options) {
		options = options || {};
		var refer_to = options['me'] || $(this);
		var form_id = refer_to.form.identify();
		function processSubmitAnswer(r) {
			var json = r.responseText.evalJSON();
			/* did any global errors occur? display them */
			if(json['error']) {
				display_error(json['error']);
			} else { /* process the form and its errors */
				var fielderrors = json['fielderrors'] || {};
				var inputWasValid = !json['fielderrors'];
				AJAJForms.displayErrorsFor(form_id, fielderrors);
				if(inputWasValid) {
					$(form_id).getElements().invoke('removeClassName', 'changed');
					AJAJForms.updateMemorizedFields(form_id);
					if(options['onValidInput']) {
						options['onValidInput'](json);
					}
				} else if(options['onInvalidInput']) {
					options['onInvalidInput'](json);
				}
			}
		}
		refer_to.form.request({
			requestHeaders: ['Content-Type', 'application/x-www-form-urlencoded'],
			onSuccess: processSubmitAnswer,
			onFailure: processSubmitAnswer
		});
		return false;
	},

	/**
	 * In case your are using a AJAJForm in a Modalbox and want to have
	 * a grid reloaded once valid input is submitted by the form,
	 * then use this function by overwriting the input[type="submit"].onclick
	 *
	 * @param	e		set to "this".
	 * @param	grid_to_reload	the grid's ID
	 */
	submitAdv: function(e, grid_to_reload) {
		AJAJForms.submit({me: e, onInvalidInput: function() {
			Modalbox.resizeToContent()
		}, onValidInput: function() {
			setTimeout("PagingDataGrid.reload('"+grid_to_reload+"');", 750);
			Modalbox.hide()
		}})
	}
}

var PaginationBar = {
	/* storage for bars' data with bar's id as key */
	decoratedBars: {},
	/* replace these for I18N */
	text: {
		total: 'of %d',
		first: 'first',
		prev: 'prev',
		next: 'next',
		last: 'last',
		reload: 'reload'
	},
	images: {
		enabled: {
			first: '/tg_widgets/scriptaculous/images/nav_first.gif',
			prev: '/tg_widgets/scriptaculous/images/nav_prev.gif',
			next: '/tg_widgets/scriptaculous/images/nav_next.gif',
			last: '/tg_widgets/scriptaculous/images/nav_last.gif',
			reload: '/tg_widgets/scriptaculous/images/reload.gif'
		},
		disabled: {
			first: '/tg_widgets/scriptaculous/images/nav_grey_first.gif',
			prev: '/tg_widgets/scriptaculous/images/nav_grey_prev.gif',
			next: '/tg_widgets/scriptaculous/images/nav_grey_next.gif',
			last: '/tg_widgets/scriptaculous/images/nav_grey_last.gif',
			reload: '/tg_widgets/scriptaculous/images/reload_grey.gif'
		}
	},

	/* remove non-existend bars */
	unlistNonexistendBars: function() {
		var tmp = {};
		for(var bid in PaginationBar.decoratedBars) {
			if(!!$(bid)) {
				tmp[bid] = PaginationBar.decoratedBars[bid];
			}
		}
		PaginationBar.decoratedBars = tmp;
	},

	/* Bar event handlers */
	changePage: function(bar_id, new_page) {
		if(!PaginationBar.decoratedBars[bar_id].locked
		   && PaginationBar.decoratedBars[bar_id].currentPage != new_page) {
			PaginationBar.decoratedBars[bar_id].callbackGotoPage(new_page);
			PaginationBar.decoratedBars[bar_id].currentPage = new_page;
			PaginationBar.decoratedBars[bar_id].controls.pageInput.value = new_page;
		}
		this.resetImages(bar_id);
	},
	first: function() {
		PaginationBar.changePage(this.bar_id, 1);
	},
	prev: function() {
		new_page = Math.max(1, PaginationBar.decoratedBars[this.bar_id].currentPage - 1);
		PaginationBar.changePage(this.bar_id, new_page);
	},
	next: function() {
		new_page = Math.min(PaginationBar.decoratedBars[this.bar_id].maxPage, PaginationBar.decoratedBars[this.bar_id].currentPage + 1);
		PaginationBar.changePage(this.bar_id, new_page);
	},
	last: function() {
		new_page = PaginationBar.decoratedBars[this.bar_id].maxPage;
		PaginationBar.changePage(this.bar_id, new_page);
	},
	reload: function() {
		if(!PaginationBar.decoratedBars[this.bar_id].locked) {
			PaginationBar.decoratedBars[this.bar_id].callbackReload();
		}
	},
	pageInput: function() {
		n = parseInt(this.value);
		if(!isNaN(n) && n >= 1 && n <= PaginationBar.decoratedBars[this.bar_id].maxPage) {
			PaginationBar.changePage(this.bar_id, n);
		} else {
			this.value = PaginationBar.decoratedBars[this.bar_id].currentPage;
		}
	},
	pageInputKP: function(event) {
		if((event.which || event.keyCode) == Event.KEY_RETURN) {
			PaginationBar.pageInput();
		}
	},

	/* Bar functions */
	/** This function is a wrapper which only resets the current page number. */
	setPage: function(bar_id, new_page) {
		PaginationBar.decoratedBars[bar_id].currentPage = new_page;
		PaginationBar.decoratedBars[bar_id].controls.pageInput.value = new_page;
		PaginationBar.resetImages(bar_id);
	},
	resetImages: function(bar_id) {
		var mybar = PaginationBar.decoratedBars[bar_id];
		if(mybar.locked || mybar.currentPage <= 1) {
			mybar.controls.first.src = PaginationBar.images.disabled.first;
			mybar.controls.prev.src = PaginationBar.images.disabled.prev;
		} else {
			mybar.controls.first.src = PaginationBar.images.enabled.first;
			mybar.controls.prev.src = PaginationBar.images.enabled.prev;
		}
		if(mybar.locked || mybar.currentPage >= mybar.maxPage) {
			mybar.controls.next.src = PaginationBar.images.disabled.next;
			mybar.controls.last.src = PaginationBar.images.disabled.last;
		} else {
			mybar.controls.next.src = PaginationBar.images.enabled.next;
			mybar.controls.last.src = PaginationBar.images.enabled.last;
		}
		if(!mybar.locked) {
			mybar.controls.reload.src = PaginationBar.images.enabled.reload;
			mybar.controls.pageInput.disabled = "";
		} else {
			mybar.controls.reload.src = PaginationBar.images.disabled.reload;
			mybar.controls.pageInput.disabled = "disabled";
		}
	},
	setMaxPage: function(bar_id, maxPage) {
		PaginationBar.decoratedBars[bar_id].maxPage = maxPage;
		this.setTotalText(bar_id);
		this.resetImages(bar_id);
	},
	setTotalText: function(bar_id) {
		txt = PaginationBar.text.total.replace('%d', PaginationBar.decoratedBars[bar_id].maxPage);
		PaginationBar.decoratedBars[bar_id].controls.totalSpan.innerHTML = txt;
	},
	lock: function(bar_id) {
		PaginationBar.decoratedBars[bar_id].locked = true;
		this.resetImages(bar_id);
	},
	unlock: function(bar_id) {
		PaginationBar.decoratedBars[bar_id].locked = false;
		this.resetImages(bar_id);
	},

	decorateBar: function(bar) {
		var bar_id = bar.identify();
		if(!PaginationBar.decoratedBars[bar_id]) {
			bar.insert('<img src="'+PaginationBar.images.enabled.first+'" alt="first" class="pBfirst" />'
				   +'<img src="'+PaginationBar.images.enabled.prev+'" alt="prev" class="pBprev" />'
				   +'<div><input type="text" name="page" value="1" />&#160;<span></span></div>'
				   +'<img src="'+PaginationBar.images.enabled.next+'" alt="next" class="pBnext" />'
				   +'<img src="'+PaginationBar.images.enabled.last+'" alt="last" class="pBlast" />'
				   +'<img src="'+PaginationBar.images.enabled.reload+'" alt="reload" class="pBreload" />'
				   +'<hr />');
			var mybar = {
				currentPage: 1,
				maxPage: 1,
				locked: false,
				controls: {
					first: bar.select('.pBfirst')[0],
					prev: bar.select('.pBprev')[0],
					next: bar.select('.pBnext')[0],
					last: bar.select('.pBlast')[0],
					reload: bar.select('.pBreload')[0],
					pageInput: bar.select('input')[0],
					totalSpan: bar.select('span')[0]
				},
				/* overwrite these callbacks with your function */
				callbackGotoPage: function(new_page) {
					alert(new_page);
				},
				callbackReload: function() {
					alert('reload');
				}
			}
			mybar.controls.first.bar_id = bar_id;
			mybar.controls.prev.bar_id = bar_id;
			mybar.controls.next.bar_id = bar_id;
			mybar.controls.last.bar_id = bar_id;
			mybar.controls.reload.bar_id = bar_id;
			mybar.controls.pageInput.bar_id = bar_id;
			Event.observe(mybar.controls.first, 'click', PaginationBar.first);
			Event.observe(mybar.controls.prev, 'click', PaginationBar.prev);
			Event.observe(mybar.controls.next, 'click', PaginationBar.next);
			Event.observe(mybar.controls.last, 'click', PaginationBar.last);
			Event.observe(mybar.controls.reload, 'click', PaginationBar.reload);
			Event.observe(mybar.controls.pageInput, 'change', PaginationBar.pageInput);
			Event.observe(mybar.controls.pageInput, 'keypress', PaginationBar.pageInputKP);
			PaginationBar.decoratedBars[bar_id] = mybar;
			PaginationBar.setTotalText(bar_id);
			PaginationBar.resetImages(bar_id);
		}
		return bar_id;
	},

	decoratePagingBars: function() {
		PaginationBar.unlistNonexistendBars();
		$$('div.paginationBar').each(PaginationBar.decorateBar);
	}
}

/**
 * You will want use this widget that way:
 * 1. Place an empty container element somewhere in your document.
 * 2. Create a grid by PagingDataGrid.init
 * If you intend to call something by hand, you will want to utilize these:
 * - PagingDataGrid.reload
 * - PagingDataGrid.gotoPage
 *
 * @see			http://tgwidgets.ossdl.de/wiki/Scriptaculous/PagingDataGrid
 */
var PagingDataGrid = {
	/** storage for grids' data with grid's id as key */
	decorated: {},

	/** Does remove non-existend items. Safe to call. */
	unlistNonexistend: function() {
		var tmp = {};
		for(var bid in PagingDataGrid.decorated) {
			if(!!$(bid)) {
				tmp[bid] = PagingDataGrid.decorated[bid];
			}
		}
		PagingDataGrid.decorated = tmp;
	},

	/**
	 * Helper function to assembly table headers with appropriate attributes.
	 * Is used in PagingDataGrid.redrawGrid
	 */
	_makeGridTH: function(container_id, properties) {
		var th = '<th'
			+ (properties.width && ' width="'+properties.width+'"' || '')
			+ '><div'
			+ (properties.sortable && ' class="sortable" onclick="PagingDataGrid.sortBy(\''+container_id+'\', \''+properties.dataIndex+'\', this)"' || '')
			+ '>' + (properties.header || '') + '</div></th>';
		return th;
	},

	/**
	 * Is called by PagingDataGrid._initWithProperties to fill the empty
	 * container element with the grid's basic structure.
	 *
	 * You shouldn't use this one unless you change the grid's properties
	 * after its creation. In that case you must also call reload to have
	 * the newly created table filled with data!
	 */
	redrawGrid: function(container_id) {
		var cdat = PagingDataGrid.decorated[container_id];
		var n = $(container_id);
		n.addClassName('pagingDataGrid');
		var headers = cdat.properties.columnModel.collect(function(p) {return PagingDataGrid._makeGridTH(container_id, p)}).join('');
		n.update('<table cellspacing="0" cellpadding="0" border="0"><thead><tr>'+headers+'</tr></thead><tbody></tbody><tfoot><tr><td colspan="'+cdat.properties.columnModel.length+'"><div class="grid_pagingbar paginationBar""></div><div class="grid_paginginfo"></div></td></tr></tfoot></table>');
		/* grid_pagingbar */
		PaginationBar.unlistNonexistendBars();
		var pbid = PaginationBar.decorateBar(n.select('.grid_pagingbar')[0]);
		cdat.pagination_bar_id = pbid;
		PaginationBar.decoratedBars[pbid].callbackGotoPage = function(page) {
			PagingDataGrid.gotoPage(container_id, page)
		};
		PaginationBar.decoratedBars[pbid].callbackReload = function() {
			PagingDataGrid.reload(container_id)
		};
	},

	/**
	 * Is called by PagingDataGrid._SetContent to display the pagination
	 * information. If you happen to manipulate data inside the grid's table
	 * you should also call this one.
	 */
	setTotalText: function(container_id) {
		var txt = '';
		var cdat = PagingDataGrid.decorated[container_id];
		if(cdat.total <= 0) {
			txt = cdat.properties.no_items_message;
		} else {
			txt = cdat.properties.display_message
				.replace('{0}', cdat.start + 1)
				.replace('{1}', Math.min(cdat.start + cdat.limit, cdat.total))
				.replace('{2}', cdat.total);
		}
		$(container_id).select('.grid_paginginfo')[0].update(txt);
	},

	/** Utilized whenever rows are added to grid. E.g., in _setContent */
	classifyRowsEvenOdd: function(grid_id) {
		var rows = $(grid_id).select('tbody tr');
		for(var i = 0; i < rows.length; i++) {
			rows[i].addClassName(i % 2 && 'odd' || 'even').removeClassName(i % 2 && 'even' || 'odd');
		}
	},

	/** Helper function for _setContent */
	_renderRow: function(container_id, row) {
		var props = PagingDataGrid.decorated[container_id].properties;
		var tr = '<tr id="'+container_id+'_row'+row[props.metadata.id]+'">';
		tr += props.columnModel.collect(function(col) {
			return '<td><div'
				+(col.width && ' style="width: '+col.width+'px"' || '')
				+'>'+(row[col.dataIndex] || '')+'</div></td>';
		}).join('');
		tr += '</tr>';
		return tr;
	},

	/**
	 * Callback for PagingDataGrid.reload as content might get loaded asynchronously.
	 * If append is set, the new content gets appended to existing.
	 *   As after that the users will want to delete entries,
	 * classifyRowsEvenOdd is not called.
	 */
	_setContent: function(container_id, def_d, append) {
		var cdat = PagingDataGrid.decorated[container_id];
		var props = cdat.properties;
		var content = def_d[props.metadata.root].collect(function(row) {
			return PagingDataGrid._renderRow(container_id, row);
		}).join('');
		var tbody = $(container_id).select('tbody')[0];
		if(append) {
			tbody.insert(content);
		} else {
			tbody.update(content);
			PagingDataGrid.classifyRowsEvenOdd(container_id);
		}
		cdat.total = def_d[props.metadata.totalProperty];
		PagingDataGrid.setTotalText(container_id);
		PaginationBar.setMaxPage(cdat.pagination_bar_id, Math.ceil(cdat.total/cdat.limit));
		PaginationBar.unlock(cdat.pagination_bar_id);
	},


	/**
	 * Use this only with data being a JSON-queryable source.
	 * Please consider using PagingDataGrid.removeRow than this one.
	 */
	getOneMoreRow: function(grid_id) {
		var d = PagingDataGrid.decorated[grid_id];
		PaginationBar.lock(d.pagination_bar_id);
		new Ajax.Request(d.data, {
			method: 'post',
			requestHeaders: ['Content-Type', 'application/x-www-form-urlencoded'],
			parameters: Object.extend(d.data_parameters, {'start': Math.max(d.start+d.limit-1, 0), 'limit': 1}),
			onSuccess: function(r) {
				var json = r.responseText.evalJSON();
				PagingDataGrid._setContent(grid_id, json, true);
			}
		});
	},

	/**
	 * Helper function for your grid manipulations, to be used as onSuccess
	 * callback. You are expected to do the deletion on server-side.
	 *
	 * @requires	Scriptaculous
	 */
	removeRow: function(grid_id, row_id) {
		var row = grid_id+'_row'+row_id;
		PagingDataGrid.getOneMoreRow(grid_id);
		new Effect.Fade(row, {afterFinish: function() {
			$(row).remove();
			PagingDataGrid.classifyRowsEvenOdd(grid_id);
		}})
	},

	/**
	 * This one is called whenever the user clicks on a sortable TH.
	 * Event handler assignment is done in PagingDataGrid._makeGridTH
	 *
	 * @param	dataIndex	name of the data column to be sorted on
	 * @param	e		optionally the clicked TH
	 */
	sortBy: function(container_id, dataIndex, e) {
		var cdat = PagingDataGrid.decorated[container_id];
		if(cdat.data_parameters.sort == dataIndex) {
			cdat.data_parameters.dir = cdat.data_parameters.dir == 'ASC' && 'DESC' || 'ASC';
		} else {
			cdat.data_parameters.sort = dataIndex;
			cdat.data_parameters.dir = 'ASC';
		}
		PagingDataGrid.reload(container_id);
		$(container_id).select('thead th div')
			.invoke('removeClassName', 'sort_ASC')
			.invoke('removeClassName', 'sort_DESC');
		if(e) {
			e.addClassName(cdat.data_parameters.dir == 'ASC' && 'sort_ASC' || 'sort_DESC');
		}
	},

	/**
	 * Use this in case you want manipulate data_parameters. E.g.,
	 * for implementing a server-side search function.
	 * Does not reload the data after resetting sorting arguments, so
	 * either call reload or, preferably, gotoPage(..., 1).
	 */
	resetSort: function(container_id) {
		var cdat = PagingDataGrid.decorated[container_id];
		delete cdat.data_parameters.sort;
		delete cdat.data_parameters.dir;
		$(container_id).select('thead th')
			.invoke('removeClassName', 'sort_ASC')
			.invoke('removeClassName', 'sort_DESC');
	},

	/**
	 * Use in server-side search functions.
	 *
	 * @param	data_parameters		Place your search string preferably here. E.g., {'token': xy}
	 * 					or leave empty to have the additional data cleared (i.e., in end of search)
	 */
	setNewData: function(grid_id, data, data_parameters) {
		PagingDataGrid.resetSort(grid_id);
		var d = PagingDataGrid.decorated[grid_id];
		d.data = data;
		if(data_parameters) {
			d.data_parameters = Object.extend(d.data_parameters, data_parameters);
		} else {
			d.data_parameters = {};
		}
		PagingDataGrid.gotoPage(grid_id, 1);
	},

	/**
	 * Use this as callback or in any other interactive elements.
	 * Is called every time new content shall be pulled from data's location.
	 */
	reload: function(container_id) {
		var d = PagingDataGrid.decorated[container_id];
		var ds = String(d.data);
		PaginationBar.lock(d.pagination_bar_id);
		if(ds[0] == "[" && ds.isJSON()) {
			PagingDataGrid._setContent(container_id, ds.evalJSON());
		} else if(typeof(d.data) == "function") {
			d.data(container_id, d.start, d.limit, function(def_d) {
				PagingDataGrid._setContent(container_id, def_d);
			});
		} else {
			new Ajax.Request(d.data, {
				method: 'post',
				requestHeaders: ['Content-Type', 'application/x-www-form-urlencoded'],
				parameters: Object.extend(d.data_parameters, {'start': d.start, 'limit': d.limit}),
				onSuccess: function(r) {
					var json = r.responseText.evalJSON();
					PagingDataGrid._setContent(container_id, json);
				}
			});
		}
	},

	/** Use this as callback or in any other interactive elements. */
	gotoPage: function(grid_id, page) {
		var cdat = PagingDataGrid.decorated[grid_id];
		cdat.start = Math.min(Math.max(0, page - 1)*cdat.limit, Math.floor(cdat.total/cdat.limit)*cdat.limit);
		PagingDataGrid.reload(grid_id);
		PaginationBar.setPage(cdat.pagination_bar_id, page);
	},

	/**
	 * This is the callback for PagingDataGrid.init.
	 * The latter might be called with an address to get properties from,
	 * so this part of initialization should be done asynchronously.
	 *
	 * @param	def_p		definite/constant hash of properties
	 */
	_initWithProperties: function(container_id, data, def_p) {
		PagingDataGrid.decorated[container_id] = {
			start: 0, // not currentPage!
			total: 1, // not maxPage!
			limit: 25,
			data: data,
			data_parameters: {}, // will be send along with start and limit on page changes or reloads
			properties: def_p
		};
		PagingDataGrid.redrawGrid(container_id);
		PagingDataGrid.reload(container_id);
	},

	/**
	 * Call this method in order to create a paging data grid.
	 * You will have to place a container element somewehere in which the
	 * grid will be written later by PagingDataGrid.redrawGrid and finally
	 * PagingDataGrid._setContent .
	 *
	 * @param	container_id	ID of the container the grid will be written into.
	 * 				(Hint: call Element#identify())
	 * @param	data		Either a JSON String with the data to be displayed,
	 * 				or a function to return that data
	 * 				or an URL the data can be pulled from.
	 * @param	properties	The same as in data, but for properties.
	 * 				This is only read at initialization.
	 */
	init: function(container_id, data, properties) {
		var p = String(properties);
		if(p[0] == "{" && p.isJSON()) {
			PagingDataGrid._initWithProperties(container_id, data, p.evalJSON());
		} else if(typeof(properties) == "function") {
			properties(container_id, data, function(def_p) {
				PagingDataGrid._initWithProperties(container_id, data, def_p);
			});
		} else {
			new Ajax.Request(properties, {
				method: 'get',
				requestHeaders: ['Content-Type', 'application/x-www-form-urlencoded'],
				onSuccess: function(r) {
					var json = r.responseText.evalJSON();
					PagingDataGrid._initWithProperties(container_id, data, json);
				}
			});
		}
	}
}
