from content import *
from content import IContentPermissions

from roles import *
from roles import IDolmenRoles

from zope.interface import moduleProvides


class IDolmenSecurity(IContentPermissions, IDolmenRoles):
    """A public Dolmen security API
    """

moduleProvides(IDolmenSecurity)
__all__ = list(IDolmenSecurity)
