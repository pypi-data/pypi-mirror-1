# -*- coding: utf-8 -*-

import grok
from zope.interface import Interface, Attribute, moduleProvides


class Member(grok.Role):
    grok.name('dolmen.Member')
    grok.permissions(
        'dolmen.content.View',
        'dolmen.content.Copy',
        )


class Owner(grok.Role):
    grok.name('dolmen.Owner')
    grok.permissions(
        'dolmen.content.Add',
        'dolmen.content.View',
        'dolmen.content.Edit',
        'dolmen.content.Cut',
        'dolmen.content.Copy',
        'dolmen.content.Paste',
        )
    

class Contributor(grok.Role):
    grok.name('dolmen.Contributor')
    grok.permissions(
        'dolmen.content.Add',
        'dolmen.content.View',
        'dolmen.content.Edit',
        'dolmen.content.Cut',
        'dolmen.content.Copy',
        'dolmen.content.Paste',
        )


class Reviewer(grok.Role):
    grok.name('dolmen.Reviewer')
    grok.permissions(
        'dolmen.content.View',
        'dolmen.content.Edit',
        'dolmen.control.Review',
        )


class IDolmenRoles(Interface):
    """The public Dolmen roles
    """
    Owner = Attribute("The owner of an object.")
    Member = Attribute("A basic member.")
    Reviewer = Attribute("A content reviewer.")
    Contributor = Attribute("A content contributor.")
    

moduleProvides(IDolmenRoles)
__all__ = list(IDolmenRoles)
