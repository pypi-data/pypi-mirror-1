"""quixote
$HeadURL: svn+ssh://svn.mems-exchange.org/repos/trunk/quixote/__init__.py $
$Id: __init__.py 25830 2005-01-05 18:37:29Z dbinger $

A highly Pythonic web application framework.
"""

__version__ = '2.0a4'

# These are frequently needed by Quixote applications.
from quixote.publish import \
     get_publisher, get_request, get_response, get_path, redirect, \
     get_session, get_session_manager, get_user, get_field, get_cookie


def enable_ptl():
    """
    Installs the import hooks needed to import PTL modules.  This must
    be done explicitly because not all Quixote applications need to use
    PTL, and import hooks are deep magic that can cause all sorts of
    mischief and deeply confuse innocent bystanders.  Thus, we avoid
    invoking them behind the programmer's back.  One known problem is
    that, if you use ZODB, you must import ZODB before calling this
    function.
    """
    from quixote import ptl_import
    ptl_import.install()
