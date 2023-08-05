import unittest
from turbogears import testutil
import turbogears
import cherrypy
import time

def cookie_header(morsel):
    """Returns a dict containing cookie information to pass to a server."""
    return {'Cookie': morsel.output(header="")[1:]}


class VisitRoot(turbogears.controllers.RootController):

    def index(self):
        return dict()
    index = turbogears.expose()(index)


class TestVisit(unittest.TestCase):

    def setUp(self):
        self._visit_on = turbogears.config.get('visit.on', False)
        turbogears.config.update({'visit.on': True})
        self._visit_timeout = turbogears.config.get('visit.timeout', 20)
        turbogears.config.update({'visit.timeout': 60})
        self.cookie_name = turbogears.config.get("visit.cookie.name", 'tg-visit')
        cherrypy.root = VisitRoot()

    def tearDown(self):
        turbogears.startup.stopTurboGears()
        turbogears.config.update({'visit.timeout': self._visit_timeout})
        turbogears.config.update({'visit.on': self._visit_on})

    def test_visit_response(self):
        "Test if the visit cookie is set in cherrypy.response."
        testutil.create_request("/")
        print "simple cookies: %s" % cherrypy.response.simple_cookie
        assert cherrypy.response.simple_cookie.has_key(self.cookie_name)
        # the following command shuts down the visit framework properly
        # the test still passes without it, but exceptions are thrown later
        # once nose wants to quit.

    def test_new_visit(self):
        "Test that we can see a new visit on the server."
        testutil.create_request("/")
        assert turbogears.visit.current().is_new

    def test_old_visit(self):
        "Test if we can track a visitor over time."
        testutil.create_request("/")
        # first visit's cookie
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        testutil.create_request("/", headers=cookie_header(morsel))
        assert not turbogears.visit.current().is_new

    def test_cookie_expires(self):
        "Test if the visit timeout mechanism works."
        # set expiration to one second
        turbogears.config.update({'visit.timeout': 1.0/60})
        testutil.create_request("/")
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        time.sleep(3)  # 3 seconds
        testutil.create_request("/", headers=cookie_header(morsel))
        assert cherrypy.response.simple_cookie[self.cookie_name].value != morsel.value, \
            'cookie values should not match'
        assert turbogears.visit.current().is_new, \
            'this should be a new visit, as the cookie has expired'

    def test_cookie_re_sent(self):
        "Test whether the visit cookie is re-sent with new expiry time."
        testutil.create_request('/')
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        exp1 = time.strptime(morsel['expires'], '%a, %d-%b-%Y %H:%M:%S GMT')
        # sleep one second to ensure that we get a new expiry time.
        time.sleep(1)
        headers = {'Cookie': morsel.output(header='')[1:]}
        testutil.create_request('/', headers=headers)
        assert self.cookie_name in cherrypy.response.simple_cookie
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        exp2 = time.strptime(morsel['expires'], '%a, %d-%b-%Y %H:%M:%S GMT')
        assert exp1 < exp2
