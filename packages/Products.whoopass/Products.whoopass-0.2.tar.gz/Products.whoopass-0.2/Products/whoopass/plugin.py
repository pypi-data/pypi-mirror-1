from AccessControl import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces import plugins as pluginifaces

_NON_PROPERTY_IDENTITY_KEYS = ('repoze.who.userid', 'groups', 'roles')

class WhoPlugin(SimpleItem, BasePlugin):
    """ PAS multi-plugin for use with repoze.who

    o This plugin relies on the contract that when repoze.who authenticates
      a user, it leaves a mapping in the environment under the key,
      'repoze.who.identity'.  That mapping *must* include a key,
      'repoze.who.userid', which contains the authenticated user's ID.

      In addition, the mapping may contain other metadata about the user.
      This plugin splits any 'groups' or 'roles' out, along with the
      actual identity, and treats the others as properties.
    """
    meta_type = "Who Plugin"

    manage_options = BasePlugin.manage_options + SimpleItem.manage_options

    implements(pluginifaces.IExtractionPlugin,
               pluginifaces.IAuthenticationPlugin,
               pluginifaces.IPropertiesPlugin,
               pluginifaces.IGroupsPlugin,
               pluginifaces.IRolesPlugin,
              )

    security = ClassSecurityInfo()

    def __init__(self, id):
        self._setId(id)

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ See IExtractionPlugin.
        """
        return request.environ.get('repoze.who.identity', {})

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """ See IAuthenticationPlugin.
        """
        userid = credentials.get('repoze.who.userid')
        if userid:
            username = credentials.get('login', userid)
            return userid, username

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin.
        """
        identity = self._getIdentityFromRequest(request)
        return dict([(key, value) for key, value in identity.items()
                            if key not in _NON_PROPERTY_IDENTITY_KEYS])

    security.declarePrivate('getGroupsForPrincipal')
    def getGroupsForPrincipal(self, principal, request=None):
        """ See IGroupsPlugin.
        """
        identity = self._getIdentityFromRequest(request)
        return identity.get('groups', ())

    security.declarePrivate('getRolesForPrincipal')
    def getRolesForPrincipal(self, principal, request=None):
        """ See IRolesPlugin.
        """
        identity = self._getIdentityFromRequest(request)
        return identity.get('roles', ())

    security.declarePrivate('_getIdentityFromRequest')
    def _getIdentityFromRequest(self, request):
        if request is not None:
            return request.environ.get('repoze.who.identity', {})
        return {}
    

InitializeClass(WhoPlugin)

manage_addWhoPluginForm = PageTemplateFile('www/addWhoPluginForm.pt',
                                           globals(),
                                           _name__='manage_addWhoPluginForm')

def manage_addWhoPlugin(container, id, REQUEST=None):
    """ Add plugin to container (should be a PAS).
    """
    plugin = WhoPlugin(id)
    container._setObject(plugin.getId(), plugin)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'Who+Plugin+added.'
                                    % container.absolute_url() )
