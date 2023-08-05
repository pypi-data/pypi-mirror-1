"Tests for paginate"

import unittest
from urllib import quote
import warnings

from turbogears import config, expose, database
from turbogears.controllers import RootController, url
from turbogears.database import get_engine, metadata, session, mapper
from turbogears.paginate import paginate, sort_ordering
from turbogears.testutil import create_request, sqlalchemy_cleanup
from turbojson.jsonify import jsonify

import cherrypy
from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relation
from sqlalchemy.ext.selectresults import SelectResults as SASelectResults
from sqlobject import SQLObject, IntCol, StringCol, connectionForURI


config.update({"tg.strict_parameters": True,
               "sqlalchemy.dburi": "sqlite:///:memory:"})

# sqlalchemy setup
sqlalchemy_cleanup()
get_engine()

# sqlobject setup
database.set_db_uri("sqlite:///:memory:")
__connection__ = hub = database.PackageHub('test_paginate')


def test_sort_ordering():
    """Test ticket #1508"""
    d = dict()
    sort_ordering(d, 'a')
    assert d == {'a': [0, True]}
    sort_ordering(d, 'a')  # descending order
    assert d == {'a': [0, False]}
    sort_ordering(d, 'b')
    assert d == {'b': [0, True], 'a': [1, False]}
    sort_ordering(d, 'c')
    assert d == {'c': [0, True], 'b': [1, True], 'a': [2, False]}
    sort_ordering(d, 'c') # descending order
    assert d == {'c': [0, False], 'b': [1, True], 'a': [2, False]}
    sort_ordering(d, 'a') # 'a' again.. still in descending order
    assert d == {'a': [0, False], 'c': [1, False], 'b': [2, True]}
    sort_ordering(d, 'a') # 'a' again.. now in ascending order
    assert d == {'a': [0, True], 'c': [1, False], 'b': [2, True]}
    sort_ordering(d, 'd')
    assert d == {'d': [0, True], 'a': [1, True], 'c': [2, False], 'b': [3, True]}
    sort_ordering(d, 'a')
    assert d == {'a': [0, True], 'd': [1, True], 'c': [2, False], 'b': [3, True]}


class Spy(object):
    """Helper class to test paginate's instances in cherrypy.request.

    We could use a special template to output paginate's attributes, but
    testing values/types before they are rendered (when possible) is much
    easier.
    """

    def __init__(self, name=None, **expectations):
        self.name = name
        self.expectations = expectations

    def __str__(self):
        if self.name:
            paginate = cherrypy.request.paginates[self.name]
        else:
            paginate = cherrypy.request.paginate
            assert paginate in cherrypy.request.paginates.values()

        for k,v in self.expectations.iteritems():
            if not hasattr(paginate, k):
                return "fail: paginate does not have '%s' attribute" % k
            if getattr(paginate, k) != v:
                return "fail: expected %s=%r, got %s=%r" % \
                    (k, v, k, getattr(paginate, k))

        return "ok: [paginate %s ]" % \
            " , ".join(["%s=%r" % (k,v) for k,v in paginate.__dict__.items()])

    def assert_ok(body, key, value, raw=False):
        assert "ok: [paginate" in body
        if raw:
            expr = "%s=%s " % (key, value)
        else:
            expr = "%s=%r " % (key, value)
        if expr not in body:
            print body
        assert expr in body, "expected %s" % expr
    assert_ok = staticmethod(assert_ok)


def jsonify_spy(obj):
    result = str(obj)
    return result
jsonify_spy = jsonify.when('isinstance(obj, Spy)')(jsonify_spy)


