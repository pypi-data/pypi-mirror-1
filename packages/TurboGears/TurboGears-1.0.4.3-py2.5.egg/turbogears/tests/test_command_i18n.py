import sys
import os
import kid
import tempfile

from datetime import datetime

import turbogears
from turbogears.command.i18n import InternationalizationTool

work_dir = tempfile.mkdtemp()
locale_dir = os.path.join(work_dir, 'locale')
tool = None

turbogears.config.update({
    'i18n.locale_dir':locale_dir,
    'i18n.domain':'testmessages',
})

def setup(m):
    global tool
    tool = InternationalizationTool('0.9')

def teardown(m):
    import shutil
    shutil.rmtree(work_dir)

def test_creates_locale_dir():
    "Verify the locale directory got created as needed."
    assert not os.path.isdir(locale_dir)
    test_src_dir = os.path.join(work_dir, 'src')
    sys.argv = ['i18n.py', '--src-dir', test_src_dir, 'collect']
    tool.config = False
    tool.run()
    assert os.path.isdir(locale_dir), "locale directory not created"

TEMPLATE = """
<html xmlns:py="http://purl.org/kid/ns#">
<head>
    <link py:strip="1" py:for="css in tg_css">${css.display()}</link>
    <link py:strip="1" py:for="js in tg_js_head">${js.display()}</link>
</head>
<body>
  <div>Some text to be i18n'ed</div>
  <div>This is text that has a kid-expression ${_('which is to be i18n')}</div>
  <div foo="${_('kid expression in attribute')}"/>
  <div foo="normal attribute text"/>
  <div lang="en">This is english, and it shouldn't be collected</div>
  <div lang="de">Dies ist Deutsch, und es sollte nicht aufgesammelt werden</div>
  <div>These are some entities that we shouldn't complain about: &nbsp;</div>
</body>
</html>
"""
def test_collect_template_strings():
    "Verify the locale directory got created as needed."
    test_src_dir = os.path.join(work_dir, 'src')
    os.mkdir(test_src_dir)
    tf = open(os.path.join(test_src_dir, "test.kid"), "w")
    tf.write(TEMPLATE)
    tf.close()
    sys.argv = ['i18n.py', '--src-dir', test_src_dir, 'collect']
    tool.config = False
    tool.run()
    pot_content = open(os.path.join(locale_dir, "testmessages.pot")).read()
    assert "Some text to be i18n'ed" in pot_content
    assert "kid expression in attribute" in pot_content
    assert not "normal attribute text" in pot_content
    assert not "This is english, and it shouldn't be collected" in pot_content
    assert not "Dies ist Deutsch, und es sollte nicht aufgesammelt werden" in pot_content

