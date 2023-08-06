'''Class: GappsHelper
'''

import gdata.base.service

from OFS.Cache import Cacheable
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, \
            ICredentialsResetPlugin, \
            IUserAdderPlugin, \
            IRoleAssignerPlugin
from Products.PluggableAuthService.utils import classImplements

import interface
import plugins

class GappsHelper(BasePlugin, Cacheable):
    '''Multi-plugin

    '''

    meta_type = 'GApps Authentication Helper'
    security = ClassSecurityInfo()

    def __init__( self, id, title=None ):
        self._setId( id )
        self.title = title

    #
    #   IAuthenticationPlugin implementation
    #
    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):

        """ See IAuthenticationPlugin.

        o We expect the credentials to be those returned by
          ILoginPasswordExtractionPlugin.
        """
        #import pdb;pdb.set_trace()
        login = credentials.get( 'login' )
        password = credentials.get( 'password' )

        if login is None or password is None:
            return None

        ga = gdata.base.service.GBaseService(login, password)
        try:
            ga.ProgrammaticLogin()
            if self._getPAS().getUserById(login) is None:  # user doesn't exist
                self.makeMember(login, password)
	except gdata.service.BadAuthentication, e:
            #print "Authentication error logging in: %s" % e
            return None
    	except Exception, e:
            #print "Error Logging in: %s" % e
            return None

        return login, login

    def makeMember(self, loginname, password):
        """Make a user with id `userId`, and assign him the Member role."""
        # I could just call self._getPAS()._doAddUser(...), but that's private and not part of the IPluggableAuthService interface. It might break someday. So the following is based on PluggableAuthService._doAddUser():
	
        # Make sure we actually have user adders and role assigners. It would be ugly to succeed at making the user but be unable to assign him the role.
        userAdders = self.plugins.listPlugins(IUserAdderPlugin)
        if not userAdders:
            raise NotImplementedError("I wanted to make a new user, but there are no PAS plugins active that can make users.")
        roleAssigners = self.plugins.listPlugins(IRoleAssignerPlugin)
        if not roleAssigners:
            raise NotImplementedError("I wanted to make a new user and give him the Member role, but there are no PAS plugins active that assign roles to users.")

        # Add the user to the first IUserAdderPlugin that works:
        user = None
        for _, curAdder in userAdders:
            if curAdder.doAddUser(loginname, password):  # Assign a dummy password. It'll never be used if you're using apachepas to delegate authentication to Apache.
                user = self._getPAS().getUser(loginname)
                break

        # Map the Member role to the user using all available IRoleAssignerPlugins (just like doAddUser does for some reason):
        for curAssignerId, curAssigner in roleAssigners:
            try:
                curAssigner.doAssignRoleToPrincipal(user.getId(), 'Member')
            except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                logger.debug('RoleAssigner %s error' % curAssignerId, exc_info=True)

classImplements(GappsHelper, interface.IGappsHelper)

InitializeClass( GappsHelper )