class TestSpy(unittest.TestCase):
    """Never trust a spy"""

    class MyRoot(RootController):
        def spy(self):
            data = range(100)
            spy = Spy()
            return dict(data=data, spy=spy)
        spy = paginate("data")(spy)
        spy = expose()(spy)

        def spy_correct_expectation(self):
            data = range(100)
            spy = Spy(page_count=10)
            return dict(data=data, spy=spy)
        spy_correct_expectation = paginate("data")(spy_correct_expectation)
        spy_correct_expectation = expose()(spy_correct_expectation)

        def spy_wrong_expectation(self):
            data = range(100)
            spy = Spy(page_count=9)
            return dict(data=data, spy=spy)
        spy_wrong_expectation = paginate("data")(spy_wrong_expectation)
        spy_wrong_expectation = expose()(spy_wrong_expectation)

        def spy_invalid_expectation(self):
            data = range(100)
            spy = Spy(foobar=10)
            return dict(data=data, spy=spy)
        spy_invalid_expectation = paginate("data")(spy_invalid_expectation)
        spy_invalid_expectation = expose()(spy_invalid_expectation)


    def setUp(self):
        cherrypy.root = self.MyRoot()

    def test_spy(self):
        create_request('/spy')
        body = cherrypy.response.body[0]
        Spy.assert_ok(body, 'current_page', 1)

        try:
            Spy.assert_ok(body, 'current_page', 2)
            raise Exception("above test should have failed")
        except AssertionError:
            pass

    def test_correct_expectation(self):
        create_request('/spy_correct_expectation')
        body = cherrypy.response.body[0]
        assert "ok: [paginate" in body

    def test_wrong_expectation(self):
        create_request('/spy_wrong_expectation')
        body = cherrypy.response.body[0]
        assert "fail: expected page_count=9, got page_count=10" in body

    def test_invalid_expectation(self):
        create_request('/spy_invalid_expectation')
        body = cherrypy.response.body[0]
        assert "fail: paginate does not have 'foobar' attribute" in body

    def test_raw_expectation(self):
        create_request('/spy_correct_expectation')
        Spy.assert_ok(cherrypy.response.body[0], 'var_name', 'data')
        Spy.assert_ok(cherrypy.response.body[0], 'var_name', "'data'", raw=True)




class TestPagination(unittest.TestCase):
    """Base class for all Paginate TestCases"""
    def request(self, url):
        create_request(url)
        self.body = cherrypy.response.body[0]
        if "fail: " in self.body:
            print self.body
            assert False, "Spy alert! Check body output for details..."




