"""Tests for integration of ToscaWidgets with TurboGears."""

import re

import turbogears as tg
from turbogears import testutil

try:
    from tw.api import (CSSLink, CSSSource, JSLink, JSSource, WidgetsList,
        locations as tw_locations)
    from tw.forms import TableForm, TextField
except ImportError, e:
    import warnings
    warnings.warn("ToscaWidgets not installed. Can not perform TG integration "
            "unit tests!: %s" % e)
else:
    css_link = CSSLink(modname="turbogears.tests", filename="foo.css")
    css_src = CSSSource("body {font-size: 1.em;}")
    js_link = JSLink(modname="turbogears.tests", filename="foo.js")
    js_head_src = JSSource("alert('head');")
    js_headbottom_src = JSSource("alert('headbottom');",
        location=tw_locations.headbottom)
    js_bodytop_src = JSSource("alert('bodytop');",
        location=tw_locations.bodytop)
    js_bodybottom_src = JSSource("alert('bodybottom');",
        location=tw_locations.bodybottom)

    rx_css_link = r'<link.*?href=".*?%s".*?>'
    rx_js_link = r'<script.*?src=".*?%s".*?>'
    rx_css_src = r'<style.*?>\s*?%s\s*?</style>'
    rx_js_src = r'<script.*?>\s*?%s\s*?</script>'

    class FormWithResources(TableForm):
        class fields(WidgetsList):
            title = TextField()

        javascript = [js_link, js_head_src, js_headbottom_src, js_bodytop_src,
            js_bodybottom_src]
        css = [css_link, css_src]

        # Make sure that the old resource retrieval interface can not be used
        def retrieve_javascript(self):
            raise NotImplementedError
        def retrieve_css(self):
            raise NotImplementedError

    form = FormWithResources()

    class MyRoot(tg.controllers.RootController):
        @tg.expose(template="turbogears.tests.form")
        def showform(self):
            return dict(form=form)

        @tg.expose(template="kid:turbogears.tests.form")
        def showform_kid(self):
            return dict(form=form)

    class ToscaWidgetsTest(testutil.TGTest):

        root = MyRoot

        def setUp(self):
            self.defaultview =  tg.config.get('tg.defaultview', 'kid')
            tg.config.update({
                'toscawidgets.on': True,
                'tg.defaultview': "genshi"
            })
            super(ToscaWidgetsTest, self).setUp()

        def tearDown(self):
            super(ToscaWidgetsTest, self).tearDown()
            tg.config.update({
                'toscawidgets.on': False,
                'tg.defaultview': self.defaultview
            })

        def test_css_inclusion(self):
            """Inclusion of CSS widgets in Genshi templates works with ToscaWidgets."""
            response = self.app.get("/showform")
            assert re.search(rx_css_src % r"body \{font-size: 1\.em;\}",
                response.body)
            assert re.search(rx_css_link % r'foo\.css', response.body)

        def test_js_inclusion(self):
            """Inclusion of JS widgets in Genshi templates works with ToscaWidgets."""
            response = self.app.get("/showform")
            for src in (r"alert\('head'\);", r"alert\('headbottom'\);",
                    r"alert\('bodytop'\);", r"alert\('bodybottom'\);"):
                assert re.search(rx_js_src % src, response.body)
            assert re.search(rx_js_link % r'foo\.js', response.body)

        def test_css_inclusion_kid(self):
            """Inclusion of CSS widgets in Kid templates works with ToscaWidgets."""
            response = self.app.get("/showform_kid")
            assert re.search(rx_css_src % r"body \{font-size: 1\.em;\}",
                response.body)
            assert re.search(rx_css_link % r'foo\.css', response.body)

        def test_js_inclusion_kid(self):
            """Inclusion of JS widgets in Kid templates works with ToscaWidgets."""
            response = self.app.get("/showform_kid")
            for src in (r"alert\('head'\);", r"alert\('headbottom'\);",
                    r"alert\('bodytop'\);", r"alert\('bodybottom'\);"):
                assert re.search(rx_js_src % src, response.body)
            assert re.search(rx_js_link % r'foo\.js', response.body)
