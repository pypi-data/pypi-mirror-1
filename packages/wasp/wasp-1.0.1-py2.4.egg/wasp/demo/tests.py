# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os.path
import sys
import wasp.demo

from StringIO import StringIO
from unittest import TestCase,TestSuite,makeSuite
from wasp import Message,Notification,status
from wasp.demo import SendMessage,ProcessResponse
from wasp.tests import BaseSendTests, BaseProcessResponse, setUp, FunctionalLayer
from textwrap import dedent
from zope.app.testing.functional import ZCMLLayer
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.component.testing import tearDown as componentTearDown
from zope.testing import doctest

class Checker:

    def __init__(self,u):
        self.u = u
        self.o = StringIO()

    def __call__(self,*args,**kw):
        try:
            sys.stdout = self.o
            return self.u(*args,**kw)
        finally:
            sys.stdout = sys.__stdout__

    def check(self,t,expected):
        t.assertEqual(self.o.getvalue(),dedent(expected))
            
class SendTests(BaseSendTests):

    klass = SendMessage

    def test_send(self):
        c = Checker(self.u)
        self.assertEqual(c('123','test message','456'),self.response)
        c.check(self,"""\
        Send to: '123'
        Message: 'test message'
             Id: '456'
        """)

    def test_send_no_id(self):
        c = Checker(self.u)
        self.assertEqual(c('123','test message'),self.response)
        c.check(self,"""\
        Send to: '123'
        Message: 'test message'
             Id: None
        """)

    def test_send_false_response(self):
        c = Checker(SendMessage(response=False))
        self.assertEqual(c('123','test message'),False)
        c.check(self,"""\
        Send to: '123'
        Message: 'test message'
             Id: None
        """)
        
class ProcessResponseTests(BaseProcessResponse):

    klass = ProcessResponse

    def test_message(self):
        self.cmp(
            self.u.process(None,{
            'type':'message',
            'msisdn':'1234',
            'message_text':'message',
            },''),
            (
            Message(
                '1234',
                'message'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_message_missingparams(self):
        self.cmp(
            self.u.process(None,{
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
            'type':'notification',
            'message_id':'1234',
            'status':'failed',
            'details':'it sucked',
            },''),
            (
            Notification(
                '1234',
                status.failed,
                'it sucked'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_notification_rubbish_status(self):
        self.cmp(
            self.u.process(None,{
            'type':'notification',
            'message_id':'1234',
            'status':'moo',
            'details':'it sucked',
            },''),
            (
            Notification(
                '1234',
                status.delivered,
                'it sucked'
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_notification_missingparams(self):
        self.cmp(
            self.u.process(None,{
            'type':'notification',
            },''),
            (
            Notification(
                '<not supplied>',
                status.delivered,
                '<not supplied>',
                ),
            )
            )
        self.assertEqual(self.u.response(),'done')

    def test_nothing(self):
        self.cmp(
            self.u.process(None,{},''),
            (),
            )
        self.assertEqual(self.u.response(),'done')

    def test_no_type(self):
        self.cmp(
            self.u.process(None,{
            'message_id':'1234',
            'status':'failed',
            'detailed':'it sucked',
            },''),
            ()
            )
        self.assertEqual(self.u.response(),'done')

    def test_rubbish_type(self):
        self.cmp(
            self.u.process(None,{
            'type':'fish',
            },''),
            ()
            )
        self.assertEqual(self.u.response(),'done')

FunctionalLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], '..','ftesting.zcml'),
    __name__,
    'wasp.demo Functional Layer',
    allow_teardown=True)

def test_suite():
    
    doc_suite = FunctionalDocFileSuite(
            'readme.txt',
            setUp=setUp,
            tearDown=componentTearDown,
            optionflags=doctest.REPORT_NDIFF|doctest.ELLIPSIS
            )
    doc_suite.layer = FunctionalLayer

    return TestSuite((
        doc_suite,
        makeSuite(SendTests),
        makeSuite(ProcessResponseTests),
        ))
