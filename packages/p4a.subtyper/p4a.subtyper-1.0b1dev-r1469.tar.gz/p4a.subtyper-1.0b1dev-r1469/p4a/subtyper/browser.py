import urllib
import zope.interface
import zope.component
from p4a.subtyper import interfaces
from p4a.subtyper import utils
import Products.Five.browser

class ISubtyperView(zope.interface.Interface):
    def possible_types(): pass 
    def has_possible_types(): pass
    def change_type(): pass

class SubtyperView(Products.Five.browser.BrowserView):
    """View for introspecting and possibly changing subtype info for the
    current context.
    """

    zope.interface.implements(ISubtyperView)

    def possible_types(self):
        subtyper = zope.component.getUtility(interfaces.ISubtyper)
        return subtyper.possible_types(self.context)

    def has_possible_types(self):
        return len(self.possible_types()) > 0

    def _redirect(self, msg):
        url = self.context.absolute_url()
        self.request.response.redirect(url + '?portal_status_message=' + \
                                       urllib.quote(msg))
        return ''

    def change_type(self):
        """Change the sub type of the current context.
        """

        subtyper = zope.component.getUtility(interfaces.ISubtyper)

        subtype_name = self.request.get('subtype', None)
        if subtype_name:
            subtype = subtyper.get_named_type(subtype_name)
            subtyper.change_type(self.context, subtype_name)
            msg = 'Changed subtype to %s' % subtype.title
        else:
            msg = 'No subtype specified'

        return self._redirect(msg)
