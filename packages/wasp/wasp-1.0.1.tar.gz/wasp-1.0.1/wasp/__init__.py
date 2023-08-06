# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from interfaces import ISendMessage,IReceiveMessage,INotifyMessage,IProcessResponse
from zope.component import getUtility,queryAdapter
from zope.publisher.browser import BrowserView

def send(msisdn,message_text,message_id=None):
    return getUtility(ISendMessage)(msisdn,message_text,message_id)

class Receiver(BrowserView):

    def __call__(self):
        # we have to use duck typing here because Zope 2
        # requests lie about implementing interfaces :-(
        bodyStream = getattr(self.request,'bodyStream',None)
        if bodyStream is None:
            # zope 2
            body = self.request.get('BODY','')
        else:
            # zope 3
            body = self.request.bodyStream.read()
        # despatch to IProcessResponse utility and handle returned events
        utility = getUtility(IProcessResponse)
        for event in utility.process(self.request,self.request.form,body):
            adapter = queryAdapter(self.context,event.interface)
            if adapter is not None:
                adapter(**event.__dict__)
            else:
                getUtility(event.interface)(**event.__dict__)
        return utility.response()

class Notification:
    """
    A notification object used to dispatch notifications from an
    IProcessResponse utility to INotifyMessage utilities or adapters.

    message_id - the message_id passed to the `send` method

    status - one of the statuses in wasp.status

    details - a string giving more information about why the status
              was returned. In the case of errors, this should contain
              the full error message returned from the WASP.
              If the status is wasp.status.Delivered then this may be
              an empty string.
    """
                          
    interface = INotifyMessage
                          
    def __init__(self,message_id,status,details):
        self.message_id = message_id
        self.status = status
        self.details = details

class Message:
    """
    A message object used to dispatch messages recieved by an
    IProcessResponse utility to IRecieveMessage utilities or adapters.

    msisdn - the msisdn the message was recieved to

    message_text - the text of the recieved message.
    """

    interface = IReceiveMessage
                          
    def __init__(self,msisdn,message_text):
        self.msisdn = msisdn
        self.message_text = message_text

class SendException(Exception):
    """
    An exception to raise from within an ISendMessage implementation's
    __call__ method when something goes wrong.
    """
