# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os.path
import sys
import urllib2
import wasp.bulksms

from StringIO import StringIO
from unittest import TestCase,TestSuite,makeSuite
from wasp import Message,Notification,status,SendException
from wasp.interfaces import ISendMessage
from wasp.bulksms import SendMessage,ProcessResponse
from wasp.tests import BaseSendTests, BaseProcessResponse, setUp, FunctionalLayer
from zope.app.appsetup.appsetup import getConfigContext
from zope.app.testing.functional import ZCMLLayer
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.component import getUtility
from zope.component.testing import tearDown as componentTearDown
from zope.configuration import xmlconfig
from zope.security.interfaces import Unauthorized
from zope.testing import doctest

class Response(StringIO):

    def __init__(self,parent,url,data,response):
        StringIO.__init__(self,response)
        self.url = url
        self.data = data
        self.parent = parent

    def read(self):
        if self.parent:
            self.parent.opened = self.url
        else:
            print 'opened:',repr(self.url)
        if self.data:
            if self.parent:
                self.parent.data = self.data
            else:
                print 'data:',repr(self.data)
        return StringIO.read(self)
        
class TestOpenerDirector:

    response = ''
    opened = ''
    data = ''
    
    def __init__(self,store=False):
        self.store = store

    def open(self,fullurl,data=None):
        return Response(self.store and self,
                        fullurl,data,self.response)
    
    def set_response(self,response):
        self.response = response
        
