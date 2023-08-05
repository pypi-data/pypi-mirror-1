import os.path
import unittest
import transaction
from zope.app.testing.functional import FunctionalDocFileSuite, getRootFolder
from zope.app.testing.functional import ZCMLLayer
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from wc.cookiecredentials.plugin import CookieCredentialsPlugin

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer')

def setUp(test):
    root = getRootFolder()

    # add and register PAU
    sm = root.getSiteManager()
    pau = sm['pau'] = PluggableAuthentication()
    sm.registerUtility(pau, IAuthentication)

    # add, configure and register cookie credentials plug-in
    cookies = pau['cookies'] = CookieCredentialsPlugin()
    pau.credentialsPlugins = ('cookies',)

    # add and register principal folder authenticator plug-in, create
    # a test principal
    principals = pau['principals'] = PrincipalFolder('wc.test.')
    principals['admin'] = InternalPrincipal('admin', 'secret', 'Administrator')
    pau.authenticatorPlugins = ('principals',)

    # give admin the manager role
    role_manager = IPrincipalRoleManager(root)
    role_manager.assignRoleToPrincipal('zope.Manager', 'wc.test.admin')

    transaction.commit()

def test_suite():
    suite = FunctionalDocFileSuite('README.txt',
                                   package='wc.cookiecredentials',
                                   setUp=setUp)
    suite.layer = FunctionalLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
