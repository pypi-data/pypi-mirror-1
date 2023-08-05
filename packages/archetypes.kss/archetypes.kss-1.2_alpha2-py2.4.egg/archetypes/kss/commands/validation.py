
from kss.core.azaxview import AzaxViewAdapter
#from kss.core import force_unicode

class ValidationCommands(AzaxViewAdapter):
    __allow_access_to_unprotected_subobjects__ = 1
    
    def issueFieldError(self, fieldname, error):
        'Issue this error message for the field'
        # XXX translation?
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#archetypes-fieldname-%s div.fieldErrorBox' % fieldname)
        if error:
            # Blame AT for not using unicodes.
            #error = force_unicode(error, 'utf')
            ksscore.replaceInnerHTML(selector, error)
            errorklass = ' error'
        else:
            ksscore.clearChildNodes(selector)
            errorklass = ''
        klass ="field%s Archetypes%sfield kukit-atfieldname-%s kukit-widgetstate-edit" % \
                    (errorklass, fieldname, fieldname)
        # set the field style in the required way
        ksscore.setAttribute(
            ksscore.getHtmlIdSelector('archetypes-fieldname-%s' % fieldname),
            'class', klass)
