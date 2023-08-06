# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from wasp import Notification,Message,status,SendException
from wasp.interfaces import ISendMessage,IProcessResponse
from urllib import quote
from urllib2 import urlopen
from zope.interface import implements
from zope.security.interfaces import Unauthorized

status_mapping = {
    '0':'In progress',
    '1':'Scheduled',
    '11':'Delivered to mobile',
    '22':'Internal fatal error',
    '23':'Authentication failure',
    '24':'Data validation failed',
    '25':'You do not have sufficient credits',
    '26':'Upstream credits not available',
    '27':'You have exceeded your daily quota',
    '28':'Upstream quota exceeded',
    '29':'Message sending cancelled',
    '31':'Unroutable',
    '32':'Blocked',
    '33':'Failed: censored',
    '40':'Temporarily unavailable',
    '50':'Delivery failed',
    '51':'Delivery to phone failed',
    '52':'Delivery to network failed',
    '53':'Message expired',
    '54':'Failed on remote network',
    '56':'Failed: remotely censored',
    '57':'Failed due to fault on handset',
    '64':'Queued for retry after temporary failure delivering, due to fault on handset (transient)',
    '70':'Unknown upstream status',
    }

def get_message(code):
    code=str(code)
    if code not in status_mapping:
        code = '70'
    return '%s: %s'%(code,status_mapping[code])

class SendMessage:

    implements(ISendMessage)

    def __init__(self,username,password,secure=False,want_report=False):
        if secure:
            url = 'https://bulksms.2way.co.za/eapi/submission/send_sms/2/2.0'
        else:
            url = 'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0'
        url += ('?username=%s&password=%s&message=%%s&msisdn=%%s&want_report=%s' % (
            quote(username).replace('%','%%'),
            quote(password).replace('%','%%'),
            want_report and '1' or '0',
            ))
        self.url = str(url)
        
    def __call__(self,msisdn,message_text,message_id=None):
        url = self.url % (
            quote(message_text),
            quote(msisdn),
            )
        if message_id:
            url += ('&source_id='+quote(message_id))
        code,message,batch_id = urlopen(url).read().split('|')
        if code!='0':
            raise SendException(get_message(code))
        return False
    
class ProcessResponse:

    implements(IProcessResponse)

    def __init__(self,incoming_password):
        self.incoming_password = incoming_password
        
    def process(self,request,form,body):
        
        if form.get('pass')!=self.incoming_password:
            raise Unauthorized()

        type = form.get('type')

        if type=='message':
            return (Message(
                form.get('sender','<not supplied>'),
                form.get('message','<not supplied>'),
                ),)
        
        if type=='notification':
            code = form.get('status')
            if code=='11':
                s = status.delivered
            else:
                s = status.failed
            return (Notification(
                form.get('source_id',form.get('msg_id','<not supplied>')),
                s,
                form.get('details',get_message(code)),
                ),)

        raise Exception('Neither message nor notification was specified')

    def response(self):
        return 'done'

