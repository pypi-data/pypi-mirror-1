# -*- coding: utf-8 -*-
#
# File: sizeofmail.py
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

from mailtoplone.base.interfaces import IEmail
from mailtoplone.contentrules import baseMessageFactory as _

class ISizeOfMailCondition(Interface):
    """Interface for the configurable aspects of a SizeOfMail condition.
    
    This is also used to create add and edit forms, below.
    """
    operator = schema.Choice(title=_(u"Relational operator"),
                                    description=_(u"The relational operator to be used"),
                                    required=True,
                                    values=['>=','<='],
                                    default='>=')
    size = schema.Int(title=_(u"Size"),
                                    description=_(u"The size to check for in megabytes"),
                                    required=True)

         
class SizeOfMailCondition(SimpleItem):
    """The actual persistent implementation of the SizeOfMail condition.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(ISizeOfMailCondition, IRuleElementData)
    operator = u''
    size = u''
    element = "mailtoplone.contentrules.conditions.SizeOfMail"
    
    @property
    def summary(self):
        return _(u"Check if mail is ${operator} ${size} megabytes", mapping=dict(operator=self.operator,size=self.size))

class SizeOfMailConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, ISizeOfMailCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        operator = self.element.operator
        size = self.element.size * 1024 * 1024
        if not IEmail.providedBy(obj):
            return False
       
        if operator == '>=':
            return len(obj.data) >= size

        if operator == '<=':
            return len(obj.data) <= size

        return False
        
class SizeOfMailAddForm(AddForm):
    """An add form for SizeOfMail rule conditions.
    """
    form_fields = form.FormFields(ISizeOfMailCondition)
    label = _(u"Add SizeOfMail Condition")
    description = _(u"An SizeOfMail Condition checks the size of a mail (<=, >=) against a user specified size in megabyte")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = SizeOfMailCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class SizeOfMailEditForm(EditForm):
    """An edit form for portal type conditions
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(ISizeOfMailCondition)
    label = _(u"Edit SizeOfMail Condition")
    description = _(u"An SizeOfMail Condition checks the size of a mail (<=, >=) against a user specified size in megabyte")
    form_name = _(u"Configure element")

# vim: set ft=python ts=4 sw=4 expandtab :