class SendTests(BaseSendTests):

    klass = SendMessage

    response = False
    
    def setUp(self):
        self.u = self.klass('testusername','testpassword')
        self.opener = TestOpenerDirector(store=True)
        self.original_opener = urllib2._opener
        urllib2.install_opener(self.opener)
        self.opener.set_response('0|IN_PROGRESS|71070172')

    def tearDown(self):
        urllib2.install_opener(self.original_opener)
        
    def test_send(self):
        self.assertEqual(self.u('123','test message','456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message&msisdn=123&want_report=0&source_id=456'
            )

    def test_send_no_id(self):
        self.assertEqual(self.u('123','test message'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message&msisdn=123&want_report=0'
            )

    def test_error_on_send(self):
        self.opener.set_response('22|INTERNAL_FATAL_ERROR|71070172')
        self.assertRaises(SendException,self.u,'123','test message')
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message&msisdn=123&want_report=0'
            )
        
    def test_secure(self):
        self.u = self.klass('testusername','testpassword',secure=True)
        self.assertEqual(self.u('123','test message'),self.response)
        self.assertEqual(
            self.opener.opened,
            'https://bulksms.2way.co.za/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message&msisdn=123&want_report=0'
            )
        
    def test_want_report(self):
        self.u = self.klass('testusername','testpassword',want_report=True)
        self.assertEqual(self.u('123','test message'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message&msisdn=123&want_report=1'
            )

    def test_quote_msisdn(self):
        self.assertEqual(self.u('1%3','message','456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=message&msisdn=1%253&want_report=0&source_id=456'
            )

    def test_quote_message(self):
        self.assertEqual(self.u('123','test message &fail=1','456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=test%20message%20%26fail%3D1&msisdn=123&want_report=0&source_id=456'
            )

    def test_quote_message_id(self):
        self.assertEqual(self.u('123','message','%456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=testpassword&message=message&msisdn=123&want_report=0&source_id=%25456'
            )

    def test_quote_username(self):
        self.u = self.klass('user&name','testpassword')
        self.assertEqual(self.u('123','message','456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=user%26name&password=testpassword&message=message&msisdn=123&want_report=0&source_id=456'
            )
        
    def test_quote_password(self):
        self.u = self.klass('testusername','pass&word')
        self.assertEqual(self.u('123','message','456'),self.response)
        self.assertEqual(
            self.opener.opened,
            'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testusername&password=pass%26word&message=message&msisdn=123&want_report=0&source_id=456'
            )

class ProcessResponseTests(BaseProcessResponse):

    def setUp(self):
        self.u=ProcessResponse('password')

    def test_message(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'message',
            'msisdn':'1234',
            'sender':'345',
            'msg_class':'2',
            'dca':'7bit',
            'msg_id':'40436130',
            'message':'message',
            'origin_id':'id123',
            'source_id':'id456',
            'network_id':'65501',
            'referring_msg_id':'99172705',
            'referring_batch_id':'71070172',
            },''),
            (
            Message(
                '345',
                'message'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_message_missingparams(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'message',
            },''),
            (
            Message(
                '<not supplied>',
                '<not supplied>',
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_notification(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'notification',
            'msg_id':'9916694',
            'msisdn':'123',
            'status':'11',
            'batch_id':'71070172',
            'source_id':'1234',
            },''),
            (
            Notification(
                '1234',
                status.delivered,
                '11: Delivered to mobile'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_notification_rubbish_status(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'notification',
            'msg_id':'9916694',
            'msisdn':'123',
            'status':'moo',
            'batch_id':'71070172',
            'source_id':'1234',
            },''),
            (
            Notification(
                '1234',
                status.failed,
                '70: Unknown upstream status'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_message_id_fallback(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'notification',
            'msg_id':'9916694',
            'msisdn':'123',
            'status':'11',
            'batch_id':'71070172',
            },''),
            (
            Notification(
                '9916694',
                status.delivered,
                '11: Delivered to mobile'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')
        
    def test_notification_missingparams(self):
        self.cmp(
            self.u.process(None,{
            'pass':'password',
            'type':'notification',
            },''),
            (
            Notification(
                '<not supplied>',
                status.failed,
                '70: Unknown upstream status'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_nothing(self):
        self.assertRaises(Unauthorized,self.u.process,None,{},'')

    def test_no_type(self):
        self.assertRaises(Exception,self.u.process,None,{'pass':'password'},'')

    def test_rubbish_type(self):
        self.assertRaises(Exception,self.u.process,None,{'pass':'password',
                                                         'type':'fish'},'')

    def test_wrong_password(self):
        self.assertRaises(Unauthorized,self.u.process,None,{'pass':'something'},'')

class TestZCML(TestCase):

    # The bulk of the ZCML is tested in the doctests.
    # The tests here are for the rare bits that aren't.
    layer = ZCMLLayer(
        os.path.join(os.path.split(__file__)[0], '..','ftesting.zcml'),
        __name__,
        'wasp.bulksms.zcml Functional Layer',
        allow_teardown=True)

    def setUp(self):
        self.load_zcml('<include package="wasp.bulksms" file="meta.zcml" />')
        
    def load_zcml(self,text):
        config = getConfigContext()
        xmlconfig.string(text,config)
        
    def test_secure(self):
        self.load_zcml('''
 <configure 
     xmlns="http://namespaces.zope.org/zope"
     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
     <wasp:sender 
         username="testuser"
         password="testpassword"
         secure="True"
     />
 </configure>
        ''')
        u = getUtility(ISendMessage)
        self.assertEqual(
            u.url,
            'https://bulksms.2way.co.za/eapi/submission/send_sms/2/2.0?username=testuser&password=testpassword&message=%s&msisdn=%s&want_report=0'
            )

FunctionalLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], '..','ftesting.zcml'),
    __name__,
    'wasp.bulksms Functional Layer',
    allow_teardown=True)

_original_opener = None

def urlSetUp(test):
    global _original_opener
    setUp(test)
    # *sulk* no api to retrieve this
    _original_opener = urllib2._opener
    # put in the test one
    opener = TestOpenerDirector()
    urllib2.install_opener(opener)
    test.globs['opener']=opener
    opener.set_response('0|IN_PROGRESS|71070172')
    
def urlTearDown(test):
    urllib2.install_opener(_original_opener)
    componentTearDown(test)
    
def test_suite():
    
    doc_suite = FunctionalDocFileSuite(
            'readme.txt',
            setUp=urlSetUp,
            tearDown=urlTearDown,
            optionflags=doctest.REPORT_NDIFF|doctest.ELLIPSIS
            )
    doc_suite.layer = FunctionalLayer

    return TestSuite((
        doc_suite,
        makeSuite(SendTests),
        makeSuite(ProcessResponseTests),
        makeSuite(TestZCML),
        ))
