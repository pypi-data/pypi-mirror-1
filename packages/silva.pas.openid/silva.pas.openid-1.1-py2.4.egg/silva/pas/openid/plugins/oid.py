# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: oid.py 28290 2008-04-10 09:57:16Z sylvain $

# Zope 2
from Acquisition import aq_parent
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zExceptions import Redirect
import transaction

# Zope 3
from zope.component import getUtility
from zope.component.event import objectEventNotify

# PAS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin

# Silva
from silva.pas.openid.interfaces import *
from silva.pas.base.interfaces import IUserConverter
from silva.pas.openid.store import ZopeStore
from silva.pas.openid.events import *

# OpenID
from openid.yadis.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, SUCCESS

# Python
import logging
import urlparse

manage_addOpenIDPluginForm = PageTemplateFile("../www/openIDAddForm", 
                globals(), __name__="manage_addOpenIDPluginForm")

logger = logging.getLogger("PluggableAuthService")

def manage_addOpenIDPlugin(self, id, title='', REQUEST=None):
    """Add a OpenID plugin to a Pluggable Authentication Service.
    """
    plugin = OpenIdPlugin(id, title)
    self._setObject(plugin.getId(), plugin)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=OpenID+plugin+added." %
                self.absolute_url())


class OpenIdPlugin(BasePlugin):
    """OpenID authentication plugin.
    """

    meta_type = "OpenID plugin"
    security = ClassSecurityInfo()

    _properties = BasePlugin._properties + ({'id': 'policy_url',
                                             'type': 'string',
                                             'mode': 'w',
                                             'label': 'Policy URL',
                                             },)

    policy_url = ''

    def __init__(self, id, title=None):
        self._setId(id)
        self.title=title
        self.store=ZopeStore()


    def getTrustRoot(self):
        pas=self._getPAS()
        site=aq_parent(pas)
        return site.absolute_url()


    def getConsumer(self):
        session=self.REQUEST["SESSION"]
        return Consumer(session, self.store)


    def extractOpenIdServerResponse(self, request, creds):
        """Process incoming redirect from an OpenId server.

        The redirect is detected by looking for the openid.mode
        form parameters. If it is found the creds parameter is
        cleared and filled with the found credentials.
        """

        mode = request.form.get("openid.mode", None)
        if mode == "id_res":
            # id_res means 'positive assertion' in OpenID, more commonly
            # describes as 'positive authentication'
            creds["openid.creds"] = request.form.copy()
        elif mode == "cancel":
            # cancel is a negative assertion in the OpenID protocol,
            # which means the user did not authorize correctly.
            objectEventNotify(OpenIDResultCancel(self, None, None))


    # IOpenIdExtractionPlugin implementation
    def initiateChallenge(self, identity_url, return_to=None):
        consumer = self.getConsumer()
        try:
            result = consumer.begin(identity_url)
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
        if not return_to:
            return_to=self.getTrustRoot()
        self.REQUEST["SESSION"]['return_to'] = return_to

        if self.policy_url:
            result.addExtensionArg('sreg', 'policy_url', self.policy_url)

        extra = IOpenIDAskedUserInformation(self.REQUEST)
        if extra.require():
            result.addExtensionArg('sreg', 
                                   'required', 
                                   ','.join(extra.require()))
        if extra.optional():
            result.addExtensionArg('sreg', 
                                   'optional', 
                                   ','.join(extra.optional()))

        url = result.redirectURL(self.getTrustRoot(), return_to)

        # There is evilness here: we can not use a normal RESPONSE.redirect
        # since further processing of the request will happily overwrite
        # our redirect. So instead we raise a Redirect exception, However
        # raising an exception aborts all transactions, which means are
        # session changes are not stored. So we do a commit ourselves to
        # get things working.
        # XXX this also f**ks up ZopeTestCase
        transaction.commit()
        raise Redirect, url


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        """This method performs the PAS credential extraction.

        It takes either the zope cookie and extracts openid credentials
        from it, or a redirect from a OpenID server.
        """
        creds = {}
        identity = request.form.get("__ac_identity_url", '').strip()
        if identity:
            self.initiateChallenge(identity)
            return creds

        self.extractOpenIdServerResponse(request, creds)
        return creds


    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.has_key("openid.creds"):
            return None
        real_creds = credentials["openid.creds"]
        if real_creds:
            consumer = self.getConsumer()
            result = consumer.complete(real_creds,
                                       self.REQUEST["SESSION"]['return_to'])
            userid = self._identityToId(result.identity_url)

            if result.status==SUCCESS:
                pas = self._getPAS()
                pas.updateCredentials(self.REQUEST,
                                      self.REQUEST.RESPONSE, 
                                      userid, 
                                      "")

                objectEventNotify(OpenIDResultSuccess(self, result, userid))
                return (userid, result.identity_url)
            else:
                logger.info("OpenId Authentication for %s failed: %s",
                            result.identity_url, result.message)
                objectEventNotify(OpenIDResultCancel(self, result, userid))

        return None

    def _identityToId(self, identity):
        utility = getUtility(IUserConverter, name="openid")
        converter = utility()
        return converter.convert(identity)


classImplements(OpenIdPlugin, IOpenIdExtractionPlugin, IAuthenticationPlugin)


