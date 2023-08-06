# -*- coding: utf-8 -*-
# Author: Roberto Allende (rover@menttes.com)
# Copyright (c) 2008 by Menttes SRL
# GNU General Public License (GPL)
#

import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import menttes.action.createfolder

from zope.interface import implements, Interface
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IObjectEvent

from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable
from plone.app.contentrules.rule import Rule

import menttes.action.createfolder

from menttes.action.createfolder.createfolder import CreatefolderAction
from menttes.action.createfolder.createfolder import CreatefolderEditForm

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestCreatefolderaction(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             menttes.action.createfolder)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        self.setRoles(('Manager',))
#       self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'testfolder')
#        self.login(default_user)
#        self.folder.invokeFactory('Document', 'd1')



    def testRegistered(self): 
        element = getUtility(IRuleAction,
                             name='menttes.action.createfolder.Createfolder')
        self.assertEquals('menttes.action.createfolder.Createfolder',
                           element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)
    
    def testInvokeAddView(self): 
        element = getUtility(IRuleAction,
                             name='menttes.action.createfolder.Createfolder')
        storage = getUtility(IRuleStorage)


        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
         
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST),
                                   name=element.addview)
         
        addview.createAndAdd(data={'foldername' : 'foo'})
         
        e = rule.actions[0]

        self.failUnless(isinstance(e, CreatefolderAction))
        self.assertEquals('foo', e.foldername)
     
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction,
                             name='menttes.action.createfolder.Createfolder')
        storage = getUtility(IRuleStorage)

        e = CreatefolderAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, CreatefolderEditForm))

    def testExecute(self): 
        e = CreatefolderAction()
        e.foldername = 'foo'
        ex = getMultiAdapter(( self.portal.testfolder , e, 
                               DummyEvent(self.portal.testfolder )), IExecutable)
        self.assertEquals(True, ex())
        self.failUnless('foo' in self.portal.testfolder.objectIds())

def test_suite():
    return unittest.TestSuite([ unittest.makeSuite(TestCreatefolderaction)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
