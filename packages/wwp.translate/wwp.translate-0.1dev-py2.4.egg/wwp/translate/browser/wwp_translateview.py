from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from wwp.translate import translateMessageFactory as _


class Iwwp_translateView(Interface):
    """
    wwp_translate view interface
    """

    def test():
        """ test method"""


class wwp_translateView(BrowserView):
    """
    wwp_translate browser view
    """
    implements(Iwwp_translateView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    
    def google_form(self):
        
        g_frm = ''
        g_frm = g_frm+'<form name="f" id="f" action="#" onsubmit="translate(); return false;">'
        g_frm = g_frm+'Enter '+str(self.context.getFrom_lang_long())+' text here:<br /><textarea name="text" rows="7" cols="55"></textarea>'
        g_frm = g_frm+'<br /><br />'
        g_frm = g_frm+'<input type="submit" value="Translate!" onfocus="this.blur();" />'
        g_frm = g_frm+'<br /><br />'
        g_frm = g_frm+'Output in '+str(self.context.getTo_lang_long())+':<br /><textarea name="translation" rows="7" cols="55" onfocus="this.select();" readonly="true">'
        g_frm = g_frm+'</textarea>'
        g_frm = g_frm+'</form>'
        g_frm = g_frm+'<br />'
        g_frm = g_frm+'<script type="text/javascript" src="http://www.google.com/jsapi"></script> '
        g_frm = g_frm+'<script type="text/javascript">google.load("language", "1"); function translate() {var originaltext=document.forms["f"].text.value; google.language.translate(originaltext, "'
        g_frm = g_frm+ str(self.context.from_lang)
        g_frm = g_frm+ '", "'
        g_frm = g_frm+ str(self.context.to_lang)
        g_frm = g_frm+'", function(result) { document.forms["f"].translation.value = (result.error)?("Error: "+result.error.message):result.translation; }); } </script>'
        return g_frm


    
    
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}