class TestBasicPagination(TestPagination):

    class MyRoot(RootController):
        def basic(self):
            spy = Spy(var_name='data', pages=[1,2,3], limit=4, page_count=3,
                      order=None, ordering={}, row_count=10)
            data = range(10)
            return dict(data=data, spy=spy)
        basic = paginate("data", limit=4)(basic)
        basic = expose()(basic)

        def custom_limit(self):
            spy = Spy(var_name='data', order=None, ordering={}, row_count=10)
            data = range(10)
            return dict(data=data, spy=spy)
        custom_limit = paginate("data", limit=4,
            allow_limit_override=True)(custom_limit)
        custom_limit = expose()(custom_limit)

        def default_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering={}, row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)
        default_max_pages = paginate("data")(default_max_pages)
        default_max_pages = expose()(default_max_pages)

        def four_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering={}, row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)
        four_max_pages = paginate("data", max_pages=4)(four_max_pages)
        four_max_pages = expose()(four_max_pages)

        def three_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering={}, row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)
        three_max_pages = paginate("data", max_pages=3)(three_max_pages)
        three_max_pages = expose()(three_max_pages)

        def invalid_dynamic(self):
            data = range(10)
            return dict(data=data)
        invalid_dynamic = paginate("data", limit=4,
            dynamic_limit='foobar')(invalid_dynamic)
        invalid_dynamic = expose()(invalid_dynamic)

        def dynamic(self):
            spy = Spy(var_name='data', pages=[1,2], limit=7, page_count=2,
                      order=None, ordering={}, row_count=10)
            data = range(10)
            return dict(data=data, spy=spy, foobar=7)
        dynamic = paginate("data", limit=4, dynamic_limit='foobar',
            allow_limit_override=True)(dynamic)
        dynamic = expose()(dynamic)

        def multiple(self):
            spy_foo = Spy(name='foo', var_name='foo', pages=[1,2,3,4,5],
                          limit=4, page_count=5, order=None, ordering={},
                          row_count=20)
            spy_bar = Spy(name='bar', var_name='bar', pages=[1,2,3], limit=10,
                          page_count=3, order=None, ordering={}, row_count=26)
            foo = range(20)
            bar = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') # 26 letters

            return dict(foo=foo, bar=bar, spy_foo=spy_foo, spy_bar=spy_bar)
        multiple = paginate("foo", limit=4)(multiple)
        multiple = paginate("bar")(multiple)
        multiple = expose()(multiple)

        def empty(self):
            spy = Spy(var_name='data', pages=[], page_count=0,
                      order=None, ordering={}, row_count=0,
                      current_page=1, first_item=0, last_item=0)
            data = []
            return dict(data=data, spy=spy)
        empty = paginate("data", limit=4, allow_limit_override=True)(empty)
        empty = expose()(empty)
    # end of MyRoot ------------------------------------------------------------


    def setUp(self):
        cherrypy.root = self.MyRoot()

    def test_pagination_old_style(self):
        self.request("/basic")
        assert '"data": [0, 1, 2, 3]' in self.body
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'first_item', 1)
        Spy.assert_ok(self.body, 'last_item', 4)

        self.request("/basic/?tg_paginate_no=1")
        assert '"data": [0, 1, 2, 3]' in self.body
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'first_item', 1)
        Spy.assert_ok(self.body, 'last_item', 4)

        self.request("/basic/?tg_paginate_no=2")
        assert '"data": [4, 5, 6, 7]' in self.body
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'first_item', 5)
        Spy.assert_ok(self.body, 'last_item', 8)

        self.request("/basic/?tg_paginate_no=3")
        assert '"data": [8, 9]' in self.body
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'first_item', 9)
        Spy.assert_ok(self.body, 'last_item', 10)

    def test_pagination_new_style(self):
        self.request("/basic/?data_tgp_no=1")
        assert '"data": [0, 1, 2, 3]' in self.body
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'first_item', 1)
        Spy.assert_ok(self.body, 'last_item', 4)

        self.request("/basic/?data_tgp_no=2")
        assert '"data": [4, 5, 6, 7]' in self.body
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'first_item', 5)
        Spy.assert_ok(self.body, 'last_item', 8)

        self.request("/basic/?data_tgp_no=3")
        assert '"data": [8, 9]' in self.body
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'first_item', 9)
        Spy.assert_ok(self.body, 'last_item', 10)

    def test_limit_override(self):
        # can't override limit (old style)
        self.request('/basic/?tg_paginate_limit=2')
        assert '"data": [0, 1, 2, 3]' in self.body

        # can't override limit (new style)
        self.request("/basic/?data_tgp_limit=2")
        assert '"data": [0, 1, 2, 3]' in self.body

        # can override limit (old style)
        self.request('/custom_limit/?tg_paginate_limit=2')
        assert '"data": [0, 1]' in self.body
        Spy.assert_ok(self.body, 'page_count', 5)
        Spy.assert_ok(self.body, 'limit', 2)
        Spy.assert_ok(self.body, 'pages', [1,2,3,4,5])

        # can override limit (new style)
        self.request("/custom_limit/?data_tgp_limit=2")
        assert '"data": [0, 1]' in self.body
        Spy.assert_ok(self.body, 'page_count', 5)
        Spy.assert_ok(self.body, 'limit', 2)
        Spy.assert_ok(self.body, 'pages', [1,2,3,4,5])

    def test_max_pages(self):
        self.request("/default_max_pages")
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', [1, 2, 3, 4, 5])

        self.request("/default_max_pages/?data_tgp_no=5")
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', [3, 4, 5, 6, 7])

        self.request("/three_max_pages")
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', [1, 2, 3])

        self.request("/three_max_pages/?data_tgp_no=5")
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', [4, 5, 6])

        # even 'max pages'
        self.request("/four_max_pages")
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', [1, 2, 3, 4])

        self.request("/four_max_pages/?data_tgp_no=5")
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', [4, 5, 6, 7])

    def test_invalid_dynamic_limit(self):
        self.request("/invalid_dynamic")
        assert 'StandardError: dynamic_limit: foobar not found in output dict' in self.body

    def test_dynamic_limit(self):
        self.request("/dynamic")
        assert '"data": [0, 1, 2, 3, 4, 5, 6]' in self.body

        self.request('/dynamic/?tg_paginate_limit=2')
        assert '"data": [0, 1, 2, 3, 4, 5, 6]' in self.body

    def test_multiple(self):
        self.request("/multiple")
        assert '"foo": [0, 1, 2, 3]' in self.body
        assert '"bar": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]' in self.body

        self.request("/multiple/?foo_tgp_no=3")
        assert '"foo": [8, 9, 10, 11]' in self.body
        assert '"bar": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]' in self.body

        self.request("/multiple/?bar_tgp_no=2")
        assert '"foo": [0, 1, 2, 3]' in self.body
        assert '"bar": ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]' in self.body

        self.request("/multiple/?foo_tgp_no=2&bar_tgp_no=3")
        assert '"foo": [4, 5, 6, 7]' in self.body
        assert '"bar": ["U", "V", "W", "X", "Y", "Z"]' in self.body

    def test_out_of_bound_pages(self):
        for number in range(-3,1):
            self.request("/basic/?tg_paginate_no=%s" % number)
            assert '"data": [0, 1, 2, 3]' in self.body
            Spy.assert_ok(self.body, 'current_page', 1)
            Spy.assert_ok(self.body, 'first_item', 1)
            Spy.assert_ok(self.body, 'last_item', 4)

        for number in range(4, 7):
            self.request("/basic/?tg_paginate_no=%s" % number)
            assert '"data": [8, 9]' in self.body
            Spy.assert_ok(self.body, 'current_page', 3)
            Spy.assert_ok(self.body, 'first_item', 9)
            Spy.assert_ok(self.body, 'last_item', 10)

    def test_last_page(self):
        self.request("/basic/?tg_paginate_no=last")
        assert '"data": [8, 9]' in self.body
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'first_item', 9)
        Spy.assert_ok(self.body, 'last_item', 10)

    def test_href(self):
        # note: this test requires simplejson 1.5 or newer
        # since old simplejson versions do not escape forward slashes

        self.request("/basic/?data_tgp_no=0") # out of bound
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next', r"'\/basic\/?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last', r"'\/basic\/?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request("/basic/?data_tgp_no=1")
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next', r"'\/basic\/?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last', r"'\/basic\/?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request("/basic/?data_tgp_no=2")
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'href_first', r"'\/basic\/?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev', r"'\/basic\/?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next', r"'\/basic\/?data_tgp_no=3&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last', r"'\/basic\/?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request("/basic/?data_tgp_no=3")
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'href_first', r"'\/basic\/?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev', r"'\/basic\/?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

        self.request("/basic/?data_tgp_no=4") # out of bound !
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'href_first', r"'\/basic\/?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev', r"'\/basic\/?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

        # empty data
        self.request("/empty")
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

    def test_empty_data(self):
        self.request("/empty")
        assert '"data": []' in self.body
        Spy.assert_ok(self.body, 'limit', 4)

    def test_zero_limit(self):
        self.request("/custom_limit/?data_tgp_limit=0")
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'page_count', 1)
        Spy.assert_ok(self.body, 'limit', 10)
        Spy.assert_ok(self.body, 'pages', [1])

    def test_empty_data_zero_limit(self):
        self.request("/empty/?data_tgp_limit=0")
        print self.body
        assert '"data": []' in self.body
        Spy.assert_ok(self.body, 'page_count', 0)
        Spy.assert_ok(self.body, 'limit', 1)




