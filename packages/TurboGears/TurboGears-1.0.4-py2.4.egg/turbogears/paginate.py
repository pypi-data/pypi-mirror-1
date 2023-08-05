import re
import types
from math import ceil
import logging
import warnings

import cherrypy
try:
    import sqlobject
    from sqlobject.main import SelectResults
except ImportError:
    SelectResults = None
    sqlobject = None

try:
    # Can't depend on sqlalchemy being available.
    import sqlalchemy
    from sqlalchemy.ext.selectresults import SelectResults as SASelectResults
    from sqlalchemy.orm.query import Query
    # sqlalchemy 0.4.x turned SelectResults into a function that returns a Query
    if isinstance(SASelectResults, types.FunctionType):
        SASelectResults = None
except ImportError:
    SASelectResults = None
    sqlalchemy = None
    Query = None

import turbogears
from turbogears.controllers import redirect
from turbogears.decorator import weak_signature_decorator
from turbogears.view import variable_providers
from formencode.variabledecode import variable_encode, variable_decode

log = logging.getLogger("turbogears.paginate")

# lists of databases that lack support for OFFSET
# this will need to be updated periodically as modules change
_so_no_offset = 'mssql maxdb sybase'.split()
_sa_no_offset = 'mssql maxdb access'.split()

# this is a global that is set the first time paginate() is called
_simulate_offset = None

