from zope.formlib.form import EditForm, Fields
from zope.formlib.namedtemplate import NamedTemplate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('wc.cookiecredentials')
from zope.app.authentication.session import IBrowserFormChallenger

from wc.cookiecredentials.interfaces import ICookieCredentials

class CookieCredentialsEditForm(EditForm):
    form_fields = Fields(ICookieCredentials) + Fields(IBrowserFormChallenger)
    label = _(u"Configure cookie credentials plugin")
