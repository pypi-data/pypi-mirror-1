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
from zope.publisher.interfaces.browser import IBrowserView

from Acquisition import aq_inner
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class FieldsView(AzaxBaseView):
    
    implements(IPloneAzaxView)

    ## Kss methods
   
    view_field_wrapper = ZopeTwoPageTemplateFile('browser/view_field_wrapper.pt')
    edit_field_wrapper = ZopeTwoPageTemplateFile('browser/edit_field_wrapper.pt')

    def renderViewField(self, fieldname, templateId, macro):
        """
        renders the macro coming from the view template
        """
        template = self.context.restrictedTraverse(templateId)
        
        if IBrowserView.providedBy(template):
            view = template
            for attr in ('index', 'template', '__call__'):
                template = getattr(view, attr, None)
                if template is not None and hasattr(template, 'macros'):
                    break
            if template is None:
                raise KeyError("Unable to find template for view %s" % templateId)

        viewMacro = template.macros[macro]
        res = self.view_field_wrapper(viewMacro=viewMacro,
                                      context=self.context,
                                      templateId=templateId)
        return res

    def renderEditField(self, fieldname, templateId, macro):
        """
        renders the edit widget inside the macro coming from the view template
        """
        context = self.context
        fieldname = fieldname.split('archetypes-fieldname-')[-1]
        field = context.getField(fieldname)
        template = context.restrictedTraverse(templateId)
        
        
        if IBrowserView.providedBy(template):
            view = template
            for attr in ('index', 'template', '__call__'):
                template = getattr(view, attr, None)
                if template is not None and hasattr(template, 'macros'):
                    break
            if template is None:
                raise KeyError("Unable to find template for view %s" % templateId)
        
        containingMacro = template.macros[macro]
        widget = field.widget
        widgetMacro = widget('edit', context)
        
        res = self.edit_field_wrapper(containingMacro=containingMacro,
                                      widgetMacro=widgetMacro,
                                      field=field, instance=context,
                                      mode='edit',
                                      templateId=templateId)
        return res

    def replaceField(self, fieldname, templateId, macro):
        """
        kss commands to replace the field value by the edit widget
        """
        parent_fieldname = "parent-fieldname-%s" % fieldname
        html = self.renderEditField(fieldname, templateId, macro)
        html = html.strip()
        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(parent_fieldname), html)
        ksscore.focus("#%s .firstToFocus" % parent_fieldname)
        return self.render()


    def replaceWithView(self, fieldname, templateId, macro):
        """
        kss commands to replace the edit widget by the field view
        """
        parent_fieldname = "parent-fieldname-%s" % fieldname
        html = self.renderViewField(fieldname, templateId, macro)
        html = html.strip()
        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML(ksscore.getHtmlIdSelector(parent_fieldname), html)
        return self.render()


    def saveField(self, fieldname, value, templateId, macro):
        """
        This method saves the current value to the field. and returns the rendered
        view macro.
        """
        # We receive a dict in value.
        #
        instance = self.context.aq_inner
        field = instance.getField(fieldname)
        value, kwargs = field.widget.process_form(instance, field, value)
        error = field.validate(value, instance, {})
        if not error and field.writeable(instance):
            setField = field.getMutator(instance)
            setField(value, **kwargs)
            self.context.reindexObject() #XXX: Temp workaround, should be gone in AT 1.5
            
            descriptor = lifecycleevent.Attributes(IPortalObject, fieldname)
            event.notify(ObjectEditedEvent(self.context, descriptor))
            
            return self.replaceWithView(fieldname, templateId, macro)
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

    def getKssClasses(self, fieldname, templateId=None, macro=None):
        context = aq_inner(self.context)
        field = context.getField(fieldname)
        # field can be None when widgets are used without fields
        # check whether field is valid
        if field is not None and field.writeable(context):
            classstring = ' kssattr-atfieldname-%s' % fieldname
            if templateId is not None:
                classstring += ' kssattr-templateId-%s' % templateId
            if macro is not None:
                classstring += ' kssattr-macro-%s' % macro
            else:
                classstring += ' kssattr-macro-%s-field-view' % fieldname
        else:
            classstring = ''
        return classstring
    
    def getKssClassesInlineEditable(self, fieldname, templateId, macro=None):
        classstring = self.getKssClasses(fieldname, templateId, macro)
        if classstring:
            classstring += ' inlineEditable'
        return classstring
