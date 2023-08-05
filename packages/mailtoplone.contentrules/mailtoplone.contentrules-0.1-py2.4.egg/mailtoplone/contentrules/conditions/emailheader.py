# -*- coding: utf-8 -*-
#
# File: emailheader.py
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
import re
from mailtoplone.base.interfaces import IEmail
from mailtoplone.contentrules import baseMessageFactory as _
from mailtoplone.contentrules.config import vo_headers, vo_headers_default

class IEmailHeaderCondition(Interface):
    """Interface for the configurable aspects of a portal type condition.
    
    This is also used to create add and edit forms, below.
    """
    header = schema.Choice(title=_(u"Email Header"),
                                    description=_(u"The Email Header to check for"),
                                    required=True,
                                    values=vo_headers,
                                    default=vo_headers_default)
    value = schema.TextLine(title=_(u"Value"),
                                    description=_(u"The Value to check for"),
                                    required=True)

         
class EmailHeaderCondition(SimpleItem):
    """The actual persistent implementation of the file extension condition.
    
    Note that we must mix in Explicit to keep Zope 2 security happy.
    """
    implements(IEmailHeaderCondition, IRuleElementData)
    header = u''
    value = u''
    element = "mailtoplone.contentrules.conditions.EmailHeader"
    
    @property
    def summary(self):
        return _(u"Check ${header} for ${value}", mapping=dict(header=self.header,value=self.value))

class EmailHeaderConditionExecutor(object):
    """The executor for this condition.
    
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, IEmailHeaderCondition, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        # TODO: 
        # - recursive functionality:add checkbox (go recursively through mail?)
        obj = self.event.object
        header = self.element.header
        value = self.element.value
        
        if not IEmail.providedBy(obj):
            return False
        
        mailobj = email.message_from_string(obj.data)
        if not header in mailobj.keys():
            return False
        
        # The user may enter a malformed regex, in that case, the input should be interpreted as
        # a string
        try:
            exp = re.compile(value)
        except:
            return value in mailobj.get(header)

        if re.search(exp,mailobj.get(header)):
            return True

        return False
        
class EmailHeaderAddForm(AddForm):
    """An add form for EmailHeader rule conditions.
    """
    form_fields = form.FormFields(IEmailHeaderCondition)
    label = _(u"Add EmailHeader Condition")
    description = _(u"An EmailHeader Condition checks a specified header for a specified value, specify value as regular expression")
    form_name = _(u"Configure element")
    
    def create(self, data):
        c = EmailHeaderCondition()
        form.applyChanges(c, self.form_fields, data)
        return c

class EmailHeaderEditForm(EditForm):
    """An edit form for portal type conditions
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IEmailHeaderCondition)
    label = _(u"Edit EmailHeader Condition")
    description = _(u"An EmailHeader Condition checks a specified header for a specified value, value can be a regular expression")
    form_name = _(u"Configure element")

# vim: set ft=python ts=4 sw=4 expandtab :
