# -*- coding: UTF-8 -*-
# Copyright (c) 2006
# Authors:
#   Jean-Paul Ladage <j.ladage@zestsoftware.nl>, jladage
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

from plone.app.kss import AzaxBaseView
from plone.app.kss.interfaces import IPloneAzaxView
from plone.app.kss.interfaces import IPortalObject

from zope.interface import implements
from zope import lifecycleevent, event

from Acquisition import aq_inner
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class FieldsView(AzaxBaseView):
    
    implements(IPloneAzaxView)

    ## Kss methods
   
    field_wrapper = ZopeTwoPageTemplateFile('browser/field_wrapper.pt')
    def renderField(self, fieldname, mode='view'):
        """
        This method handles the rendering of a field, it calls either the edit or
        view macro based on the given mode.
        """
        context = self.context
        fieldname = fieldname.split('archetypes-fieldname-')[-1]
        field = context.getField(fieldname)
        code = field.widget(mode, context)
        res = self.field_wrapper(the_macro=code, field=field, instance=context, mode=mode)
        return res

    def replaceFieldHelper(self, fieldname, mode='view'):
        """
        """
        archetypes_fieldname = "archetypes-fieldname-%s" % fieldname
        res = self.renderField(fieldname, mode=mode)

        res = res.strip()
        ksscore = self.getCommandSet('core')
        if mode == 'view':
            if fieldname == 'title':
                res = '<h1 id="' + archetypes_fieldname + '" class="documentFirstHeading kukit-atfieldname-%s kukit-widgetstate-view">' % fieldname + res + '</h1>'
            if fieldname=='description':
                res = '<p id="' + archetypes_fieldname + '" class="documentDescription kukit-atfieldname-%s kukit-widgetstate-view">' % fieldname + res + '</p>'
            if fieldname=='text':
                res = '<div id="' + archetypes_fieldname + '" class="plain kukit-atfieldname-%s kukit-widgetstate-view">' % fieldname + res + '</div>'
            ksscore.replaceHTML(ksscore.getHtmlIdSelector('azax-inlineform-%s'%fieldname), res)
        if mode == 'edit':
            ksscore.replaceHTML(ksscore.getHtmlIdSelector(archetypes_fieldname), res)

    def replaceField(self, fieldname, mode='view'):
        """
        """
        self.replaceFieldHelper(fieldname, mode)
        return self.render()

    def saveField(self, fieldname, value, mode='view'):
        """
        This method saves the current value to the field. and returns the rendered
        view macro.
        """
        # We receive a string or a dict in value.
        #
        # XXX we want to get rid of this! I believe that for all types
        # we support, there would be a possibility to just receive a string value.
        # what's more I think this is principally wrong because the mutator
        # does _not_ except the form in kwargs but already some values deducted
        # from it. If we really want to go this way we should use process_input
        # from the widget, but since we can make a per widget customized solution
        # the best would be just to pass what we need instead of passing the entire
        # form (if possible).
        if isinstance(value, basestring):
            kwargs = {}
        else:
            kwargs = dict(value)
            value = kwargs.get(fieldname, '')
        #
        instance = self.context.aq_inner
        field = instance.getField(fieldname)
        error = field.validate(value, instance, {})
        if not error and field.writeable(instance):
            setField = field.getMutator(instance)
            setField(value, **kwargs)
            self.context.reindexObject() #XXX: Temp workaround, should be gone in AT 1.5
            
            descriptor = lifecycleevent.Attributes(IPortalObject, fieldname)
            event.notify(ObjectEditedEvent(self.context, descriptor))
            
            self.replaceFieldHelper(fieldname=fieldname, mode='view')
        else:
            if not error:
                # XXX This should not actually happen...
                error = 'Field is not writeable.'
            # Send back the validation error
            self.getCommandSet('atvalidation').issueFieldError(fieldname, error)
        return self.render()


# --
# (Non-ajax) browser view for decorating the field
# --

class ATFieldDecoratorView(BrowserView):

    def kss_class(self, fieldname, mode, singleclick=False):
        context = aq_inner(self.context)
        field = context.getField(fieldname)
        if field.writeable(context):
            # kukit-atfieldname-FIELDNAME:  the generic field marker
            # kukit-widgetstate-STATE:      the widgets's state
            # kssFieldClickable:            selector for clickable
            # kssFieldDblClickable:         selector for double clickable
            classstring = ' kukit-atfieldname-%s kukit-widgetstate-%s' % (fieldname, mode)
            if singleclick:
                classstring += ' kssFieldClickable'
            else:
                classstring += ' kssFieldDblClickable'
        else:
            classstring = ''
        return classstring
