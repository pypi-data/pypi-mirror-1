from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound

import sys
import os

if sys.version_info < (2, 3):
    raise SystemExit("Python 2.3 or later is required")

execfile(os.path.join("turbogears", "release.py"))

# setup params
install_requires = [
            "TurboJson >= 0.9.9",
            "TurboCheetah >= 0.9.5",
            "TurboKid >= 1.0.2",
            "CherryPy >= 2.2.1,<3.0.0alpha",
            "simplejson >= 1.3",
            "elementtree >= 1.2.6",
            "PasteScript >= 0.9.7",
            "FormEncode >= 0.7.1",
            "setuptools >= 0.6c2",
            "RuleDispatch >= 0.5a0.dev-r2303",
            "DecoratorTools >= 1.4",
            "ConfigObj >= 4.3.2"]

tgtesttools =  ["nose >= 0.9.1", "SQLAlchemy>=0.3"]

standard = ["SQLObject>=0.8,<0.10dev"]

# python 2.5 compatible list
if sys.version_info < (2, 5):
    install_requires.extend([
        "cElementTree >= 1.0.5",
        ])
    tgtesttools.extend([
        "pysqlite"
        ])
    standard = ["SQLObject==bugfix,>=0.7.1dev-r1860,<=0.7.99"]
else:
    install_requires.extend([
        "Cheetah >= 2.0rc7",
        ])


setup(
    name="TurboGears",
    version=version,
    author=author,
    author_email=email,
    download_url="http://www.turbogears.org/download/filelist.html",
    dependency_links=[
        "http://files.turbogears.org/eggs/",
        ],
    license=license,
    description="front-to-back rapid web development",
    long_description="""
front-to-back rapid web development
===================================

TurboGears brings together four major pieces to create an
easy to install, easy to use web megaframework. It covers
everything from front end (MochiKit JavaScript for the browser,
Kid for templates in Python) to the controllers (CherryPy) to
the back end (SQLObject).

The TurboGears project is focused on providing documentation
and integration with these tools without losing touch
with the communities that already exist around those tools.

TurboGears is easy to use for a wide range of web applications.

The latest development version is available in
<a href="http://svn.turbogears.org/trunk#egg=turbogears-dev"
>the TurboGears subversion repository</a>.""",
    url="http://www.turbogears.org",
    zip_safe=False,
    install_requires = install_requires,
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={"thirdparty": ["*"]},
    entry_points = """
    [console_scripts]
    tg-admin = turbogears.command:main

    [distutils.commands]
    docs = turbogears.docgen:GenSite

    [paste.paster_create_template]
    tgbase = turbogears.command.quickstart:BaseTemplate
    turbogears = turbogears.command.quickstart:TurbogearsTemplate
    tgbig = turbogears.command.quickstart:TGBig
    tgwidget = turbogears.command.quickstart:TGWidgetTemplate

    [turbogears.command]
    quickstart = turbogears.command.quickstart:quickstart
    sql = turbogears.command.base:SQL
    shell = turbogears.command.base:Shell
    toolbox = turbogears.command.base:ToolboxCommand
    update = turbogears.command.quickstart:update
    i18n = turbogears.command.i18n:InternationalizationTool
    info = turbogears.command.info:InfoCommand

    [turbogears.identity.provider]
    sqlobject = turbogears.identity.soprovider:SqlObjectIdentityProvider
    sqlalchemy= turbogears.identity.saprovider:SqlAlchemyIdentityProvider

    [turbogears.extensions]
    identity = turbogears.identity.visitor
    visit = turbogears.visit

    [turbogears.visit.manager]
    sqlobject = turbogears.visit.sovisit:SqlObjectVisitManager
    sqlalchemy = turbogears.visit.savisit:SqlAlchemyVisitManager

    [turbogears.toolboxcommand]
    widgets = turbogears.toolbox.base:WidgetBrowser
    shell = turbogears.toolbox.shell:WebConsole
    admi18n = turbogears.toolbox.admi18n:Internationalization
    designer = turbogears.toolbox.designer:Designer
    info = turbogears.toolbox.base:Info
    catwalk = turbogears.toolbox.catwalk:CatWalk

    """,
    extras_require = {
        "exp" : ["TGFastData"],
        "standard" : standard,
        "future" : ["Genshi>=0.3", "SQLAlchemy>=0.3"],
        "testtools" : ["nose >= 0.9.1"],
        "tgtesttools" : tgtesttools,
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    test_suite = 'nose.collector',
    )

