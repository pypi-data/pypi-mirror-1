# -*- coding: utf-8 -*-

import grok
from zope.interface import Interface, Attribute, moduleProvides


class CanAddContent(grok.Permission):
    grok.name('dolmen.content.Add')
    grok.title('dolmen: add content')


class CanEditContent(grok.Permission):
    grok.name('dolmen.content.Edit')
    grok.title('dolmen: edit content')


class CanViewContent(grok.Permission):
    grok.name('dolmen.content.View')
    grok.title('dolmen: view content')


class CanListContent(grok.Permission):
    grok.name('dolmen.content.List')
    grok.title('dolmen: list content')


class CanDeleteContent(grok.Permission):
    grok.name('dolmen.content.Delete')
    grok.title('dolmen: delete content')


class CanCopyContent(grok.Permission):
    grok.name('dolmen.content.Copy')
    grok.title('dolmen: copy content')


class CanCutContent(grok.Permission):
    grok.name('dolmen.content.Cut')
    grok.title('dolmen: cut content')


class CanPasteContent(grok.Permission):
    grok.name('dolmen.content.Paste')
    grok.title('dolmen: paste content')

    
class CanReviewContent(grok.Permission):
    grok.name('dolmen.control.Review')
    grok.title('dolmen: review content')


class IContentPermissions(Interface):
    """Public Dolmen content centric permissions
    """
    CanAddContent = Attribute("Add content.")
    CanEditContent = Attribute("Edit content.")
    CanViewContent = Attribute("View content.")
    CanListContent = Attribute("List the container content.")
    CanDeleteContent = Attribute("Delete content.")
    CanCopyContent = Attribute("Copy content to the clipboard.")
    CanPasteContent = Attribute("Paste content from the clipboard.")
    CanReviewContent = Attribute("Review and annotate content.")


moduleProvides(IContentPermissions)
__all__ = list(IContentPermissions)
