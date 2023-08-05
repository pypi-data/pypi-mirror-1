import logging

import formencode
import formencode.variabledecode as variabledecode

import pylons

from decorator import decorator

from formencode import htmlfill
from paste.util.multidict import UnicodeMultiDict
from pylons.i18n import _
from pylons.helpers import abort

from authxpprojectname.lib.auth import redirect_to_login

log = logging.getLogger(__name__)

def authorize(permission):
    
    """Decorator for authenticating individual actions. Takes a permission 
    instance as argument(see lib/permissions.py for examples)"""
    def wrapper(func, self, *args, **kw):
        if permission.check():
            log.debug("Checking permission")
            return func(self, *args, **kw)
        redirect_to_login()
    return decorator(wrapper)