def paginate(var_name, default_order='', default_reversed=None, limit=10,
            allow_limit_override=False, max_pages=5, dynamic_limit=None):
    '''
    @param var_name: the variable name that the paginate decorator will try
    to control. This key must be present in the dictionnary returned from
    your controller in order for the paginate decorator to be able to handle
    it.
    @type var_name: string

    @param default_order: Needs work! XXX
    @type default_order: string or a list of strings. Any string starting with
    "-" (dash) indicates a reverse order for that field/column.

    @param default_reversed: Needs work! XXX
    @type default_reversed: Boolean [Deprecated]

    @param limit: the hard coded limit that the paginate decorator will
    impose on the number of "var_name" to display at the same time.
    This value can be overridden by the use of the dynamic_limit keyword
    argument
    @type limit: integer

    @param allow_limit_override: A boolean that indicates if the parameters
    passed in the calling URL can modify the imposed limit. By default it is
    set to False. If you want to be able to control the limit by using an
    URL parameter then you need to set this to True.
    @type allow_limit_override: Boolean

    @param max_pages: Needs work! XXX
    @type max_pages: integer

    @param dynamic_limit: If specified, this parameter must be the name
    of a key present in the dictionnary returned by your decorated
    controller. The value found for this key will be used as the limit
    for our pagination and will override the other settings, the hard-coded
    one declared in the decorator itself AND the URL parameter one.
    This enables the programmer to store a limit settings inside the
    application preferences and then let the user manage it.
    @type dynamic_limit: string
    '''
    def entangle(func):
        def decorated(func, *args, **kw):
            def kwpop(default, *names):
                for name in names:
                    if kw.has_key(name):
                        return kw.pop(name)
                return default

            if default_reversed is not None:
                warnings.warn(
                    "default_reversed is deprecated. Use default_order='-field'"
                    " to indicate default reversed order or"
                    " default_order=['field1', '-field2, 'field3']"
                    " for multiple fields", DeprecationWarning, 2)

            get = turbogears.config.get

            page = kwpop(1, var_name + '_tgp_no', 'tg_paginate_no')
            if page == 'last':
                page = None
            else:
                page = int(page)
                if page < 1:
                    page = 1
                    if get('paginate.redirect_on_out_of_range'):
                        cherrypy.request.params[var_name + '_tgp_no'] = page
                        redirect(cherrypy.request.path, cherrypy.request.params)

            limit_ = int(
                kwpop(limit, var_name + '_tgp_limit', 'tg_paginate_limit'))
            order = kwpop(None, var_name + '_tgp_order', 'tg_paginate_order')
            ordering = kwpop(
                {},
                var_name + '_tgp_ordering',
                'tg_paginate_ordering')

            # Convert ordering str to a dict.
            if ordering:
                ordering = convert_ordering(ordering)

            if not allow_limit_override:
                limit_ = limit

            log.debug("Pagination params: page=%s, limit=%s, order=%s "
                      "", page, limit_, order)

            # get the output from the decorated function
            output = func(*args, **kw)
            if not isinstance(output, dict):
                return output
            try:
                var_data = output[var_name]
            except KeyError:
                raise StandardError("Didn't get expected variable")

            if dynamic_limit:
                try:
                    dyn_limit = output[dynamic_limit]
                except KeyError:
                    msg = "dynamic_limit: %s not found in output dict" % (
                            dynamic_limit)
                    raise StandardError(msg)

                limit_ = dyn_limit

            if order and not default_order:
                msg = "If you want to enable ordering you need "
                msg += "to provide a default_order"
                raise StandardError(msg)

            elif default_order and not ordering:
                if isinstance(default_order, basestring):
                    # adapt old style to new style
                    df = [(default_reversed and "-" or "") + default_order]
                elif default_reversed:
                    raise StandardError("default_reversed (deprecated) is only "
                        " allowed when default_order is basestring type")
                else:
                    df = default_order

                ordering = dict([(v.lstrip('-'), [k, not v.startswith('-')])
                                 for k,v in enumerate(df)])
            elif ordering and order:
                sort_ordering(ordering, order)
            log.debug('ordering %s' % ordering)

            row_count = 0
            if (SelectResults and isinstance(var_data, SelectResults)) or \
               (SASelectResults and isinstance(var_data, SASelectResults)) or \
               (Query and isinstance(var_data, Query)):
                row_count = var_data.count() or 0
                if ordering:
                    # Build order_by list.
                    order_cols = range(len(ordering))
                    for (colname, order_opts) in ordering.items():
                        col = sql_get_column(colname, var_data)
                        if not col:
                            msg = "The order column (%s) doesn't exist" % colname
                            raise StandardError(msg)

                        order_by_expr = sql_order_col(col, order_opts[1])
                        order_cols[order_opts[0]] = order_by_expr
                    # May need to address potential of ordering already
                    # existing in var_data.
                    # SO and SA differ on this method name.
                    if hasattr(var_data, 'orderBy'):
                        var_data = var_data.orderBy(order_cols)
                    else:
                        var_data = var_data.order_by(order_cols)

            elif isinstance(var_data, list) or (sqlalchemy and isinstance(
                    var_data, sqlalchemy.orm.attributes.InstrumentedList)):
                row_count = len(var_data)

            else:
                raise StandardError(
                    'Variable is not a list or SelectResults or Query (%s)' % type(
                            var_data))

            # If limit is zero then return all our rows
            if not limit_:
                limit_ = row_count or 1

            page_count = int(ceil(float(row_count)/limit_))

            if page > page_count:
                page = max(page_count, 1)
                if get('paginate.redirect_on_out_of_range'):
                    cherrypy.request.params[var_name + '_tgp_no'] = page
                    redirect(cherrypy.request.path, cherrypy.request.params)

            if page is None:
                page = max(page_count, 1)
                if get('paginate.redirect_on_last_page'):
                    cherrypy.request.params[var_name + '_tgp_no'] = page
                    redirect(cherrypy.request.path, cherrypy.request.params)

            offset = (page-1) * limit_

            # if it's possible display every page
            if page_count <= max_pages:
                pages_to_show = range(1,page_count+1)
            else:
                pages_to_show = _select_pages_to_show(page_count=page_count,
                                              current_page=page,
                                              max_pages=max_pages)

            # which one should we use? cherrypy.request.input_values or kw?
            #input_values = cherrypy.request.input_values.copy()
            ##input_values = kw.copy()
            input_values =  variable_encode(cherrypy.request.params.copy())
            input_values.pop('self', None)
            for input_key in input_values.keys():
                if input_key.startswith(var_name + '_tgp_') or \
                    input_key.startswith('tg_paginate'):
                    del input_values[input_key]

            paginate_instance = Paginate(
                current_page=page,
                limit=limit_,
                pages=pages_to_show,
                page_count=page_count,
                input_values=input_values,
                order=order,
                ordering=ordering,
                row_count=row_count,
                var_name=var_name)

            cherrypy.request.paginate = paginate_instance
            if not hasattr(cherrypy.request, 'paginates'):
                cherrypy.request.paginates = dict()
            cherrypy.request.paginates[var_name] = paginate_instance

            # we replace the var with the sliced one
            endpoint = offset + limit_
            log.debug("slicing data between %d and %d", offset, endpoint)

            global _simulate_offset
            if _simulate_offset is None:
                _simulate_offset = get('paginate.simulate_offset', None)
                if _simulate_offset is None:
                    _simulate_offset = False
                    so_db = get('sqlobject.dburi', 'NOMATCH:').split(':', 1)[0]
                    sa_db = get('sqlalchemy.dburi', 'NOMATCH:').split(':', 1)[0]
                    if so_db in _so_no_offset or sa_db in _sa_no_offset:
                        _simulate_offset = True
                        log.warning("simulating OFFSET, paginate may be slow")
                        log.warning("to turn off, set "
                                     "paginate.simulate_offset=False")

            if _simulate_offset:
                var_data_iter = iter(var_data[:endpoint])
                # skip over the number of records specified by offset
                for i in range(offset):
                    var_data_iter.next()
                # return the records that remain
                output[var_name] = list(var_data_iter)
            else:
                output[var_name] = var_data[offset:endpoint]

            return output
        return decorated
    return weak_signature_decorator(entangle)

