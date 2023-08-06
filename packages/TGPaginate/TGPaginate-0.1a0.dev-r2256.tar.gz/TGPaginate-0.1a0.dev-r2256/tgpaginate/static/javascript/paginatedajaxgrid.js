var PaginatedAjaxGrid = Class.create(); 

PaginatedAjaxGrid.prototype = {};

PaginatedAjaxGrid.prototype.initialize = 
function(table, options) { 
    this.options = options;
    this.table = $(table);
    this.table.ajax = this;
    this.current_page = 1;
    if (!this.options.no_init) {
        Event.observe(window, 'load', 
                      function() {this.show_page(1);}.bind(this));
    }
}

PaginatedAjaxGrid.prototype.refresh =
function() {
    this.show_page(this.current_page);
}

PaginatedAjaxGrid.prototype.show_page =
function(page_no) {
    var search_params = $H(this.options.search_params)
    search_params['tg_paginate_' + this.options.var_name + '_no'] = page_no;
    search_params = search_params.toQueryString();
    
    var this_ = this;
    var onSuccess = function(e) {this_.update_grid_from_request(e)};
    var onFailure = function(e) {this_.bad_request(e)};
    var onComplete = function(e) {$(this_.table.id + '_spinner').hide();};
    
    var request_options = {method: 'post', parameters: search_params,
                       onSuccess: onSuccess, onFailure: onFailure,
                       onComplete: onComplete};
    
    $(this_.table.id + '_spinner').show();
    var request = new Ajax.Request(this.options.url, request_options);
}

PaginatedAjaxGrid.prototype.update_grid_from_request =
function(request) {
    eval('results = ' + request.responseText);
    
    this.current_page = 
        Number(request.getResponseHeader(
               'tg_paginate_' + this.options.var_name + '_current_page'));
    
    this.last_page_count = 
        Number(request.getResponseHeader('tg_paginate_' +
                                         this.options.var_name +
                                         '_page_count'));
    
    this.nav_links = 
        request.getResponseHeader('tg_paginate_' + this.options.var_name +
                                  '_nav_links');
        
    // update the navigation links
    this.update_nav_links();
    
    // update grid data
    this.update_grid(results[this.options.var_name]);
}

// updates the navigation links
PaginatedAjaxGrid.prototype.update_nav_links =
function() {
    var old_nav_links = $(this.table.id + '_nav_links');
    var new_nav_links = document.createElement('div');
    new_nav_links.setAttribute('id', this.table.id + '_nav_links');
    new_nav_links.className = 'nav_links';
    
    var this_ = this;
    function create_link_to(page_no, text) {
        a = document.createElement('a');
        _on_click = function(e) { this.show_page(page_no); }.bind(this_);
        Event.observe(a, 'click', _on_click);
        a.appendChild(document.createTextNode(text));
        return a
    }
    
    // first
    new_nav_links.appendChild(create_link_to(1, '<<'));
    
    // previous
    var a = document.createElement('a');
    _on_click = function(e) { this.previous_page(); }.bind(this);
    Event.observe(a, 'click', _on_click);
    a.appendChild(document.createTextNode('<'));
    new_nav_links.appendChild(a);
    
    // pages
    if (this.nav_links) {
        $A(this.nav_links.split(',')).each(
            function (page_no) {
                if (page_no == this_.current_page) {
                    var span = document.createElement('span')
                    span.className = 'current_page';
                    span.appendChild(
                        document.createTextNode('[' + page_no + ']'));
                    new_nav_links.appendChild(span);
                } else {
                    new_nav_links.appendChild(create_link_to(page_no, page_no));
                }
            }
        );
    }
    
    // next
    a = document.createElement('a');
    
    _on_click = function(e) { this.table.ajax.next_page(); }.bind(this);
    Event.observe(a, 'click', _on_click);
    
    a.appendChild(document.createTextNode('>'));
    new_nav_links.appendChild(a);    
    
    // last
    new_nav_links.appendChild(create_link_to(this.last_page_count, '>>'));
    
    // replace the nav links with the new ones
    old_nav_links.parentNode.replaceChild(new_nav_links, old_nav_links);
    
    // update the page info
    $(this.table.id + '_page_info').innerHTML = this.current_page + ' / ' +
                                                this.last_page_count;
}

PaginatedAjaxGrid.prototype.bad_request =
function(request) {
    alert('There was a problem updating the grid (code: ' + 
          request.status + ')');
}

// builds table body from data
PaginatedAjaxGrid.prototype.update_grid =
function(data) {
    // create a new tbody
    tbody = document.createElement('TBODY');
    
    var counter = 1;
    var scripts = $A();
    
    $A(data).each(
        function(row) {
            var tr = document.createElement('TR');
            counter++ % 2 ? tr.className = 'odd' : tr.className = 'even';
            
            if (row['__row_attributes']) {
                $H(row['__row_attributes']).each(function (attr) {
                    if (attr[0] == 'class') {
                        tr.addClassName(attr[1]);
                    } else {
                        tr.setAttribute(attr[0], attr[1]);
                    };
                });
            }
            
            make_td = function(html) {
                html = String(html);
                
                if (this.options.eval_scripts) {
                    scripts.push(html);
                }
                
                td = document.createElement('TD');
                td.innerHTML = html.stripScripts();
                tr.appendChild(td);
                
            }.bind(this);
            
            if (!row[0]) {
                // the results are a list of associative arrays
                this.options.columns.each(
                    function (col) {
                        if (row[col]) {
                            make_td(row[col]);
                        } else {
                            make_td('');
                        }
                    }
                )
            } else {
                // the results are a list of lists
                row.each(make_td)
            }
            if (this.options.row_selector) {
                Event.observe(tr, 'click', 
                    function() { this.options.row_selector(row); }.bind(this)
                );
                tr.style.cursor = 'pointer';
            }
            tbody.appendChild(tr);
        }.bind(this)
    );
    
    // replace the table's body
    old_tbody = this.table.getElementsByTagName('TBODY')[0];
    old_tbody.parentNode.replaceChild(tbody, old_tbody);
    
    // execute the scripts contained in the columns if specified.
    if (this.options.eval_scripts) {
        scripts.each(function(html) {
            html.evalScripts();
        });
    }
}

// shows the next page
PaginatedAjaxGrid.prototype.next_page =
function() {
    if (this.last_page_count <= (this.current_page)) {
        return false;
    }
    
    this.show_page(this.current_page + 1);
}

// shows the previous page
PaginatedAjaxGrid.prototype.previous_page =
function() {
    if (this.current_page <= 1) {
        return false;
    }
    this.show_page(this.current_page - 1);
}

