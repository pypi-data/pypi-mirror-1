from Acquisition import aq_inner
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.remember.utils import getAdderUtility
from openid.consumer.consumer import SUCCESS
from openid.yadis.discover import DiscoveryFailure
from persistent.list import PersistentList
from plone.openid.plugins.oid import OpenIdPlugin
from random import choice
from zExceptions import Redirect
import AccessControl
import logging
import string
import transaction

manage_addRemOpenIdPlugin = PageTemplateFile("www/remopenidAdd",
                                             globals(),
                                             __name__="manage_addRemOpenIdPlugin")

logger = logging.getLogger("PluggableAuthService")

def addRemOpenIdPlugin(self, id, title='', REQUEST=None):
    """Add Remember-compatible OpenID plugin to a PAS instance."""
    p = RemOpenIdPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=Remember-compatible+OpenID+plugin+added." %
                self.absolute_url())


class RemOpenIdPlugin(OpenIdPlugin):
    """Subclass the default OpenIdPlugin so we can add code to support
    working with Remember member objects."""

    meta_type = "Remember-compatible OpenID plugin"

    def __init__(self, id, title=None):
        super(RemOpenIdPlugin, self).__init__(id, title)
        self._url_username_map = OOBTree()
        self._temp_member_map = OOBTree()

    def _create_member(self, login):
        mdc = getToolByName(self, 'portal_memberdata')
        size = 9
        password = ''.join([choice(string.letters + string.digits
                                   + string.punctuation)
                            for i in range(size)])
        # we create the member obj ourself instead of delegating to
        # the adder utility b/c the utility loses the REQUEST from the
        # acq chain somehow, things go boom... :(
        adder = getAdderUtility(self)
        memtype = adder.default_member_type
        # temporarily escalate privs
        orig_sec_mgr = AccessControl.getSecurityManager()
        app = self.getPhysicalRoot()
        system_user = AccessControl.SpecialUsers.system
        AccessControl.SecurityManagement.newSecurityManager(app, system_user)

        pf = mdc.portal_factory
        mem_folder = pf._getTempFolder(memtype)
        mem = mem_folder.restrictedTraverse(login)
        AccessControl.SecurityManagement.setSecurityManager(orig_sec_mgr)
        return mem
    
    def remember_check(self, credentials):
        """check to see if we have an existing member object, creating
        one if we don't"""
        mbtool = getToolByName(self, 'membrane_tool')
        openid_url = credentials.get('openid.identity')
        login = self._url_username_map.get(openid_url)
        if login:
            mem_brain = mbtool.getUserAuthProvider(login, brain=True)
        else:
            login = self.generateUniqueId('Member')
            mem_brain = None
        if mem_brain is None:
            mem = self._create_member(login)
            self._temp_member_map[login] = openid_url
            response = self.REQUEST.RESPONSE
            response.redirect('%s/complete' % mem.absolute_url())

    def extractOpenIdServerResponse(self, request, creds):
        """Process incoming redirect from an OpenId server.

        The redirect is detected by looking for the openid.mode
        form parameters. If it is found the creds parameter is
        cleared and filled with the found credentials.
        """
        mode=request.form.get("openid.mode", None)
        if mode=="id_res":
            # id_res means 'positive assertion' in OpenID, more commonly
            # described as 'positive authentication'
            creds.clear()
            creds["openid.source"]="server"
            creds["janrain_nonce"]=request.form.get("janrain_nonce")
            for (field,value) in request.form.iteritems():
                if field.startswith("openid.") or field.startswith("openid1_"):
                    creds[field]=request.form[field]
            uuid = request.form.get('uuid')
            if uuid:
                # presence of 'uuid' form field means that we're
                # adding an openid association to an existing member
                # object
                mbtool = getToolByName(self, 'membrane_tool')
                mbrain = mbtool(UID=uuid)
                if mbrain:
                    mbrain = mbrain[0]
                    mem = mbrain.getObject()
                    openid_url = request.form.get('openid.identity')
                    self._url_username_map[openid_url] = mem.getId()
                    if not hasattr(mem, '_openid_urls'):
                        mem._openid_urls = PersistentList([openid_url])
                    elif openid_url not in mem._openid_urls:
                        mem._openid_urls.append(openid_url)
                    plone_utils = getToolByName(self, 'plone_utils')
                    plone_utils.addPortalMessage('OpenID URL set.')
        elif mode=="cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            pass

    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, identity_url, return_to=None):
        consumer=self.getConsumer()
        try:
            auth_request=consumer.begin(identity_url)
        except DiscoveryFailure, e:
            logger.info("openid consumer discovery error for identity %s: %s",
                    identity_url, e[0])
            return
        except KeyError, e:
            logger.info("openid consumer error for identity %s: %s",
                    identity_url, e.why)
            pass
            
        if return_to is None:
            return_to=self.REQUEST.form.get("came_from", None)
        if not return_to or 'janrain_nonce' in return_to:
            # The conditional on janrain_nonce here is to handle the case where
            # the user logs in, logs out, and logs in again in succession.  We
            # were ending up with duplicate open ID variables on the second response
            # from the OpenID provider, which was breaking the second login.
            return_to=self.getTrustRoot()

        uuid = self.REQUEST.form.get('uuid')
        if uuid:
            auth_request.return_to_args['uuid'] = uuid
        url=auth_request.redirectURL(self.getTrustRoot(), return_to)

        # There is evilness here: we can not use a normal RESPONSE.redirect
        # since further processing of the request will happily overwrite
        # our redirect. So instead we raise a Redirect exception, However
        # raising an exception aborts all transactions, which means our
        # session changes are not stored. So we do a commit ourselves to
        # get things working.
        # XXX this also f**ks up ZopeTestCase
        transaction.commit()
        raise Redirect, url

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.has_key("openid.source"):
            return None

        if credentials["openid.source"]=="server":
            consumer=self.getConsumer()
            
            # remove the extractor key that PAS adds to the credentials,
            # or python-openid will complain
            query = credentials.copy()
            del query['extractor']
            
            result=consumer.complete(query, self.REQUEST.ACTUAL_URL)
            identity=result.identity_url
            
            if result.status==SUCCESS:
                self._getPAS().updateCredentials(self.REQUEST,
                        self.REQUEST.RESPONSE, identity, "")
                # do the Remember-compatibility stuff
                self.remember_check(credentials)
                username = self._url_username_map.get(identity, identity)
                return (username, identity)
            else:
                logger.info("OpenId Authentication for %s failed: %s",
                                identity, result.message)

        return None

    # IUserEnumerationPlugin implementation
    def enumerateUsers(self, id=None, login=None, exact_match=False,
            sort_by=None, max_results=None, **kw):
        """Sneaky and maybe a little evil.. delegate to the membrane
        user manager"""
        # the 'login' we have at this point is the OpenID URL, so we
        # need to convert that to the username
        login = self._url_username_map.get(login, login)
        mb_user_mgr = aq_inner(self.membrane_users)
        return mb_user_mgr.enumerateUsers(id=id, login=login,
                                          exact_match=exact_match,
                                          sort_by=sort_by,
                                          max_results=max_results,
                                          **kw)
