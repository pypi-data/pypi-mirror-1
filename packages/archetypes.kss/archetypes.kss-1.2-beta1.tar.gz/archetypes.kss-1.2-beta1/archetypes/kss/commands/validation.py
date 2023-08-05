
from kss.core.azaxview import AzaxViewAdapter

class ValidationCommands(AzaxViewAdapter):
    __allow_access_to_unprotected_subobjects__ = 1
    
    def issueFieldError(self, fieldname, error):
        'Issue this error message for the field'
        ksscore = self.getCommandSet('core')
        selector = ksscore.getCssSelector('div#archetypes-fieldname-%s div.fieldErrorBox' % fieldname)
        if error:
            ksscore.replaceInnerHTML(selector, error)
            errorklass = ' error'
        else:
            ksscore.clearChildNodes(selector)
            errorklass = ''
        klass = "field%s Archetypes%sfield" % (errorklass, fieldname)
        # set the field style in the required way
        ksscore.setAttribute(
            ksscore.getHtmlIdSelector('archetypes-fieldname-%s' % fieldname),
            'class', klass)
