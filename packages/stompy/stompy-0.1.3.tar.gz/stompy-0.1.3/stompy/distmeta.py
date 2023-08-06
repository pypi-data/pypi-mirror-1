"""Implementation of the STOMP protocol in Python."""
VERSION = (0, 1, 3)
__version__ = ".".join(map(str, VERSION))
__author__ = "Benjamin W. Smith"
__contact__ = "benjaminwarfield@just-another.net"
__homepage__ = "http://bitbucket.org/benjaminws/python-stomp/"
__docformat__ = "restructuredtext"
__doc__ = "For documentation, see: packages.python.org/stompy/"


def is_stable_release():
    return bool(not VERSION[1] % 2)


def version_with_meta():
    meta = "unstable"
    if is_stable_release():
        meta = "stable"
    return "%s (%s)" % (__version__, meta)
