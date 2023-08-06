"""TurboGears Front-to-Back Web Framework"""

import pkg_resources

from turbogears import config
from turbogears.controllers import (absolute_url, expose, flash, validate,
    redirect, error_handler, exception_handler, url)
from turbogears import (controllers, view, database, validators, command,
    i18n, widgets, startup, scheduler)
from turbogears.release import (version as __version__, author as __author__,
    email as __email__, license as __license__, copyright as __copyright__)
from turbogears.widgets import mochikit
from turbogears.widgets import jsi18nwidget
from turbogears.config import update_config
from turbogears.paginate import paginate

from turbogears.startup import start_server

# XXX: obsolete --> to be removed
extensions = pkg_resources.iter_entry_points("turbogears.extensions")
for entrypoint in extensions:
    ext = entrypoint.load()
    if hasattr(ext, "tgsymbols"):
        globals().update(ext.tgsymbols())

i18n.install() # adds _ (gettext) to builtins namespace


__all__ = [
    "absolute_url",
    "database",
    "command",
    "config",
    "controllers",
    "expose",
    "flash",
    "error_handler",
    "exception_handler",
    "mochikit",
    "redirect",
    "scheduler",
    "start_server",
    "update_config",
    "url",
    "validate",
    "validators",
    "view",
    "widgets",
]