def _paginate_var_provider(d):
    # replaced cherrypy.thread_data for cherrypy.request
    # thanks alberto!
    paginate = getattr(cherrypy.request, 'paginate', None)
    if paginate:
        d.update(dict(paginate=paginate))
    paginates = getattr(cherrypy.request, 'paginates', None)
    if paginates:
        d.update(dict(paginates=paginates))
variable_providers.append(_paginate_var_provider)

class Paginate:
    """class for variable provider"""
    def __init__(self, current_page, pages, page_count, input_values,
                 limit, order, ordering, row_count, var_name):

        self.var_name = var_name
        self.pages = pages
        self.limit = limit
        self.page_count = page_count
        self.current_page = current_page
        self.input_values = input_values
        self.order = order
        self.ordering = ordering
        self.row_count = row_count
        self.first_item = page_count and ((current_page - 1) * limit + 1) or 0
        self.last_item = min(current_page * limit, row_count)
        self.reversed = False

        # Should reversed be true?
        for (field_name, ordering_values) in ordering.items():
            if ordering_values[0] == 0 and not ordering_values[1]:
                self.reversed = True

        # If ordering is empty, don't add it.
        input_values = {var_name + '_tgp_limit': limit}
        if ordering:
            input_values[var_name + '_tgp_ordering'] = ordering
        self.input_values.update(input_values)

        if current_page < page_count:
            self.input_values.update({
                var_name + '_tgp_no': current_page + 1,
                var_name + '_tgp_limit': limit
            })
            self.href_next = turbogears.url(
                cherrypy.request.path,
                self.input_values)
            self.input_values.update({
                var_name + '_tgp_no': 'last',
                var_name + '_tgp_limit': limit
            })
            self.href_last = turbogears.url(
                cherrypy.request.path,
                self.input_values)
        else:
            self.href_next = None
            self.href_last = None

        if current_page > 1:
            self.input_values.update({
                var_name + '_tgp_no': current_page - 1,
                var_name + '_tgp_limit': limit
            })
            self.href_prev = turbogears.url(
                cherrypy.request.path,
                self.input_values)
            self.input_values.update({
                var_name + '_tgp_no': 1,
                var_name + '_tgp_limit': limit
            })
            self.href_first = turbogears.url(
                cherrypy.request.path,
                self.input_values)
        else:
            self.href_prev = None
            self.href_first = None

    def get_href(self, page, order=None, reverse_order=None):
        # Note that reverse_order is not used.  It should be cleaned up here
        # and in the template.  I'm not removing it now because I don't want
        # to break the API.
        order = order or None
        input_values = self.input_values.copy()
        input_values[self.var_name + '_tgp_no'] = page
        if order:
            input_values[ self.var_name + '_tgp_order'] = order

        return turbogears.url('', input_values)

