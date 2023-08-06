# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: SilvaOpenIDMember.py 28288 2008-04-10 09:34:17Z sylvain $

from zope.interface import implements
from zope.component import getUtility

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
import DateTime

from Products.Silva.SimpleMembership import SimpleMember
from Products.Silva.helpers import add_and_edit
from Products.Silva import SilvaPermissions

from silva.pas.base.interfaces import IUserConverter
from interfaces import IOpenIDMember

class SilvaOpenIDMember(SimpleMember):

    implements(IOpenIDMember)

    meta_type = 'Silva OpenID Member'
    security = ClassSecurityInfo()


    manage_options = ({'label': 'Details',
                       'action': 'manage_details',
                       },) + SimpleMember.manage_options

    def __init__(self, identity_url, id):
        super(SilvaOpenIDMember, self).__init__(id)
        self.identity_url = identity_url
        self.application_date = DateTime.DateTime()
        self.fully_registered = False
        self.last_login_date = None


    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
                              'manage_details')
    manage_details = PageTemplateFile(
        "www/openIDMemberDetails", globals(),
        __name__='manage_details')

    manage_main = manage_details


Globals.InitializeClass(SilvaOpenIDMember)

manage_addOpenIDMemberForm = PageTemplateFile(
    "www/openIDMemberAdd", globals(),
    __name__='manage_addOpenIDMemberForm')

def manage_addOpenIDMember(self, identity_url, REQUEST=None):
    """Add a OpenID Member.
    """
    utility = getUtility(IUserConverter, name="openid")
    converter = utility()
    userid = converter.convert(identity_url)

    object = SilvaOpenIDMember(identity_url, userid)
    self._setObject(userid, object)
    object.sec_assign(userid, 'ChiefEditor')
    add_and_edit(self, userid, REQUEST)
    return ''
