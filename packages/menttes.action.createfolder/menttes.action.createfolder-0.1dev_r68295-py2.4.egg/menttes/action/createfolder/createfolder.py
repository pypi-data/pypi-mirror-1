# -*- coding: utf-8 -*-
# Author: Roberto Allende (rover@menttes.com)
# Copyright (c) 2008 by Menttes SRL
# GNU General Public License (GPL)
#

from OFS.SimpleItem import SimpleItem
from persistent import Persistent 

from zope.interface import implements, Interface
from zope.component import adapts
from zope.formlib import form
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone import PloneMessageFactory
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from plone.app.contentrules.browser.formhelper import AddForm, EditForm 

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

class ICreatefolderAction(Interface):
    """
    Interface for the configurable aspects of a notify action.
    This is also used to create add and edit forms, below.
    """

    foldername = schema.TextLine(title=_(u"Folder"),
                                    description=u"Name of the folder to be created",
                                    required=True,
                                 )

class CreatefolderAction(SimpleItem):
    """The actual persistent implementation of the notify action element.
    """
    implements(ICreatefolderAction, IRuleElementData)
    foldername = ''
    
    element = 'menttes.action.createfolder.Createfolder'

    @property    
    def summary(self):
        return _(u"Folder ${foldername}", mapping=dict(foldername=self.foldername))


class CreatefolderActionExecutor(object):
    """The executor for this action.
    This is registered as an adapter in configure.zcml
    """
    implements(IExecutable)
    adapts(Interface, ICreatefolderAction, Interface)
         
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        foldername = self.element.foldername
        normalized = '-'.join(foldername.split(' ')).lower()
        self.event.object.invokeFactory('Folder', title=foldername, id=normalized)
        return True 
        
class CreatefolderAddForm(AddForm):
    """An add form for notify rule actions.
    """
    form_fields = form.FormFields(ICreatefolderAction)
    label = _(u"Add Deafult Action")
    description = _(u"A notify action can show a message to the user.")
    form_name = _(u"Configure element")

    def create(self, data):
        a = CreatefolderAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class CreatefolderEditForm(EditForm):
    """An edit form for notify rule actions.
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(ICreatefolderAction)
    label = _(u"Edit Createfolder Action")
    description = _(u"A createfolder action can show a message to the user.")
    form_name = _(u"Configure element")
