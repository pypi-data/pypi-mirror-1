from zope.interface import Interface
from zope.schema import ASCIILine
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('wc.cookiecredentials')

class ICookieCredentials(Interface):

    cookie_name = ASCIILine(
        title=_(u'Cookie name'),
        description=_(u'Name of the cookie for storing credentials.'),
        required=True
        )
