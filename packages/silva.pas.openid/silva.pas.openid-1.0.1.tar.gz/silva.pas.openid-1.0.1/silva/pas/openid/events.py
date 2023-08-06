# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: events.py 28282 2008-04-09 15:37:13Z sylvain $

from zope.interface import Interface, Attribute, implements


class IOpenIDResult(Interface):
    """Event triggered when a OpenID Result occurs.
    """

    object = Attribute("Originate plugin")
    result = Attribute("Result of the OpenID request")

class IOpenIDResultSuccess(IOpenIDResult):
    """The OpenID result was a success.
    """

    userid = Attribute("UserID")


class OpenIDResult(object):
    implements(IOpenIDResult)

    def __init__(self, plugin, result):
        self.object = plugin
        self.result = result


class OpenIDResultSuccess(OpenIDResult):
    
    implements(IOpenIDResultSuccess)

    def __init__(self, plugin, result, userid):
        super(OpenIDResultSuccess, self).__init__(plugin, result)
        self.userid = userid


class IOpenIDResultCancel(IOpenIDResult):
    """The OpenID result was a cancel
    """

class OpenIDResultCancel(OpenIDResult):
    
    implements(IOpenIDResultCancel)

