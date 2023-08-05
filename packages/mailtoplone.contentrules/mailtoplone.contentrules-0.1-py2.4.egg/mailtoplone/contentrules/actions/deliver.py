# -*- coding: utf-8 -*-
#
# File: deliver.py
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

from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts, getUtility
from zope.formlib import form
from zope import schema

import OFS.subscribers

from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 
import transaction

from Acquisition import aq_inner, aq_parent, aq_base
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import utils

from mailtoplone.base.interfaces import IMailDropBoxFactory, IMailDropBox
from mailtoplone.contentrules import baseMessageFactory as _

class IDeliverAction(Interface):
    """Interface for the configurable aspects of a deliver action.
    
    This is also used to create add and edit forms, below.
    """
    
    key = schema.TextLine(title=_(u"Key"),
                                  description=_(u"Key used to determine the DropBox"),
                                  required=True,
                                  )

class DeliverAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IDeliverAction, IRuleElementData)
    
    key = ''
    element = 'mailtoplone.contentrules.actions.deliver'
    
    @property
    def summary(self):
        return _(u"Deliver to DropBoxes by key ${key}", mapping=dict(key=self.key))
    
class DeliverActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IDeliverAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        
        obj = self.event.object
        parent = aq_parent(aq_inner(obj))
        key = self.element.key
        dropbox_factory = getUtility(IMailDropBoxFactory)
        dropboxes = dropbox_factory(obj, key)

        for dropbox in dropboxes:
            if not dropbox is parent:
                IMailDropBox(dropbox).drop(obj.data)

        return True
        
class DeliverAddForm(AddForm):
    """An add form for deliver actions.
    """
    form_fields = form.FormFields(IDeliverAction)
    label = _(u"Add Deliver Action")
    description = _(u"A deliver action can drop an email to (a) different inbox(es).")
    form_name = _(u"Configure element")
    
    def create(self, data):
        a = DeliverAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class DeliverEditForm(EditForm):
    """An edit form for deliver rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IDeliverAction)
    label = _(u"Edit Deliver Action")
    description = _(u"A deliver action can drop an email to (a) different inbox(es).")
    form_name = _(u"Configure element")

# vim: set ft=python ts=4 sw=4 expandtab :
