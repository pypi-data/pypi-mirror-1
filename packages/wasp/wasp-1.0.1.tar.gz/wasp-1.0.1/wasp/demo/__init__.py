# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from wasp import Notification,Message,status
from wasp.interfaces import ISendMessage,IProcessResponse,INotifyMessage,IReceiveMessage
from zope.interface import implements

class SendMessage:

    implements(ISendMessage)

    def __init__(self,response=True):
        self.response = response
        
    def __call__(self,msisdn,message_text,message_id=None):
        print "Send to:",repr(msisdn)
        print "Message:",repr(message_text)
        print "     Id:",repr(message_id)
        return self.response
    
class EchoMessage:

    implements(IReceiveMessage)
    
    def __call__(self,msisdn,message_text):
        print "      msisdn:",repr(msisdn)
        print "message_text:",repr(message_text)

class EchoNotification:

    implements(INotifyMessage)
    
    def __call__(self,message_id,status,details):
        print "message_id:",repr(message_id)
        print "    status:",repr(status)
        print "   details:",repr(details)
        
class ProcessResponse:

    implements(IProcessResponse)
    
    def process(self,request,form,body):
        if form.get('type')=='message':
            yield Message(
                form.get('msisdn','<not supplied>'),
                form.get('message_text','<not supplied>'),
                )
        if form.get('type')=='notification':
            s = getattr(status,form.get('status','delivered'),status.delivered)
            yield Notification(
                form.get('message_id','<not supplied>'),
                s,
                form.get('details','<not supplied>'),
                )

    def response(self):
        return 'done'

class EchoResponse:

    implements(IProcessResponse)
    
    def process(self,request,form,body):
        print 'method:',request.method
        print '  form:',form
        print '  body:',repr(body)
        return ()
        
    def response(self):
        return 'done'
