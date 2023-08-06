"""Distributed Task Queue"""

VERSION = (0, 8, 0)

__version__ = ".".join(map(str, VERSION))
__author__ = "Ask Solem"
__contact__ = "askh@opera.com"
__homepage__ = "http://github.com/ask/celery/"
__docformat__ = "restructuredtext"


def is_stable_release():
    return bool(not VERSION[1] % 2)


def version_with_meta():
    meta = "unstable"
    if is_stable_release():
        meta = "stable"
    return "%s (%s)" % (__version__, meta)