#
# Test SQLAlchemy & SQLObject
#

occupations_table = Table('occupations', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(20)),
)

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(20)),
    Column('occupation_id', Integer, ForeignKey("occupations.id")),
)

addresses_table = Table('addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey("users.id")),
    Column('street', String(50)),
    Column('city', String(40))
)

class Occupation(object): pass

class User(object): pass

class Address(object):
    def __repr__(self):
        # using "[...]" instead of "<...>" avoids rendering "&lt;"
        return "[Address %r]" % self.id

mapper(Occupation, occupations_table)

mapper(User, users_table, properties={
    'occupation' : relation(Occupation, lazy=False),
    'addresses': relation(Address, backref='user', lazy=False)
})

mapper(Address, addresses_table)


class SOAddress(SQLObject):
    id = IntCol(),
    user_id = IntCol()
    street = StringCol()
    city = StringCol()

    def __repr__(self):
        # using "[...]" instead of "<...>" avoids rendering "&lt;"
        return "[Address %r]" % self.id




class TestDatabasePagination(TestPagination):

    class MyRoot(RootController):
        def __common(self, method=None):
            if method == "Q":
                data = session.query(Address)
            elif method == "SR":
                data = SASelectResults(session.query(Address))
            elif method == "SO":
                data = SOAddress.select()
            else:
                raise Exception("Invalid method")

            spy = Spy(var_name='data', pages=[1,2], limit=10, page_count=2,
                      order=None, row_count=16)
            return dict(data=data, spy=spy)

        # default_order = basestring
        basic1 = paginate("data", default_order="id")(__common)
        basic1 = expose("turbogears.tests.paginate")(basic1)

        # default_order = list
        basic2 = paginate("data", default_order=["id"])(__common)
        basic2 = expose("turbogears.tests.paginate")(basic2)

        # default_order = basestring with default_reversed (deprecated)
        warnings.filterwarnings('ignore',
            'default_reversed is deprecated', DeprecationWarning)
        reversed1 = paginate("data", default_order="id", default_reversed=True)(__common)
        reversed1 = expose("turbogears.tests.paginate")(reversed1)

        # default_order = basestring
        reversed2 = paginate("data", default_order="-id")(__common)
        reversed2 = expose("turbogears.tests.paginate")(reversed2)

        # default_order = list with default_reversed (WRONG !!!!)
        wrong_reversed = paginate("data", default_order=["id"], default_reversed=True)(__common)
        wrong_reversed = expose("turbogears.tests.paginate")(wrong_reversed)

        # default_order = list
        reversed3 = paginate("data", default_order=["-id"])(__common)
        reversed3 = expose("turbogears.tests.paginate")(reversed3)

        # +/+
        default_compound_ordering1 = paginate("data", default_order=["city", "street"])(__common)
        default_compound_ordering1 = expose("turbogears.tests.paginate")(default_compound_ordering1)

        # +/-
        default_compound_ordering2 = paginate("data", default_order=["city", "-street"])(__common)
        default_compound_ordering2 = expose("turbogears.tests.paginate")(default_compound_ordering2)

        # -/+
        default_compound_ordering3 = paginate("data", default_order=["-city", "street"])(__common)
        default_compound_ordering3 = expose("turbogears.tests.paginate")(default_compound_ordering3)

        # -/-
        default_compound_ordering4 = paginate("data", default_order=["-city", "-street"])(__common)
        default_compound_ordering4 = expose("turbogears.tests.paginate")(default_compound_ordering4)

        def related(self):
            # only SA Query
            data = session.query(Address).outerjoin(['user', 'occupation'])

            spy = Spy(var_name='data', pages=[1,2], limit=10, page_count=2,
                      order=None, row_count=16)
            return dict(data=data, spy=spy)
        related = paginate("data", default_order="id")(related)
        related = expose("turbogears.tests.paginate")(related)

        def zero_limit(self, method=None):
            if method == "Q":
                data = session.query(Address)
            elif method == "SR":
                data = SASelectResults(session.query(Address))
            elif method == "SO":
                data = SOAddress.select()
            else:
                raise Exception("Invalid method")

            spy = Spy(var_name='data', pages=[1], limit=16, page_count=1,
                      order=None, row_count=16)
            return dict(data=data, spy=spy)

        zero_limit = paginate("data", default_order="id", limit=0)(zero_limit)
        zero_limit = expose("turbogears.tests.paginate")(zero_limit)

        def empty_with_groupby(self):
            data = session.query(Address).filter(Address.c.id<0).group_by(Address.c.user_id)

            spy = Spy(var_name='data', pages=[], limit=10, page_count=0,
                      order=None, row_count=0)
            return dict(data=data, spy=spy)

        empty_with_groupby = paginate("data", default_order="id")(empty_with_groupby)
        empty_with_groupby = expose("turbogears.tests.paginate")(empty_with_groupby)

    # end of MyRoot ------------------------------------------------------------

    def setUp(self):
        cherrypy.root = self.MyRoot()

    def assert_order(self, *args):
        expr = 'data="%s"' % ''.join(['[Address %r]' % x for x in args])
        if expr not in self.body:
            print self.body
        assert expr in self.body, "expected %s" % expr

    def test_basic(self):
        for test in "basic1", "basic2":
            for method in "Q", "SR", "SO":
                self.request("/%s/?method=%s" % (test, method))
                self.assert_order(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', {'id': [0, True]})

                # old style
                self.request("/%s/?method=%s&tg_paginate_no=2" % (test, method))
                self.assert_order(11, 12, 13, 14, 15, 16)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', {'id': [0, True]})

                # new style
                self.request("/%s/?method=%s&data_tgp_no=2" % (test, method))
                self.assert_order(11, 12, 13, 14, 15, 16)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', {'id': [0, True]})

    def test_ordering(self):
        for test in "basic1", "basic2":
            for method in "Q", "SR", "SO":
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'street': [0, True]}))))
                self.assert_order(16, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', {'street': [0, True]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'street': [0, True]}))))
                self.assert_order(11, 12, 13, 14, 15, 1)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', {'street': [0, True]})

    def test_default_reversed(self):
        for test in "reversed1", "reversed2", "reversed3":
            for method in "Q", "SR", "SO":
                self.request("/%s/?method=%s" % (test, method))
                self.assert_order(16, 15, 14, 13, 12, 11, 10, 9, 8, 7)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', {'id': [0, False]})

                self.request("/%s/?method=%s&data_tgp_no=2" % (test, method))
                self.assert_order(6, 5, 4, 3, 2, 1)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', {'id': [0, False]})

    def test_invalid_default_reversed(self):
        for method in "Q", "SR", "SO":
            self.request("/wrong_reversed/?method=%s" % method)
            assert 'StandardError: default_reversed (deprecated) is only  allowed' in self.body

    def test_reverse_ordering(self):
        for test in "basic1", "basic2":
            for method in "Q", "SR", "SO":
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'street': [0, False]}))))
                self.assert_order(1, 15, 14, 13, 12, 11, 10, 9, 8, 7)
                Spy.assert_ok(self.body, 'ordering', {'street': [0, False]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'street': [0, False]}))))
                self.assert_order(6, 5, 4, 3, 2, 16)
                Spy.assert_ok(self.body, 'ordering', {'street': [0, False]})

    def test_compound_ordering(self):
        for test in "basic1", "basic2":
            for method in "Q", "SR", "SO":
                # True/True
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, True], 'street': [1, True]}))))
                self.assert_order(16, 3, 9, 10, 12, 13, 1, 4, 7, 8)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, True]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, True], 'street': [1, True]}))))
                self.assert_order(14, 15, 2, 5, 6, 11)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, True]})

                # True/False
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, True], 'street': [1, False]}))))
                self.assert_order(1, 13, 12, 10, 9, 3, 16, 15, 14, 8)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, False]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, True], 'street': [1, False]}))))
                self.assert_order(7, 4, 11, 6, 5, 2)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, False]})

                # False/True
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, False], 'street': [1, True]}))))
                self.assert_order(2, 5, 6, 11, 4, 7, 8, 14, 15, 16)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, True]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, False], 'street': [1, True]}))))
                self.assert_order(3, 9, 10, 12, 13, 1)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, True]})

                # False/False
                self.request("/%s/?method=%s&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, False], 'street': [1, False]}))))
                self.assert_order(11, 6, 5, 2, 15, 14, 8, 7, 4, 1)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, False]})

                self.request("/%s/?method=%s&tg_paginate_no=2&tg_paginate_ordering=%s" % \
                    (test, method, quote(str({'city': [0, False], 'street': [1, False]}))))
                self.assert_order(13, 12, 10, 9, 3, 16)
                Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, False]})

    def test_default_compound_ordering_1(self):
        # True/True
        for method in "Q", "SR", "SO":
            self.request("/default_compound_ordering1/?method=%s" % method)
            self.assert_order(16, 3, 9, 10, 12, 13, 1, 4, 7, 8)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, True]})

            self.request("/default_compound_ordering1/?method=%s&tg_paginate_no=2" % method)
            self.assert_order(14, 15, 2, 5, 6, 11)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, True]})

    def test_default_compound_ordering_2(self):
        # True/False
        for method in "Q", "SR", "SO":
            self.request("/default_compound_ordering2/?method=%s" % method)
            self.assert_order(1, 13, 12, 10, 9, 3, 16, 15, 14, 8)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, False]})

            self.request("/default_compound_ordering2/?method=%s&tg_paginate_no=2" % method)
            self.assert_order(7, 4, 11, 6, 5, 2)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, True], 'street': [1, False]})

    def test_default_compound_ordering_3(self):
        # False/True
        for method in "Q", "SR", "SO":
            self.request("/default_compound_ordering3/?method=%s" % method)
            self.assert_order(2, 5, 6, 11, 4, 7, 8, 14, 15, 16)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, True]})

            self.request("/default_compound_ordering3/?method=%s&tg_paginate_no=2" % method)
            self.assert_order(3, 9, 10, 12, 13, 1)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, True]})

    def test_default_compound_ordering_4(self):
        # False/False
        for method in "Q", "SR", "SO":
            self.request("/default_compound_ordering4/?method=%s" % method)
            self.assert_order(11, 6, 5, 2, 15, 14, 8, 7, 4, 1)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, False]})

            self.request("/default_compound_ordering4/?method=%s&tg_paginate_no=2" % method)
            self.assert_order(13, 12, 10, 9, 3, 16)
            Spy.assert_ok(self.body, 'ordering', {'city': [0, False], 'street': [1, False]})

    def test_related_objects_ordering_level_1(self):
        # True/True
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, True], 'id': [1, True]})))
        self.assert_order(1, 5, 3, 13, 7, 11, 16, 2, 12, 14)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, True], 'id': [1, True]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, True], 'id': [1, True]})))
        self.assert_order(10, 4, 6, 9, 15, 8)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, True], 'id': [1, True]})

        # True/False
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, True], 'id': [1, False]})))
        self.assert_order(5, 1, 3, 13, 16, 11, 7, 12, 2, 14)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, True], 'id': [1, False]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, True], 'id': [1, False]})))
        self.assert_order(10, 15, 9, 6, 4, 8)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, True], 'id': [1, False]})

        # False/True
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, False], 'id': [1, True]})))
        self.assert_order(8, 4, 6, 9, 15, 10, 14, 2, 12, 7)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, False], 'id': [1, True]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, False], 'id': [1, True]})))
        self.assert_order(11, 16, 13, 3, 1, 5)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, False], 'id': [1, True]})

        # False/False
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, False], 'id': [1, False]})))
        self.assert_order(8, 15, 9, 6, 4, 10, 14, 12, 2, 16)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, False], 'id': [1, False]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.name': [0, False], 'id': [1, False]})))
        self.assert_order(11, 7, 13, 3, 5, 1)
        Spy.assert_ok(self.body, 'ordering', {'user.name': [0, False], 'id': [1, False]})

    def test_related_objects_ordering_level_2(self):
        # True/True
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, True], 'id': [1, True]})))
        self.assert_order(1, 5, 10, 13, 14, 2, 7, 11, 12, 16)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, True], 'id': [1, True]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, True], 'id': [1, True]})))
        self.assert_order(4, 6, 8, 9, 15, 3)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, True], 'id': [1, True]})

        # True/False
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, True], 'id': [1, False]})))
        self.assert_order(14, 13, 10, 5, 1, 16, 12, 11, 7, 2)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, True], 'id': [1, False]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, True], 'id': [1, False]})))
        self.assert_order(15, 9, 8, 6, 4, 3)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, True], 'id': [1, False]})

        # False/True
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, False], 'id': [1, True]})))
        self.assert_order(3, 4, 6, 8, 9, 15, 2, 7, 11, 12)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, False], 'id': [1, True]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, False], 'id': [1, True]})))
        self.assert_order(16, 1, 5, 10, 13, 14)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, False], 'id': [1, True]})

        # False/False
        self.request("/related/?tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, False], 'id': [1, False]})))
        self.assert_order(3, 15, 9, 8, 6, 4, 16, 12, 11, 7)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, False], 'id': [1, False]})

        self.request("/related/?tg_paginate_no=2&tg_paginate_ordering=%s" % \
            quote(str({'user.occupation.name': [0, False], 'id': [1, False]})))
        self.assert_order(2, 14, 13, 10, 5, 1)
        Spy.assert_ok(self.body, 'ordering', {'user.occupation.name': [0, False], 'id': [1, False]})

    def test_zero_limit(self):
        for method in "Q", "SR", "SO":
            self.request("/zero_limit/?method=%s" % method)
            self.assert_order(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

    def test_ticket_1641(self):
        self.request("/empty_with_groupby")
        self.assert_order()


def get_data_dicts():
    occupations = (
        {'id': 1, 'name': 'Doctor'},
        {'id': 2, 'name': 'Actor'},
        {'id': 3, 'name': 'Programmer'})

    users = (
        {'id': 1, 'name': 'Smith', 'occupation_id': 1},
        {'id': 2, 'name': 'John', 'occupation_id': 2},
        {'id': 3, 'name': 'Fred', 'occupation_id': 2},
        {'id': 4, 'name': 'Albert', 'occupation_id': 3},
        {'id': 5, 'name': 'Nicole', 'occupation_id': None},
        {'id': 6, 'name': 'Sarah', 'occupation_id': None},
        {'id': 7, 'name': 'Walter', 'occupation_id': 1},
        {'id': 8, 'name': 'Bush', 'occupation_id': None});

    addresses = (
        {'id': 1, 'user_id': None, 'street': 'street P', 'city': 'city X'},
        {'id': 2, 'user_id': 2, 'street': 'street B', 'city': 'city Z'},
        {'id': 3, 'user_id': 4, 'street': 'street C', 'city': 'city X'},
        {'id': 4, 'user_id': 1, 'street': 'street D', 'city': 'city Y'},
        {'id': 5, 'user_id': None, 'street': 'street E', 'city': 'city Z'},
        {'id': 6, 'user_id': 1, 'street': 'street F', 'city': 'city Z'},
        {'id': 7, 'user_id': 3, 'street': 'street G', 'city': 'city Y'},
        {'id': 8, 'user_id': 7, 'street': 'street H', 'city': 'city Y'},
        {'id': 9, 'user_id': 1, 'street': 'street I', 'city': 'city X'},
        {'id': 10, 'user_id': 6, 'street': 'street J', 'city': 'city X'},
        {'id': 11, 'user_id': 3, 'street': 'street K', 'city': 'city Z'},
        {'id': 12, 'user_id': 2, 'street': 'street L', 'city': 'city X'},
        {'id': 13, 'user_id': 8, 'street': 'street M', 'city': 'city X'},
        {'id': 14, 'user_id': 5, 'street': 'street N', 'city': 'city Y'},
        {'id': 15, 'user_id': 1, 'street': 'street O', 'city': 'city Y'},
        {'id': 16, 'user_id': 3, 'street': 'street A', 'city': 'city X'});

    return occupations, users, addresses


def populate_sqlalchemy_database():
    occupations, users, addresses = get_data_dicts()
    metadata.bind.execute(occupations_table.insert(), occupations)
    metadata.bind.execute(users_table.insert(), users)
    metadata.bind.execute(addresses_table.insert(), addresses)


def populate_sqlobject_database():
    # SQLObject tests will need only "addresses"
    occupations, users, addresses = get_data_dicts()
    for kw in addresses:
        print SOAddress(**kw)


def setup_module():
    metadata.create_all()
    populate_sqlalchemy_database()

    SOAddress.createTable()
    populate_sqlobject_database()
    hub.commit()


def teardown_module():
    metadata.drop_all()
    sqlalchemy_cleanup()
    pass
