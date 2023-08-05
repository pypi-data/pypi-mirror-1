# -*- coding: utf-8 -*-
#
# File: haspartoftype.py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__    = """Hans-Peter Locher<hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'
__revision__  = "$Revision: 36831 $"
__version__   = '$Revision: 1.7 $'[11:-2]

from persistent import Persistent
from OFS.SimpleItem import SimpleItem

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

import email
from mailtoplone.base.interfaces import IEmail
from mailtoplone.contentrules import baseMessageFactory as _

class IHasPartOfTypeCondition(Interface):
    """Interface for the configurable aspects of a HasPartOfType condition.
    
    This is also used to create add and edit forms, below.
    """
    maintype = schema.TextLine(title=_(u"Maintype"),
                                    description=_(u"The maintype to check for"),
                                    required=False)
    subtype = schema.TextLine(title=_(u"Subtype"),
                                    description=_(u"The subtype to check for"),
                                    required=False)
         
class HasPartOfTypeCondition(SimpleItem):
    """The actual persistent implementation of the HasPartOfType condition.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(IHasPartOfTypeCondition, IRuleElementData)
    maintype = u''
    subtype = u''
    element = "mailtoplone.contentrules.conditions.HasPartOfType"
    
    @property
    def summary(self):
        return _(u"Check if the email contains a part with maintype/subtype pair ${maintype}/${subtype}", mapping=dict(maintype=self.maintype,subtype=self.subtype))

class HasPartOfTypeConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IHasPartOfTypeCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        maintype = self.element.maintype
        subtype = self.element.subtype
        if not IEmail.providedBy(obj):
            return False
        
        mailobj = email.message_from_string(obj.data)
        for part in mailobj.walk():
            if maintype and subtype:
                if part.get_content_maintype() == maintype and part.get_content_subtype() == subtype:
                    return True
            if maintype and not subtype:
                if part.get_content_maintype() == maintype:
                    return True
            if not maintype and subtype:
                if part.get_content_subtype() == subtype:
                    return True
            if not maintype and not subtype:
                return True
        return False

class HasPartOfTypeAddForm(AddForm):
    """An add form for HasPartOfType rule conditions.
    """
    form_fields = form.FormFields(IHasPartOfTypeCondition)
    label = _(u"Add HasPartOfType Condition")
    description = _(u"A HasPartOfType Condition checks if the email contains a part of specified maintype/subtype")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = HasPartOfTypeCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class HasPartOfTypeEditForm(EditForm):
    """An edit form for portal type conditions
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IHasPartOfTypeCondition)
    label = _(u"Edit HasPartOfType Condition")
    description = _(u"A HasPartOfType Condition checks if the email contains a part of specified maintype/subtype")
    form_name = _(u"Configure element")

# vim: set ft=python ts=4 sw=4 expandtab :
