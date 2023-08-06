import logging
import threading
import ad
import ldap.filter
from AccessControl.SecurityInfo import ClassSecurityInfo
from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PlonePAS.interfaces.capabilities import IPasswordSetCapability
from Products.PlonePAS.interfaces.plugins import IUserManagement

log = logging.getLogger(__file__)
AdAccessLock = threading.Lock()

manage_addADPasswordChangePlugin = PageTemplateFile("templates/addAdPlugin",
        globals(), __name__="manage_addADPasswordChangePlugin")


def addADPasswordChangePlugin(self, id, title="", domain=None,
        login_user=None, login_password=None, userid_attribute=None,
        login_attribute=None, REQUEST=None):
    """Add an ADPasswordChangePlugin to a PAS."""
    p=ADPasswordChangePlugin(id, title)
    p.domain=domain
    p.login_user=login_user
    p.login_password=login_password
    p.userid_attribute=userid_attribute
    p.login_attribute=login_attribute
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST.response.redirect("%s/manage_workspace"
                "?manage_tabs_message=AD+Password+Changing+plugin+added." %
                self.absolute_url())


class ADPasswordChangePlugin(BasePlugin):
    meta_type = "AD Password Changing"
    security = ClassSecurityInfo()

    implements(IPasswordSetCapability, IUserManagement)

    _properties = (
            dict(id    = "domain",
                 label = "AD domain name",
                 type  = "string",
                 mode  = "w"),
            dict(id    = "login_user",
                 label = "User to access AD",
                 type  = "string",
                 mode  = "w"),
            dict(id    = "login_password",
                 label = "Password to access AD",
                 type  = "string",
                 mode  = "w"),
            dict(id    = "userid_attribute",
                 label = "AD/LDAP attribute for user id",
                 type  = "selection",
                 select_variable = "ad_attributes",
                 mode  = "w"),
            dict(id    = "login_attribute",
                 label = "AD/LDAP attribute for login name",
                 type  = "selection",
                 select_variable = "ad_attributes",
                 mode  = "w"),
            )

    ad_attributes = [ "sAMAccountName", "userPrincipalName" ]

    domain = ""
    login_user = ""
    userid_attribute = "sAMAccountName"
    login_attribute = "sAMAccountName"

    ldap_filter = "(&(objectClass=user)" \
                    "(userAccountControl:1.2.840.113556.1.4.803:=%s))" % \
                    ad.AD_USERCTRL_NORMAL_ACCOUNT
                

    def __init__(self, id, title=None, domain=None,
                 login_user=None, login_password=None):
        self._setId(id)
        self.title=title
        self.domain=domain
        self.login_user=login_user
        self.login_password=login_password


    def _getAdClient(self):
        """Return a valid AD Client instance. This method MUST be called with
        AdAccessLock held."""
        creds=getattr(self, "_v_creds", None)
        if creds is None:
            self._v_creds=ad.Creds(self.domain)
            self._v_creds.acquire(self.login_user, self.login_password)
            ad.activate(self._v_creds)
        client=getattr(self, "_v_clients", None)
        if client is None:
            self._v_client=client=ad.Client(self.domain)
        return client



    def _getUserInfo(self, user_id=None, login=None):
        """Get the user information for a Plone user_id. Returns a tuple
        with the DN and a dictionary with all user information.
        """
        if not (user_id or login):
            raise ValueError("Need either user_id or login")
        filters=[self.ldap_filter]
        if user_id:
            filters.append("(%s=%s)" % (self.userid_attribute,
                                 ldap.filter.escape_filter_chars(user_id)))
        if login:
            filters.append("(%s=%s)" % (self.login_attribute,
                                 ldap.filter.escape_filter_chars(login)))
        filter="(&%s)" % "".join(filters)

        AdAccessLock.acquire()
        try:
            client=self._getAdClient()
            users=client.search(filter=filter)
        finally:
            AdAccessLock.release()

        if users:
            return users[0]

    

    def setPrincipalPassword(self, principal, password):
        AdAccessLock.acquire()
        try:
            client=self._getAdClient()
            client.set_password(principal, password)
        finally:
            AdAccessLock.release()


    # IPasswordSetCapability
    def allowPasswordSet(self, id):
        try:
            return self._getUserInfo(user_id=id) is not None
        except (ad.Error, ad.LDAPError), e:
            log.exception("Active Directory error searching for users")
            return False


    # IUserManagement
    def doChangeUser(self, login, password, **kw):
        try:
            info=self._getUserInfo(login=login)
            if info is None:
                raise KeyError("Unknown login name: %s" % login)
            self.setPrincipalPassword(info[1]["userPrincipalName"][0], password)
            return True
        except (ad.Error, ad.LDAPError), e:
            log.exception("Active Directory error changing a user password")


    def doDeleteUser(self, login):
        return False

