# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from wasp.demo import SendMessage
from wasp.interfaces import ISendMessage
from zope.component.zcml import utility
from zope.configuration.fields import Bool
from zope.interface import Interface

class ISenderDirective(Interface):
    """Setup a demo SendMessage utility."""

    response = Bool(
        title=u"Return value",
        description=u"Configures whether the SendMessage utility will return True or False when called",
        required=False
        )

def setupUtility(_context,response=None):
    kw = {}
    if response is not None:
        kw['response']=response
    sender = SendMessage(**kw)
    utility(_context, ISendMessage, sender)
