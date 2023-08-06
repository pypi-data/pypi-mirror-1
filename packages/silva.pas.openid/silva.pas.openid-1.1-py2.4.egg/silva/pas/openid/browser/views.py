# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: views.py 28977 2008-06-03 15:45:54Z sylvain $

from zope.component import getMultiAdapter

from silva.pas.openid.interfaces import IOpenIDAskUserInformation

from Products.Five import BrowserView
from Products.Silva.i18n import translate as _

from zExceptions import Redirect
from urllib import quote

class StartOpenIDRegistration(BrowserView):

    def _redirect(self, msg):
        root = self.context.get_root()
        args = (root.absolute_url(), quote(msg))
        next_url = '%s/silva_openid_register.html?openid_status=%s' % args
        raise Redirect, next_url

    def __call__(self):
        """Register a new user to use OpenID.
        """

        root = self.context.get_root()

        id = self.request.form.get('__ac_identity_register', '').strip()
        if not id:
            self._redirect(_(u"You need to provide an identity."))
            
        captcha = self.request.form.get('__ac_identity_register_captcha', None)
        if not captcha:
            self._redirect(_(u"You need to fill the captcha."))

        utility = getMultiAdapter((self.context, self.request), name='captcha')
        if not utility.verify(captcha):
            self._redirect(_(u"Error while validating the captcha."))


        self.request.form['__ac_identity_url'] = id # Re-inject the id

        smembers = root.service_members

        if smembers.is_user(id):
            # Authenticate
            # direct lookup ?
            root.acl_users.validate(self.request)
            # We should never be here.
            return

        members = root.Members
        members.manage_addProduct['silva.pas.openid'].manage_addOpenIDMember(id)

        provider = IOpenIDAskUserInformation(self.request)
        provider.require('email')
        provider.optional('nickname')
        provider.optional('fullname')

        # Add some roles ?

        root.acl_users.validate(self.request)
        # We should never be here.


        


