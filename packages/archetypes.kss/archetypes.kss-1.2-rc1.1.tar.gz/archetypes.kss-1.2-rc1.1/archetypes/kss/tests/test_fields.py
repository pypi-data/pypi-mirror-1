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
from plone.app.kss.tests.kss_and_plone_layer import KSSAndPloneTestCase

PloneTestCase.setupPloneSite()

class FieldsViewTestCase(KSSAndPloneTestCase):

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
    # test the KSS methods
    # --

    def testReplaceField(self):
        self.view.context.changeSkin('Plone Default')
        result = self.view.replaceField('title', 'kss_generic_macros', 'title-field-view')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
            ('setStyle', '.portalMessage', 'css'),
            ('replaceInnerHTML', 'kssPortalMessage', 'htmlid'),
            ('setAttribute', 'kssPortalMessage', 'htmlid'),
            ('setStyle', 'kssPortalMessage', 'htmlid'),
            ('replaceHTML', 'parent-fieldname-title', 'htmlid'),
            ('focus', '#parent-fieldname-title .firstToFocus', '')
        ])

    def testReplaceWithView(self):
        self.view.context.changeSkin('Plone Default')
        result = self.view.replaceWithView('title', 'kss_generic_macros', 'title-field-view')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
             ('replaceHTML', 'parent-fieldname-title', 'htmlid'),
            ])

    def testSaveField(self):
        view = self.view
        result = view.saveField('title', {'title':'My Title'}, 
                                'kss_generic_macros', 'title-field-view')
        self.assertEqual([(r['name'], r['selector'], r['selectorType'])
                             for r in result], [
             ('replaceHTML', 'parent-fieldname-title', 'htmlid'),
            ])
        self.assertEqual('My Title', self.portal['front-page'].Title())
        res = view.saveField('description',
                             {'description':'Woot a funky description!'},
                             'kss_generic_macros', 'description-field-view')
        self.assertEqual('Woot a funky description!', self.portal['front-page'].Description())
    
    def testSaveFieldWithEvents(self):
        view = self.view
        result = view.saveField('title', {'title':'My Title'}, 
                                'kss_generic_macros', 'title-field-view')
        self.assertEqual('My Title', self.portal['front-page'].Title())
        res = view.saveField('description',
                             {'description':'Woot a funky description!'},
                             'kss_generic_macros', 'description-field-view')
        self.assertEqual('Woot a funky description!', self.portal['front-page'].Description())


    def testMarkerInATField(self):
        # writeable
        view = self.portal['front-page'].restrictedTraverse('kss_field_decorator_view')
        result = view.getKssClasses('title')
        self.assertEqual(result, ' kssattr-atfieldname-title kssattr-macro-title-field-view')
        result = view.getKssClasses('title', 'template')
        self.assertEqual(result, ' kssattr-atfieldname-title kssattr-templateId-template kssattr-macro-title-field-view')
        result = view.getKssClasses('title', 'template', 'macro')
        self.assertEqual(result, ' kssattr-atfieldname-title kssattr-templateId-template kssattr-macro-macro')
        self.logout()
        result = view.getKssClasses('title')
        # not writeable
        self.assertEqual(result, '')

    def testMarkerInATFieldInlineEditable(self):
        # writeable
        view = self.portal['front-page'].restrictedTraverse('kss_field_decorator_view')
        result = view.getKssClassesInlineEditable('title', 'template')
        self.assertEqual(result, ' kssattr-atfieldname-title kssattr-templateId-template kssattr-macro-title-field-view inlineEditable')
        result = view.getKssClassesInlineEditable('title', 'template', 'macro')
        self.assertEqual(result, ' kssattr-atfieldname-title kssattr-templateId-template kssattr-macro-macro inlineEditable')
        self.logout()
        # not writeable
        result = view.getKssClassesInlineEditable('title', 'template')
        self.assertEqual(result, '')

    def testMarkerInNonATField(self):
        # portal root is not an AT object
        view = self.portal.restrictedTraverse('kss_field_decorator_view')
        result = view.getKssClasses('title')
        # not writeable
        self.assertEqual(result, '')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FieldsViewTestCase),
        ))
