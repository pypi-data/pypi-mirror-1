# -*- coding: UTF-8 -*-
# Copyright (c) 2006
# Authors:
#   Jean-Paul Ladage <j.ladage@zestsoftware.nl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

import unittest
from Products.PloneTestCase import PloneTestCase
from kss.core.tests.base import AzaxViewTestCase 

PloneTestCase.setupPloneSite()

class FieldsViewTestCase(PloneTestCase.PloneTestCase, AzaxViewTestCase):

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.loadCoreConfig(kss_core=False)
        # commands will be rendered as data structures,
        self.setDebugRequest()
        self.loginAsPortalOwner()
        context = self.portal['front-page']
        # Set up a view 
        self.view = context.restrictedTraverse('saveField')

    # --
    # test the Kss methods
    # --

    def testRenderField(self):
        # Test rendering a string field in both view and edit mode
        result = self.view.replaceField('title','view')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
             ('replaceHTML', 'azax-inlineform-title', 'htmlid'),
            ])

    def testRenderTitleWithEdit(self):
        result = self.view.replaceField('title','edit')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
             ('replaceHTML', 'archetypes-fieldname-title', 'htmlid'),
            ])

    def testSaveField(self):
        view = self.view
        result = view.saveField('title', 'My Title')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
             ('replaceHTML', 'azax-inlineform-title', 'htmlid'),
            ])
        self.assertEqual('My Title', self.portal['front-page'].Title())
        res = view.saveField('description', 'Woot a funky description!')
        self.assertEqual('Woot a funky description!', self.portal['front-page'].Description())
    
    def testSaveFieldWithEvents(self):
        view = self.view
        result = view.saveField('title', 'My Title')
        self.assertEqual('My Title', self.portal['front-page'].Title())
        res = view.saveField('description', 'Woot a funky description!')
        self.assertEqual('Woot a funky description!', self.portal['front-page'].Description())

    def testMarkerInATField(self):
        view = self.portal['front-page'].restrictedTraverse('kss_field_decorator_view')
        result = view.kss_class('title', 'view')
        # writeable
        self.assertEqual(result, ' kukit-atfieldname-title kukit-widgetstate-view kssFieldDblClickable')
        self.logout()
        result = view.kss_class('title', 'view')
        # not writeable
        self.assertEqual(result, '')

    def testMarkerInNonATField(self):
        # portal root is not an AT object
        view = self.portal.restrictedTraverse('kss_field_decorator_view')
        result = view.kss_class('title', 'view')
        # not writeable
        self.assertEqual(result, '')

    def testMarkerSingleClick(self):
        view = self.portal['front-page'].restrictedTraverse('kss_field_decorator_view')
        result = view.kss_class('title', 'view', singleclick=True)
        # writeable
        self.assertEqual(result, ' kukit-atfieldname-title kukit-widgetstate-view kssFieldClickable')
        self.logout()
        result = view.kss_class('title', 'view', singleclick=True)
        # not writeable
        self.assertEqual(result, '')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FieldsViewTestCase),
        ))
