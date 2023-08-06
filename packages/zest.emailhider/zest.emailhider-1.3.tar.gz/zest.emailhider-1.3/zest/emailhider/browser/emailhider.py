"""
Define a kss view for the email hider.
"""

from zope.component import getMultiAdapter
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Products.CMFCore.utils import getToolByName
from zest.emailhider.interfaces import IMailable


class KSSEmailHider(PloneKSSView):
    """kss view for revealing a user's email address"""

    @kssaction
    def reveal_email(self, uid):
        # Collect user using uid
        if not uid:
            return
        if uid == 'email_from_address':
            portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
            portal = portal_state.portal()
            email = portal.getProperty('email_from_address')
        else:
            catalog = getToolByName(self.context, 'uid_catalog')
            brains = catalog(UID=uid)
            if len(brains) != 1:
                return
            target = brains[0].getObject()
            mailable = IMailable(target, None)
            if mailable is None:
                return
            email = mailable.email
        email_link = u'<a href="mailto:%s">%s</a>' % (email, email)
        core = self.getCommandSet('core')
        core.replaceHTML('.kssattr-uid-' + uid, email_link)
