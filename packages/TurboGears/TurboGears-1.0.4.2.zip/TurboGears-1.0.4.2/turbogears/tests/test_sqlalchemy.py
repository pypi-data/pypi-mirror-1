"Tests for SQLAlchemy support"

import cherrypy, os, threading, turbogears

from sqlalchemy import *
from sqlalchemy.ext.activemapper import ActiveMapper, column, one_to_many

from turbogears import config, redirect, expose, database, errorhandling
from turbogears.testutil import create_request, capture_log, print_log, \
                                sqlalchemy_cleanup
from turbogears.database import get_engine, metadata, session, mapper
from turbogears.controllers import RootController

config.update({"sqlalchemy.dburi" : "sqlite:///:memory:"})

get_engine()

metadata.bind.echo = True

users_table = Table("users", metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", String(40)),
    Column("password", String(10))
    )

class User(object):
    def __repr__(self):
        return "(User %s, password %s)" % (self.user_name, self.password)

usermapper = mapper(User, users_table)

class Person(ActiveMapper):
    class mapping:
        id = column(Integer, primary_key=True)
        name = column(String(40))
        addresses = one_to_many("Address")

class Address(ActiveMapper):
    class mapping:
        id = column(Integer, primary_key=True)
        address = column(String(40))
        city = column(String(40))
        person_id = column(Integer, foreign_key=ForeignKey("person.id"))

def setup_module():
    metadata.create_all()

def teardown_module():
    metadata.drop_all()
    sqlalchemy_cleanup()

def test_query_in_session():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    query = session.query(User)
    globbo = query.filter_by(user_name="globbo").one()
    assert globbo.password == "thegreat!"
    users_table.delete().execute()

def test_create_and_query():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    s = users_table.select()
    r = s.execute()
    assert len(r.fetchall()) == 1
    users_table.delete().execute()

def test_active_mapper():
    p = Person(name="Ford Prefect")
    a = Address(address="1 West Guildford", city="Betelgeuse")
    p.addresses.append(a)
    session.flush()
    session.clear()
    q = session.query(Person)
    ford = q.filter_by(name="Ford Prefect").one()
    assert ford is not p
    assert len(ford.addresses) == 1

class MyRoot(RootController):
    def no_error(self, name):
        p = Person(name=name)
        raise redirect("/confirm")
    no_error = expose()(no_error)

    def e_handler(self, tg_exceptions=None):
        cherrypy.response.code = 501
        return "An exception ocurred: %r (%s)" % ((tg_exceptions,)*2)

    def create_person(self, id, docom=0, doerr=0):
        p = Person(id=id)
        if int(docom):
            cherrypy.request.sa_transaction.commit()
        if int(doerr) == 1:
            raise Exception('User generated exception')
        if int(doerr) == 2:
            raise turbogears.redirect('/')
        return "No exceptions ocurred"
    create_person = expose()(create_person)
    create_person = errorhandling.exception_handler(e_handler)(create_person)

def test_implicit_trans_no_error():
    capture_log("turbogears.database")
    cherrypy.root = MyRoot()
    create_request("/no_error?name=A.%20Dent")
    print_log()
    session.clear()
    q = session.query(Person)
    arthur = q.filter_by(name="A. Dent").one()

def test_raise_sa_exception():
    capture_log("turbogears.database")
    cherrypy.root = MyRoot()
    create_request("/create_person?id=20")
    output = cherrypy.response.body[0]
    print output
    assert "No exceptions" in output

    create_request("/create_person?id=20")
    output = cherrypy.response.body[0]
    print output

    # Note that the specific DB2API may be either OperationalError or
    # IntegrityError depending on what version of sqlite and pysqlite
    # is used.
    # SA 0.3 uses SQLError; 0.4 DBAPIError
    assert "SQLError" in output or "DBAPIError" in output

# Check that if a controller raises an exception, transactions are rolled back
def test_user_exception():
    cherrypy.root = MyRoot()
    create_request("/create_person?id=21&doerr=1")
    session.clear() # should be done automatically, but just in case
    assert Person.query().get(21) is None

# Check that if a controller redirects, transactions are committed
def test_user_redirect():
    cherrypy.root = MyRoot()
    create_request("/create_person?id=22&doerr=2")
    session.clear() # should be done automatically, but just in case
    assert Person.query().get(22) is not None

# Check it's safe to commit a transaction in the controller
def test_cntrl_commit():
    cherrypy.root = MyRoot()
    create_request("/create_person?id=23&docom=1")
    assert 'InvalidRequestError: This transaction is inactive' not in cherrypy.response.body[0]

# Check an exception within a tg.exception_handler causes a rollback
class RbRoot(RootController):
    def handerr(self, id):
        Person(id=int(id)+1)
        return dict()
    def doerr(self, id, dorb=0):
        Person(id=id)
        if int(dorb):
            cherrypy.request.sa_transaction.rollback()
        raise Exception('test')
    doerr = errorhandling.exception_handler(handerr)(doerr)
    doerr = expose()(doerr)

def test_exc_rollback():
    cherrypy.root = RbRoot()
    create_request('/doerr?id=24')
    print cherrypy.response.body[0]
    assert Person.query().get(24) is None
    assert Person.query().get(25) is not None

# Check that if controller method manually rollbacks, error handler doesn't cause problems
def test_exc_done_rollback():
    cherrypy.root = RbRoot()
    create_request('/doerr?id=26&dorb=1')
    print cherrypy.response.body[0]
    assert cherrypy.response.body[0] == '{"tg_flash": null}'

#--
# Check for session freshness, ticket #1419
# It checks that changes made to the data in thread B are reflected in thread A.
#--
fresh_md = MetaData()
test_table = Table("test", fresh_md,
    Column("id", Integer, primary_key=True),
    Column("val", String(40))
    )
class Test(object):
    pass
mapper(Test, test_table)

class FreshRoot(RootController):
    def test1(self):
        assert session.query(Test).get(1).val == 'a'
        return dict()
    test1 = expose()(test1)
    def test2(self):
        session.query(Test).get(1).val = 'b'
        return dict()
    test2 = expose()(test2)
    def test3(self):
        assert session.query(Test).get(1).val == 'b'
        return dict()
    test3 = expose()(test3)

def test_session_freshness():
    if os.path.exists('freshtest.db'):
        os.unlink('freshtest.db')
    fresh_md.bind = 'sqlite:///freshtest.db' # :memory: can't be used in multiple threads
    test_table.create()
    fresh_md.bind.execute(test_table.insert(), dict(id=1, val='a'))

    cherrypy.root = FreshRoot()

    create_request("/test1")
    print cherrypy.response.body[0]
    assert 'AssertionError' not in cherrypy.response.body[0]

    # Call test2 in a different thread
    class ThreadB(threading.Thread):
        def run(self):
            create_request("/test2")
            print cherrypy.response.body[0]
            assert 'AssertionError' not in cherrypy.response.body[0]
    thrdb = ThreadB()
    thrdb.start()
    thrdb.join()

    create_request("/test3")
    print cherrypy.response.body[0]
    assert 'AssertionError' not in cherrypy.response.body[0]
