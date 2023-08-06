from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView

class Redirect(BrowserView):
    """Stupid view to redirect to another view.
    
    This is public, but you most POST to it, with a parameter 'to' that has
    the full URL to a page in the current portal. Otherwise, it will fail.
    """
    
    def __call__(self):
        
        portal_state = getMultiAdapter((self.context, self.request), name="plone_portal_state")
        portal_url = portal_state.portal_url()
        to = self.request.form.get('to')
        
        if not to.startswith(portal_url):
            raise ValueError(to)
        
        self.request.response.redirect(self.request.get('to'))
        return ''