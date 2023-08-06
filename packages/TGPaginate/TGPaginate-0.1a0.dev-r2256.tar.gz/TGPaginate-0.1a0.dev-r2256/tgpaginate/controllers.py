from math import ceil
import logging

import cherrypy
from sqlobject.main import SelectResults, classregistry

import turbogears
from turbogears.decorator import weak_signature_decorator
from turbogears.view import variable_providers
from turbogears.widgets import PaginateDataGrid

log = logging.getLogger("tgpaginate")

def paginate(var_name, default_order='', limit=10,
            allow_limit_override=False, max_pages=5):
    def entangle(func):
        def decorated(func, *args, **kw):
            
            def get_param(param, default):
                param = param % var_name
                return kw.pop(param, default)
            
            page = int(get_param('tg_paginate_%s_no', 1))
            limit_ = int(get_param('tg_paginate_%s_limit', limit))
            order = get_param('tg_paginate_%s_order', default_order)
            reversed = get_param('tg_paginate_%s_reversed', None)
            
            if not allow_limit_override:
                limit_ = limit
            
            log.debug("Pagination params: page=%s, limit=%s, order=%s, "
                      "reversed=%s", page, limit_, order, reversed)
            
            # get the output from the decorated function    
            output = func(*args, **kw)
            if not isinstance(output, dict):
                return output
            try:
                var_data = output[var_name]
            except KeyError:
                raise "Didn't get expected variable"
            
            if order and not default_order:
                raise "If you want to enable ordering you need " \
                      "to provide a default_order" 
            
            row_count = 0
            if isinstance(var_data, SelectResults):
                row_count = var_data.count()
                if default_order:
                    split = order.split('.')
                    if len(split) > 1:
                        cls = var_data.sourceClass
                        for i in split:
                            col_meta = cls.sqlmeta.columns.get(i + 'ID', None)
                            if not col_meta:
                                col = getattr(cls.q, i)
                                break
                            cls = classregistry.findClass(col_meta.foreignKey)
                    else:
                        col = getattr(var_data.sourceClass.q, order, None)
                    
                    if col:
                        var_data = var_data.orderBy(col)
                    else:
                        raise "The order column (%s) doesn't exist" % order
                    if reversed:
                        var_data = var_data.reversed()
            elif isinstance(var_data, list):
                row_count = len(var_data)
            else:
                raise 'Variable is not a list or SelectResults'

            offset = (page-1) * limit_
            page_count = int(ceil(float(row_count)/limit_))

            # if it's possible display every page
            if page_count <= max_pages:
                pages_to_show = range(1,page_count+1)
            else:
                pages_to_show = _select_pages_to_show(page_count=page_count,
                                              current_page=page,
                                              max_pages=max_pages)
                
            # which one should we use? cherrypy.request.input_values or kw?
            #input_values = cherrypy.request.input_values.copy()
            input_values = kw.copy()
            input_values.pop('self', None)
            
            # we add the parameters from other paginators
            for k,v in cherrypy.request.params.iteritems():
                if k.startswith('tg_paginate_') and \
                not k.startswith('tg_paginate_%s_' % var_name):
                    input_values[k] = v
            
            paginate = Paginate(var_name=var_name, current_page=page,
                                limit=limit_, pages=pages_to_show, 
                                page_count=page_count, order=order,
                                input_values=input_values, reversed=reversed)
            
            # set header info
            headers = cherrypy.response.headers
            headers['tg_paginate_%s_current_page' % var_name] = page
            headers['tg_paginate_%s_page_count' % var_name] = page_count
            headers['tg_paginate_%s_order' % var_name] = order
            headers['tg_paginate_%s_reversed' % var_name] = \
                reversed and 1 or 0
            headers['tg_paginate_%s_nav_links' % var_name] = \
                ','.join(map(str, pages_to_show))
            
            if not getattr(cherrypy.request, 'paginate', False):
                cherrypy.request.paginate = dict()
            cherrypy.request.paginate[var_name] = paginate
            
            # we replace the var with the sliced one
            endpoint = offset + limit_
            log.debug("slicing data between %d and %d", offset, endpoint)
            output[var_name] = var_data[offset:endpoint]
            
            # the .var_name attribute is used by PaginateDataGrid to know 
            # which list it's paginating (needed for multiple paginators)
            if isinstance(var_data, list):
                output[var_name] = ListWrapper(output[var_name], var_name)
            else:
                output[var_name].var_name = var_name
            
            return output
        return decorated
    return weak_signature_decorator(entangle)

def _paginate_var_provider(d): 
    # replaced cherrypy.thread_data for cherrypy.request
    # thanks alberto!
    paginate = getattr(cherrypy.request, 'paginate', None)
    if paginate:
        d.update(dict(paginate=paginate))
variable_providers.append(_paginate_var_provider)

class ListWrapper(list):
    def __init__(self, list, var_name):
        super(ListWrapper, self).__init__(list)
        self.var_name = var_name

class Paginate:
    """class for variable provider"""
    def __init__(self, var_name, current_page, pages, page_count, input_values, 
                 limit, order, reversed):
        self.var_name = var_name
        self.pages = pages
        self.limit = limit
        self.page_count = page_count
        self.current_page = current_page
        self.input_values = input_values
        self.order = order
        self.reversed = reversed
        
        if current_page < page_count:
            self.href_next = self.get_href(current_page+1)
            self.href_last = self.get_href(page_count)
        else:
            self.href_next = None
            self.href_last = None
            
        if current_page > 1:
            self.href_prev = self.get_href(current_page-1)
            self.href_first = self.get_href(1)
        else:
            self.href_prev = None
            self.href_first = None
    
    def get_href(self, page, order=None, reverse_order=None):
        if order:
            if order == self.order:
                if self.reversed:
                    reversed = None
                else:
                    reversed = True
            else:
                reversed = None
                if reverse_order:
                    if reversed:
                        reversed = None
                    else:
                        reversed = True
        else:
            order = self.order
            reversed = self.reversed
        
        input_values = self.input_values.copy()
        tg_paginate_no = 'tg_paginate_%s_no' % self.var_name
        tg_paginate_order = 'tg_paginate_%s_order' % self.var_name
        tg_paginate_reversed = 'tg_paginate_%s_reversed' % self.var_name
        
        input_values.update({tg_paginate_no:page, 
                             tg_paginate_order:order,
                             tg_paginate_reversed:reversed})
        
        # we need to clear None and False values so navigation urls
        # are generated correctly. Otherwise we end up with 
        # urls like ?checkbox_value=False which ends up as u'False' which
        # evaluates as True on a simple 'if checkbox_value:'
        for k,v in input_values.iteritems():
            if v is None or v is False:
                input_values[k] = ''
        
        return turbogears.url('', input_values)


def _select_pages_to_show(current_page, page_count, max_pages):
    pages_to_show = []
    
    if max_pages < 3:
        raise "The minimun value for max_pages on this algorithm is 3"

    if page_count <= max_pages:
        pages_to_show = range(1,page_count+1)
    
    pad = 0
    if not max_pages % 2:
        pad = 1
        
    start = current_page - (max_pages / 2) + pad
    end = current_page + (max_pages / 2)
    
    if start < 1:
        end = end + (start * -1) + 1
        start = 1

    if end > page_count:
        start = start - (end - page_count)
        end = page_count
        
    return range(start, end+1)
