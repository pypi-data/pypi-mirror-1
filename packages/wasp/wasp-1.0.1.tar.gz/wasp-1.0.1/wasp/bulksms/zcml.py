# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from wasp.bulksms import SendMessage, ProcessResponse
from wasp.interfaces import ISendMessage,IProcessResponse
from zope.component.zcml import utility
from zope.configuration.fields import Bool
from zope.interface import Interface
from zope.schema import Text

class SenderDirective(Interface):
    """Setup a BulkSMS ISendMessage utility."""

    username = Text(
        title=u"Username",
        description=u"The username sent to BulkSMS",
        )

    password = Text(
        title=u"Password",
        description=u"The password sent to BulkSMS",
        )

    secure = Bool(
        title=u"Use secure connection",
        description=u"Configures whether an HTTP or HTTPS connection is used when contacting BulkSMS",
        required=False
        )

    want_report = Bool(
        title=u"Ask BulkSMS to send reports",
        description=u"Configures whether or not reports will be requested when sending messages",
        required=False
        )

class ProcessorDirective(Interface):
    """Setup a BulkSMS IProcessResponse utility."""

    incoming_password = Text(
        title=u"Password for BulkSMS requests",
        description=u"Configures whether the SendMessage utility will return True or False when called",
        )

def setupISendMessageUtility(_context,username,password,**kw):
    u = SendMessage(username,password,**kw)
    utility(_context, ISendMessage, u)

def setupIProcessResponseUtility(_context,incoming_password):
    u = ProcessResponse(incoming_password)
    utility(_context, IProcessResponse, u)
