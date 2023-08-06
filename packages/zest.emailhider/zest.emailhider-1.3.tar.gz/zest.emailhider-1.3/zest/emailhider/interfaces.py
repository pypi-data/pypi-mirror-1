from zope.interface import Interface, Attribute
from zope import schema


class IMailable(Interface):
    """An object that can provide an email address."""

    uid = Attribute('uid')
    email = Attribute('email')
