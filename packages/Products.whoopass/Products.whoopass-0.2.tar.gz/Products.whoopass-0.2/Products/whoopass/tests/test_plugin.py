import unittest

from Products.PluggableAuthService.tests.conformance import \
    IExtractionPlugin_conformance
from Products.PluggableAuthService.tests.conformance import \
    IAuthenticationPlugin_conformance
from Products.PluggableAuthService.tests.conformance import \
    IGroupsPlugin_conformance
from Products.PluggableAuthService.tests.conformance import \
    IRolesPlugin_conformance

class WhoPluginTests(unittest.TestCase,
                     IExtractionPlugin_conformance,
                     IAuthenticationPlugin_conformance,
                     IGroupsPlugin_conformance,
                     IRolesPlugin_conformance,
                    ):

    def _getTargetClass(self):
        from Products.whoopass.plugin import WhoPlugin
        return WhoPlugin

    def _makeOne(self, id='whoopass'):
        return self._getTargetClass()(id)

    def _makeRequest(self, userid=None, groups=None, roles=None, **kw):

        class DummyRequest:
            pass

        environ = {}
        if userid is not None:
            identity = kw.copy()
            identity['repoze.who.userid'] = userid
            if groups is not None:
                identity['groups'] = groups
            if roles is not None:
                identity['roles'] = roles
            environ['repoze.who.identity'] = identity

        request = DummyRequest()
        request.environ = environ
        return request

    def test_IPropertiesPlugin_conformance( self ):
        from zope.interface.verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IPropertiesPlugin

        verifyClass(IPropertiesPlugin, self._getTargetClass())

    def test_IPropertiesPlugin_listInterfaces(self):
        from Products.PluggableAuthService.interfaces.plugins \
            import IPropertiesPlugin

        listed = self._makeOne().listInterfaces()
        self.failUnless(IPropertiesPlugin.__name__ in listed)

    def test_extractCredentials_no_who(self):
        plugin = self._makeOne()
        request = self._makeRequest()
        credentials = plugin.extractCredentials(request)
        self.assertEqual(credentials, {})

    def test_extractCredentials_with_who(self):
        plugin = self._makeOne()
        request = self._makeRequest('phred')
        credentials = plugin.extractCredentials(request)
        self.assertEqual(credentials, {'repoze.who.userid': 'phred'})

    def test_authenticateCredentials_no_who(self):
        plugin = self._makeOne()
        credentials = {}
        self.assertEqual(plugin.authenticateCredentials(credentials), None)

    def test_authenticateCredentials_with_who(self):
        plugin = self._makeOne()
        credentials = {'repoze.who.userid': 'phred'}
        self.assertEqual(plugin.authenticateCredentials(credentials),
                         ('phred', 'phred'))

    def test_authenticateCredentials_with_who_and_login(self):
        plugin = self._makeOne()
        credentials = {'repoze.who.userid': 'phred',
                       'login': 'phred@example.com',
                      }
        self.assertEqual(plugin.authenticateCredentials(credentials),
                         ('phred', 'phred@example.com'))

    def test_getPropertiesForUser_no_request(self):
        plugin = self._makeOne()
        user = object()
        self.assertEqual(plugin.getPropertiesForUser(user), {})

    def test_getPropertiesForUser_no_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest()
        self.assertEqual(plugin.getPropertiesForUser(user, request), {})

    def test_getPropertiesForUser_with_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest('phred', hobbies='Beer drinking')
        self.assertEqual(plugin.getPropertiesForUser(user, request),
                        {'hobbies': 'Beer drinking'})

    def test_getPropertiesForUser_with_who_skips_groups_and_roles(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest('phred',
                                    groups=('Old Farts', 'Lazy Bastards'),
                                    roles=('Curmudgeon',),
                                    hobbies='Beer drinking',
                                   )
        self.assertEqual(plugin.getPropertiesForUser(user, request),
                        {'hobbies': 'Beer drinking'})

    def test_getGroupsForPrincipal_no_request(self):
        plugin = self._makeOne()
        user = object()
        self.assertEqual(plugin.getGroupsForPrincipal(user), ())

    def test_getGroupsForPrincipal_no_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest()
        self.assertEqual(plugin.getGroupsForPrincipal(user, request), ())

    def test_getGroupsForPrincipal_with_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest('phred',
                                    groups=('Old Farts', 'Lazy Bastards'),
                                    roles=('Curmudgeon',),
                                    hobbies='Beer drinking',
                                   )
        self.assertEqual(plugin.getGroupsForPrincipal(user, request),
                         ('Old Farts', 'Lazy Bastards'))

    def test_getRolesForPrincipal_no_request(self):
        plugin = self._makeOne()
        user = object()
        self.assertEqual(plugin.getRolesForPrincipal(user), ())

    def test_getRolesForPrincipal_no_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest()
        self.assertEqual(plugin.getRolesForPrincipal(user, request), ())

    def test_getRolesForPrincipal_with_who(self):
        plugin = self._makeOne()
        user = object()
        request = self._makeRequest('phred',
                                    groups=('Old Farts', 'Lazy Bastards'),
                                    roles=('Curmudgeon',),
                                    hobbies='Beer drinking',
                                   )
        self.assertEqual(plugin.getRolesForPrincipal(user, request),
                         ('Curmudgeon',))
