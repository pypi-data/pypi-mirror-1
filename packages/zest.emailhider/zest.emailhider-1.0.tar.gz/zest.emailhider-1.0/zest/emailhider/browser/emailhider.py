"""
Define a kss view for the email hider.
"""

from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Products.CMFCore.utils import getToolByName
from zest.emailhider.interfaces import IMailable


class KSSEmailHider(PloneKSSView):
    """kss view for revealing a user's email address"""

    @kssaction
    def reveal_email(self, uid):
        # Collect user using uid
        catalog = getToolByName(self.context, 'uid_catalog')
        brains = catalog(UID=uid)
        if len(brains) != 1:
            return
        user = brains[0].getObject()

        mailable = IMailable(user)
        email = mailable.email
        email_link = u'<a href="mailto:%s">%s</a>' % (email, email)
        core = self.getCommandSet('core')
        core.replaceHTML('.kssattr-uid-' + uid, email_link)
