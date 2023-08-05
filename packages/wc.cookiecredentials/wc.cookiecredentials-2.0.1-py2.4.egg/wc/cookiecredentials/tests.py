import unittest
import transaction
from zope.app.testing.functional import FunctionalDocFileSuite, getRootFolder
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from wc.cookiecredentials.plugin import CookieCredentialsPlugin

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
    return FunctionalDocFileSuite('README.txt',
                                  package='wc.cookiecredentials',
                                  setUp=setUp)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
