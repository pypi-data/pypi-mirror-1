from Products.Five import BrowserView
from zope.app.component.hooks import getSite

class ListenUtils(BrowserView):
    """utility methods that are shared across templates"""

    def mailinglist(self):
        """ mailinglists are local site managers, so we can call getSite to get
        a reference to them """
        return getSite()

    def mailinglist_url(self):
        return self.mailinglist().absolute_url()
