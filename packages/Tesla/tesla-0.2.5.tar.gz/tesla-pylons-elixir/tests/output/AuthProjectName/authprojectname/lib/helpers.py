"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.helpers import log, abort
from pylons.i18n import get_lang, set_lang
from authprojectname.lib.auth import get_user

def get_object_or_404(model, **kw):
    """
    Returns object, or raises a 404 Not Found is object is not in db 
    Example: user = get_object_or_404(model.User, id = 1)
    """
    obj = model.get_by(**kw)
    if obj is None:
        abort(404)
    return obj

def has_permission(perm):
    "Checks if current user has given permission"
    user = get_user()
    return (user and user.has_permission(perm))