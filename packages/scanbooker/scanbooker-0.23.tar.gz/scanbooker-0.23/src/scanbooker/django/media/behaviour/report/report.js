var Report = new Class({
    Extends: ElementObject,
    Implements: Options,
    options: {
        'id': 'report', 
        'reportId': null,
        'reportTitle': '',
        'rpcUrl': null,
        'insertFilterTemplate': [
            '<div class="report-actions">',
            '  <a class="filter-create" href="" title="Create"><img height="16" width="16" src="'+mediaUrl+'/images/icon-edit.png" alt="Create" /></a>',
            '</div><br/>',
        ].join("\n"),   
        'insertColumnTemplate': [
            '<div class="report-actions">',
            '  <a class="column-create" href="" title="Create"><img height="16" width="16" src="'+mediaUrl+'/images/icon-edit.png" alt="Create" /></a>',
            '</div><br/>',
        ].join("\n"),   
        'filterTemplateName': [
            '<div class="report-actions">',
            '  <a class="filter-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="filter-names">',
            '  %(nameOptions)',
            '</select>',
        ].join("\n"),   
        'filterTemplateNameMode': [
            '<div class="report-actions">',
            '  <a class="filter-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="filter-names">',
            '  %(nameOptions)',
            '</select>',
            '<select class="filter-modes">',
            '  %(modeOptions)',
            '</select>',
        ].join("\n"),   
        'filterTemplateNameModeText': [
            '<div class="report-actions">',
            '  <a class="filter-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="filter-names">',
            '  %(nameOptions)',
            '</select>',
            '<select class="filter-modes">',
            '  %(modeOptions)',
            '</select>',
            '<input class="filter-value" type="text"/>',
        ].join("\n"),   
        'filterTemplateNameModeCheck': [
            '<div class="report-actions">',
            '  <a class="filter-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="filter-names">',
            '  %(nameOptions)',
            '</select>',
            '<select class="filter-modes">',
            '  %(modeOptions)',
            '</select>',
            '<input class="filter-value" type="checkbox"/>',
        ].join("\n"),   
        'filterTemplateNameModeSelection': [
            '<div class="report-actions">',
            '  <a class="filter-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="filter-names">',
            '  %(nameOptions)',
            '</select>',
            '<select class="filter-modes">',
            '  %(modeOptions)',
            '</select>',
            '<select class="filter-selection">',
            '  %(selectionOptions)',
            '</select>',
        ].join("\n"),   
        'columnTemplateName': [
            '<div class="report-actions">',
            '  <a class="column-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="column-names">',
            '  %(nameOptions)',
            '</select>',
        ].join("\n"),   
        'columnTemplateNameQual': [
            '<div class="report-actions">',
            '  <a class="column-delete" href="" title="Delete"><img height="16" width="16" src="'+mediaUrl+'/images/icon-delete.png" alt="Delete" /></a>',
            '</div>',
            '<select class="column-names">',
            '  %(nameOptions)',
            '</select>',
            '<select class="column-quals">',
            '  %(qualOptions)',
            '</select>',
        ].join("\n"),   
    },
    initialize: function (options) {
        this.setOptions(options);
        this.id = this.options.id;
        this.reportId = this.options.reportId;
        this.reportTitle = this.options.reportTitle;
        this.parent('div', {id: this.id});
        this.setElementFromDom();
    },
    addRpcService: function (url) {
        this.rpcService = new MooRpcService(url);
        return this.rpcService;
    },
    initReport: function (reportId) {
        this.reportId = reportId;
        $$('form.report-update').addEvent('submit', this.stopEvent.bind(this));
        var titleElem = $('id_title');
        titleElem.addEvent('keyup', this.updateReportTitle.bind(this));
        titleElem.addEvent('change', this.updateReportTitle.bind(this));
        this.reportTitle = titleElem.value;
        this.rpcService.getReportFilters(this.reportId).callback(
            this.initFilterElements.bind(this)
        );
    },
    initFilterElements: function (filtersMsg) {
        var filterMsgs = filtersMsg.filters;
        this.clearFilters();
        //console.log('Appending filters');
        //console.log(filterMsgs);
        $each(filterMsgs, function (filterMsg) {
            this.appendFilterInsertControl(filterMsg.filterId || '0');
            this.appendFilterElement(filterMsg);
        }, this);
        this.appendFilterInsertControl('0');
        this.rpcService.getReportColumns(this.reportId).callback(
            this.initColumnElements.bind(this)
        );
        return this;
    },
    initColumnElements: function (columnsMsg) {
        var columnMsgs = columnsMsg.columns;
        this.clearColumns();
        //console.log('Appending columns');
        //console.log(columnMsgs);
        $each(columnMsgs, function (columnMsg) {
            this.appendColumnInsertControl(columnMsg.column.id || '0');
            this.appendColumnElement(columnMsg);
        }, this);
        this.appendColumnInsertControl('0');
        return this;
    },
    appendFilterElement: function (filterMsg) {
        var elem = document.createElement('div');
        var filterId = filterMsg.filterId;
        elem.addClass('filter-update');
        elem.setAttribute('filterid', filterId);
        if (filterMsg.filter.next) {
            var filterElem = this.getFilterElement(filterMsg.filter.next);
            if (filterElem) {
                elem.inject(filterElem, 'before');
            }
        }
        if (! elem.getParent() ) {
            this.filtersElement().appendChild(elem);
        }
        this.updateFilterElement(filterMsg);
        return this;
    },
    appendColumnElement: function (columnMsg) {
        var elem = document.createElement('div');
        var columnId = columnMsg.column.id;
        elem.addClass('column-update');
        elem.setAttribute('columnid', columnId);
        if (columnMsg.column.next) {
            var columnElem = this.getColumnElement(columnMsg.column.next);
            if (columnElem) {
                elem.inject(columnElem, 'before');
            }
        }
        if (! elem.getParent() ) {
            this.columnsElement().appendChild(elem);
        }
        this.updateColumnElement(columnMsg);
        return this;

    },
    updateFilterElement: function (filterMsg) {
        var filterId = filterMsg.filterId;
        var filter = this.getFilterElement(filterId);
        filter.setHTML(this.createFilterHTML(filterMsg));
        filter.getElements('input.filter-value').each(function (input) {
            if (input.type == "checkbox") {
                if (filterMsg.filter.value) {
                    input.checked = true;
                } else {
                    input.checked = false;
                }
            } else {
                input.value = filterMsg.filter.value;
            }
        });
        filter.getElements('select.filter-names').addEvent('change',
            this.updateFilterName.bind(this));
        filter.getElements('select.filter-modes').addEvent('change',
            this.updateFilterMode.bind(this));
        filter.getElements('input.filter-value').addEvent('change',
            this.updateFilterValue.bind(this));
        filter.getElements('select.filter-selection').addEvent('change',
            this.updateFilterValue.bind(this));
        filter.getElements('a.filter-delete').addEvent(
            'click', this.deleteFilter.bind(this));
    },
    updateColumnElement: function (columnMsg) {
        var columnId = columnMsg.column.id;
        var column = this.getColumnElement(columnId);
        column.setHTML(this.createColumnHTML(columnMsg));
        column.getElements('select.column-names').addEvent('change',
            this.updateColumnName.bind(this));
        column.getElements('select.column-quals').addEvent('change',
            this.updateColumnQual.bind(this));
        column.getElements('a.column-delete').addEvent(
            'click', this.deleteColumn.bind(this));
    },
    createFilterHTML: function (filterMsg) {
        var filterType = filterMsg.filterType;
        //console.log('Filter type: ' + filterType);
        var filterTemplate = this.options.filterTemplateName;
        if (filterType == 'Text') {
            filterTemplate = this.options.filterTemplateNameModeText;
        } else if (filterType == 'Date') {
            filterTemplate = this.options.filterTemplateNameModeText;
        } else if (filterType == 'Check') {
            filterTemplate = this.options.filterTemplateNameModeCheck;
        } else if (filterType == 'Selection') {
            filterTemplate = this.options.filterTemplateNameModeSelection;
        } else if (filterType == 'Selection') {
            filterTemplate = this.options.filterTemplateNameModeSelection;
        }
        //console.log('Filter template: ' + filterTemplate);
        var nameOptionsHTML = ''
        $each(filterMsg.nameOptions, function (nameOption) {
            nameOptionsHTML += '<option'
            nameOptionsHTML += ' value="'+nameOption[0]+'"';
            if (filterMsg.filter.name == nameOption[0]) {
                nameOptionsHTML += ' selected="selected" ';
            }
            nameOptionsHTML += '>'+nameOption[1]+'</option>';
        }, this);
        var modeOptionsHTML = '';
        $each(filterMsg.modeOptions, function (modeOption) {
            modeOptionsHTML += '<option'
            modeOptionsHTML += ' value="'+modeOption[0]+'"';
            if (filterMsg.filter.mode == modeOption[0]) {
                modeOptionsHTML += ' selected="selected" ';
            }
            modeOptionsHTML += '>'+modeOption[1]+'</option>';
        }, this);
        var selectionOptionsHTML = '';
        $each(filterMsg.selectionOptions, function (selectionOption) {
            var selectionValue = selectionOption[0];
            var selectionTitle = selectionOption[1];
            selectionOptionsHTML += '<option';
            selectionOptionsHTML += ' value="'+selectionValue+'"';
            if (filterMsg.filter.value == selectionValue) {
                selectionOptionsHTML += ' selected="selected" ';
            }
            selectionOptionsHTML += '>'+selectionTitle+'</option>';
        }, this);
        var filterTemplateValues = {
            'nameOptions': nameOptionsHTML,
            'modeOptions': modeOptionsHTML,
            'selectionOptions': selectionOptionsHTML,
        };
        //console.log('Filter template values: ' + filterTemplateValues);
        var html = RND(filterTemplate, filterTemplateValues);
        //console.log('Filter HTML: ' + html);
        return html;
    },
    createColumnHTML: function (columnMsg) {
        var nameOptionsHTML = ''
        $each(columnMsg.nameOptions, function (nameOption) {
            nameOptionsHTML += '<option'
            nameOptionsHTML += ' value="'+nameOption[0]+'"';
            if (columnMsg.column.name == nameOption[0]) {
                nameOptionsHTML += ' selected="selected" ';
            }
            nameOptionsHTML += '>'+nameOption[1]+'</option>';
        }, this);
        var qualOptionsHTML = ''
        $each(columnMsg.qualOptions, function (qualOption) {
            qualOptionsHTML += '<option'
            if (columnMsg.column.qual == qualOption) {
                qualOptionsHTML += ' selected="selected" ';
            }
            qualOptionsHTML += '>'+qualOption+'</option>';
        }, this);
        var columnTemplate = this.options.columnTemplateName;
        if (columnMsg.column.name) {
            columnTemplate = this.options.columnTemplateNameQual;
        }
        var html = RND(columnTemplate, {
            'nameOptions': nameOptionsHTML,
            'qualOptions': qualOptionsHTML,
        })
        return html;
    },
    appendFilterInsertControl: function (filterId) {
        elem = document.createElement('div');
        elem.setHTML(RND(this.options.insertFilterTemplate, {}));
        elem.addClass('filter-insert');
        elem.getElements('a').addEvent('click', this.insertFilter.bind(this));
        if (filterId) {
            var filterElement = this.getFilterElement(filterId);
            if (filterElement) {
                elem.inject(filterElement, 'after');
            }
        }
        if (! elem.getParent() ) {
            this.filtersElement().appendChild(elem);
        }
        return this;
    },
    appendColumnInsertControl: function (columnId) {
        elem = document.createElement('div');
        elem.setHTML(RND(this.options.insertColumnTemplate, {}));
        elem.addClass('column-insert');
        elem.getElements('a').addEvent('click', this.insertColumn.bind(this));
        if (columnId) {
            var columnElement = this.getColumnElement(columnId);
            if (columnElement) {
                elem.inject(columnElement, 'after');
            }
        }
        if (! elem.getParent() ) {
            this.columnsElement().appendChild(elem);
        }
        return this;
    },
    insertFilter: function (ev) {
        this.stopEvent(ev);
        var reportId = this.reportId;
        var filterId = this.getAttrFromInsertTarget(ev.target, 'filterid');
        this.rpcService.insertFilter(reportId, filterId).callback(
            this.insertFilterElement.bind(this)
        );
    },
    insertColumn: function (ev) {
        this.stopEvent(ev);
        var reportId = this.reportId;
        var columnId = this.getAttrFromInsertTarget(ev.target, 'columnid');
        this.rpcService.insertColumn(reportId, columnId).callback(
            this.insertColumnElement.bind(this)
        );
    },
    getAttrFromInsertTarget: function (target, attrName) {
        var elem = target.getParent().getParent();
        var attrValue = 0;
        if (elem.getNext()) {
            attrValue = elem.getNext().getAttribute(attrName);
        }
        if (!attrValue && elem.getParent().getNext()) {
            attrValue = elem.getParent().getNext().getAttribute(attrName);
        }
        return attrValue;
    },
    insertColumnElement: function (columnMsg) {
        this.appendColumnElement(columnMsg);
        this.appendColumnInsertControl(columnMsg.column.id || '0');
    },
    insertFilterElement: function (filterMsg) {
        this.appendFilterElement(filterMsg);
        this.appendFilterInsertControl(filterMsg.filterId || '0');
    },
    updateReportTitle: function (ev) {
        //ev = new Event(ev);
        //ev.stop();
        var reportTitle = $('id_title').value;
        //console.log('this.reportTitle: ' + this.reportTitle);
        //console.log('reportTitle: ' + reportTitle);
        if (this.reportTitle != reportTitle) {
            this.reportTitle = reportTitle;
            //console.log('Updating report title: ' + reportTitle);
            this.rpcService.updateReportTitle(reportId, reportTitle).callback(
                this.updateReportTitleElement.bind(this)
            );
        } else {
            //console.log('Not updating report title: ' + reportTitle);
        }
    },
    updateReportTitleElement: function (booleanMsg) {
        if (booleanMsg) {
            $('report-title').setText('Report ' + this.reportTitle);
        }
    },
    updateFilterName: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var filterId = ev.target.getParent().getAttribute('filterid');
        var filterName = ev.target.value;
        //console.log('Updating filter name: '+' '+filterName+', '+filterId);
        this.rpcService.updateFilterName(filterId, filterName).callback(
            this.updateFilterElement.bind(this)
        );
    },
    updateFilterMode: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var filterId = ev.target.getParent().getAttribute('filterid');
        var filterMode = ev.target.value;
        //console.log('Updating filter mode: '+' '+filterMode+', '+filterId);
        this.rpcService.updateFilterMode(filterId, filterMode).callback(
            this.updateFilterElement.bind(this)
        );
    },
    updateFilterValue: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var filterId = ev.target.getParent().getAttribute('filterid');
        var filterValue;
        if (ev.target.type == 'checkbox') {
            if (ev.target.checked) {
                filterValue = 'on';
            } else {
                filterValue = '';
            }
        } else {
            filterValue = ev.target.value;
        }
        console.log('Updating filter value: '+' '+filterValue+', '+filterId);
        this.rpcService.updateFilterValue(filterId, filterValue).callback(
            this.updateFilterElement.bind(this)
        );
    },
    updateColumnName: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var columnId = ev.target.getParent().getAttribute('columnid');
        //console.log('Updating column id: ' + columnId);
        var columnName = ev.target.value;
        this.rpcService.updateColumnName(columnId, columnName).callback(
            this.updateColumnElement.bind(this)
        );
    },
    updateColumnQual: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var columnId = ev.target.getParent().getAttribute('columnid');
        //console.log('Updating column id: ' + columnId);
        var columnQual = ev.target.value;
        this.rpcService.updateColumnQual(columnId, columnQual).callback(
            this.updateColumnElement.bind(this)
        );
    },
    deleteFilter: function (ev) {
        ev = new Event(ev);
        ev.stop();
        var filterId = ev.target.getParent().getParent().getAttribute('filterid');
        elem = ev.target.getParent().getParent();
        var filterId = elem.getAttribute('filterid') || elem.getParent().getAttribute('filterid');
        this.rpcService.deleteFilter(filterId).callback(
            this.deleteFilterElement.bind(this)
        );
    },
    deleteColumn: function (ev) {
        ev = new Event(ev);
        ev.stop();
        console.log(ev.target.tagName);
        elem = ev.target.getParent().getParent();
        var columnId = elem.getAttribute('columnid') || elem.getParent().getAttribute('columnid');
        this.rpcService.deleteColumn(columnId).callback(
            this.deleteColumnElement.bind(this)
        );
    },
    deleteFilterElement: function (filterMsg) {
        var filterId = filterMsg.filterId;
        var child = this.getFilterElement(filterId);
        var parent = child.getParent()
        var insertCtrl = child.getNext()
        parent.removeChild(insertCtrl);
        parent.removeChild(child);
    },
    deleteColumnElement: function (columnMsg) {
        var columnId = columnMsg.column.id;
        var child = this.getColumnElement(columnId);
        var parent = child.getParent()
        var insertCtrl = child.getNext()
        parent.removeChild(insertCtrl);
        parent.removeChild(child);
    },
    getFilterElement: function (filterId) {
        //console.log("Looking for filter: " + filterId);
        var filter;
        this.filtersElement().getChildren().each(function (child) {
            //console.log("  -- filter: " + child.getAttribute('filterid'));
            if (child.getAttribute('filterid') == filterId) {
                filter = child;
            }
        });
        if (filter) {
            //console.log("Found element for filter: " + filterId);
        } else {
            //console.log("Couldn't find element for filter: " + filterId);
        }
        return filter;
    },
    getColumnElement: function (columnId) {
        if (!columnId) {
            //console.log("Not looking for column: undefined id.");
        } else {
            //console.log("Looking for column: " + columnId);
        }
        var column;
        this.columnsElement().getChildren().each(function (child) {
            //console.log("  -- column: " + child.getAttribute('columnid'));
            if (child.getAttribute('columnid') == columnId) {
                column = child;
            }
        });
        if (column) {
            //console.log("Found element for column: " + columnId);
            //console.log(column);
        } else {
            //console.log("Couldn't find element for column: " + columnId);
        }
        return column;
    },
    clearFilters: function () {
        this.filtersElement().setHTML('');
        return this;
    },
    clearColumns: function () {
        this.columnsElement().setHTML('');
        return this;
    },
    filtersElement: function () {
        return $('report-filters');
    },
    columnsElement: function () {
        return $('report-columns');
    },
    stopEvent: function (ev) {
        ev = new Event(ev);
        ev.stop();
    },
});