def _select_pages_to_show(current_page, page_count, max_pages):
    pages_to_show = []

    if max_pages < 3:
        msg = "The minimun value for max_pages on this algorithm is 3"
        raise StandardError(msg)

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

def sort_ordering(ordering, sort_name):
    """Rearrange ordering based on sort_name."""
    log.debug('sort called with %s and %s' % (ordering, sort_name))
    if ordering.setdefault(sort_name, [-1, True])[0] == 0:
        # Flip
        ordering[sort_name][1] = not ordering[sort_name][1]
    else:
        ordering[sort_name][0] = -1

    # re-sort dictionary
    items = ordering.items()
    items.sort(lambda x,y: cmp(x[1],y[1]))
    for i,v in enumerate(items):
        ordering[v[0]][0] = i

    log.debug('sort results is %s and %s' % (ordering, sort_name))

def sql_get_column(colname, var_data):
    """Return a column from var_data based on colname."""
    if SelectResults and isinstance(var_data, SelectResults):
        col = getattr(var_data.sourceClass.q, colname, None)

    elif SASelectResults and isinstance(var_data, SASelectResults):
        col = getattr(
                var_data._query.mapper.c,
                colname[len(var_data._query.mapper.column_prefix or ''):],
                None)

    elif Query and isinstance(var_data, Query):
        col = getattr(
                var_data.mapper.c,
                colname[len(var_data.mapper.column_prefix or ''):],
                None)
        #if no attribute is found, let's try searching for 'foreign' objects...
        # eg.: address.user.occupation.name
        if not col and colname.find('.'):
            seq = colname.split('.')
            mapper = var_data.mapper
            for propname in seq[:-1]:
                prop = mapper.get_property(
                    propname, resolve_synonyms=True, raiseerr=False)
                if not prop:
                    break
                mapper = prop.mapper
            # last item from split should be a simple attribute
            col = getattr(
                    mapper.c,
                    seq[-1][len(mapper.column_prefix or ''):],
                    None)
    else:
        raise StandardError, 'expected SelectResults'

    return col

def sql_order_col(col, ascending=True):
    """Return an ordered col for col."""
    if sqlalchemy and isinstance(col, sqlalchemy.sql.ColumnElement):
        if ascending:
            order_col = sqlalchemy.sql.asc(col)
        else:
            order_col = sqlalchemy.sql.desc(col)
    elif sqlobject and isinstance(col, types.InstanceType):
        # I don't like using InstanceType, but that's what sqlobject col type
        # is.
        if ascending:
            order_col = col
        else:
            order_col = sqlobject.DESC(col)
    else:
        raise StandardError, 'expected Column, but got %s' % str(type(col))
    return order_col

# Ordering re:
ordering_expr = re.compile(r"('\w+(\.\w+)*'): ?\[(\d+), ?(True|False)\]")

def convert_ordering(ordering):
    """Covert ordering unicode string to dict."""

    log.debug('ordering received %s' % str(ordering))

    # eval would be simple, but insecure.
    if not isinstance(ordering, (str, unicode)):
        raise ValueError, "ordering should be string or unicode."
    new_ordering = {}
    if ordering == u"{}":
        pass
    else:
        try:
            ordering_info_find = ordering_expr.findall(ordering)
            emsg = "Didn't match ordering for %s." % str(ordering)
            assert len(ordering_info_find) > 0, emsg
            for ordering_info in ordering_info_find:
                ordering_key = str(ordering_info[0]).strip("'")
                ordering_order = int(ordering_info[2])
                ordering_reverse = bool(ordering_info[3] == 'True')
                new_ordering[ordering_key] = [ordering_order,
                                              ordering_reverse]
        except StandardError, e:
            log.debug('FAILED to convert ordering.')
            new_ordering = {}
    log.debug('ordering converted to %s' % str(new_ordering))
    return new_ordering
