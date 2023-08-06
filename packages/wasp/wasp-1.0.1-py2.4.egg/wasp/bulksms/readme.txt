======================
BulkSMS Implementation
======================

This package provides an implementation for the BulkSMS service.
It currently only supports the South African offering from BulkSMS.
The sections below demonstrate it's configuration and usage.

For all usage, you need to make sure the meta.zcml that defines the
directives used is loaded. This is done by adding the following to
your site.zcml::

>>> load_zcml('''
... <include package="wasp.bulksms" file="meta.zcml" />
... ''')

For the examples below, you'll see the output of calls to open
urls. This will show exactly what `wasp.bulksms` sends over the wire::

>>> from urllib2 import urlopen
>>> r = urlopen('http://www.google.com').read()
opened: 'http://www.google.com'

Sending Messages
==========================

This is done by adding an appropriate configuration directive to your
site.zcml at some point after the meta.zcml has been loaded as
described above. 

Here's a simple example of the directive::

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:sender 
...         username="testuser"
...         password="testpassword"
...     />
... </configure>
... ''')

A full reference to the <wasp:sender/> directive is provided later on
in this document.

We can now use the `wasp.send` as documented for the `wasp` package::

>>> from wasp import send
>>> send('123','message','xyz')
opened: 'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testuser&password=testpassword&message=message&msisdn=123&want_report=0&source_id=xyz'
False

As you can see, the `wasp.bulksms` implementation returns a False
value indicating that, at the point of sending, BulkSMS cannot tell
you whether or not the message was delivered. If you require
notification of message delivery, please see the section on this
below.

Now, if something goes wrong during messsage sending, BulkSMS will
return a response that looks something like the following:

>>> opener.set_response('22|INTERNAL_FATAL_ERROR|71070172')

The `wasp.bulksms` package will turn these into exceptions, as
documented in `wasp.interfaces`::

>>> send('123','message','xyz')
Traceback (most recent call last):
...
SendException: 22: Internal fatal error

Receiving Notifications About Messages
======================================

If you want to receive notifications when messages are delivered or
when things go wrong after the initial send, then you need to
configure the sender differently:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:sender 
...         username="testuser"
...         password="testpassword"
...         want_report="True"
...     />
... </configure>
... ''')

The change tells BulkSMS to send back reports once the outcome of
message delivery is known.

Now, you need to wire in the Receiver view as normal. For
demonstration purposes, we bind the view to all objects::

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:browser="http://namespaces.zope.org/browser">
...   <browser:page
...       name="wasp"
...       for="*"
...       class="wasp.Receiver"
...       permission="zope.Public"
...    
...     />
... </configure>
... ''')

Finally, we have to configure a processor for incoming requests from
BulkSMS processor so that incoming requests from BulkSMS are passed to
the handlers we will provide:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:processor
...         incoming_password="incomingpassword"
...     />
... </configure>
... ''')

The `incoming_password` will be checked for requests from BulkSMS and
only those requests with a matching password will be processed.

Now that the configuration is complete, the application programmer
needs to write a handler for the notifications. 

For demonstration purposes, we'll use the
`wasp.demo.EchoNotification` handler:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.EchoNotification"/>
... </configure>
... ''')

At this point, you should let BulkSMS know the URL to send their
status reports to. For what we've configured above, it would be::

  http://localhost:/@@wasp?pass=incomingpassword&type=notification

Now, when you send a message, the `message_id` you send will be sent
to BulkSMS:

>>> opener.set_response('0|IN_PROGRESS|71070172')
>>> r = send('123','message','id123')
opened: 'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testuser&password=testpassword&message=message&msisdn=123&want_report=1&source_id=id123'

When the message is delivered, the application notification code will
now get called:

>>> browser.open('http://localhost/@@wasp?pass=incomingpassword&type=notification&msg_id=99166594&msisdn=123&status=11&batch_id=71070172&source_id=id123')
message_id: u'id123'
    status: <wasp.status.Delivered instance at ...>
   details: '11: Delivered to mobile'

Beware though, if the application calls `wasp.send` without a
`message_id`, then the `message_id` returned by BulkSMS will be
meaningless:

>>> r = send('123','message')
opened: 'http://bulksms.2way.co.za:5567/eapi/submission/send_sms/2/2.0?username=testuser&password=testpassword&message=message&msisdn=123&want_report=1'

>>> browser.open('http://localhost/@@wasp?pass=incomingpassword&type=notification&msg_id=99166594&msisdn=123&status=11&batch_id=71070172')
message_id: u'99166594'
    status: <wasp.status.Delivered instance at ...>
   details: '11: Delivered to mobile'

If an error is reported by BulkSMS, then the status returned to the
handler will reflect that with the full error message being returned
in the details:

>>> browser.open('http://localhost/@@wasp?pass=incomingpassword&type=notification&msg_id=99166594&msisdn=123&status=22&batch_id=71070172&source_id=id123')
message_id: u'id123'
    status: <wasp.status.Failed instance at ...>
   details: '22: Internal fatal error'


Receiving Messages
============================

If you want to receive messages, you need to configure the Receiver
view as normal. For demonstration purposes, we'll wire the view to all
objects, although you may prefer to configure it such that the view is
only available through one specific url::

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:browser="http://namespaces.zope.org/browser">
...   <browser:page
...       name="wasp"
...       for="*"
...       class="wasp.Receiver"
...       permission="zope.Public"
...    
...     />
... </configure>
... ''')

Now, we have to configure a processor for incoming requests from
BulkSMS processor so that incoming requests from BulkSMS are passed to
the handlers we will provide:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:processor
...         incoming_password="incomingpassword"
...     />
... </configure>
... ''')

Finally, the application programmer needs to write a handler for the
notifications. For demonstration purposes, we'll use the
`wasp.demo.EchoMessage` handler:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.EchoMessage"/>
... </configure>
... ''')

At this point, you should let BulkSMS know the URL to send message
to. For what we've configured above, it would be:: 

  http://localhost/@@wasp?pass=incomingpassword&type=message

Now, when BulkSMS sends requests to your web server, the application
programmer's code will get called:

>>> browser.open('http://localhost/@@wasp?pass=incomingpassword&type=message&msisdn=123&sender=345&msg_class=2&dca=7bit&msg_id=40436130&message=my+message&origin_id=id123&source_id=id123&network_id=65501&referring_msg_id=99172705&referring_batch_id=71070172')
      msisdn: u'345'
message_text: u'my message'

wasp:sender reference
=====================

The `wasp:sender` directive provided by `wasp.bulksms` configures an
ISendMessage utility that sends messages using the BulkSMS
service. The configuration options are as follows::

  *username*
    The username provided to you by BulkSMS for sending messages.

  *password*
    The password provided to you by BulkSMS for sending messages.

  *secure*
    If set to True, messages will be sent to BulkSMS over a secure
    connection. This will slow down delivery but will mean message
    content cannot be snooped.
    
    default: False

  *want_report*
    If set to True, BulkSMS will send back status reports on message
    delivery to the url you have configured with them.

    default: False

wasp:processor reference
========================

The `wasp:processor` directive provided by `wasp.bulksms` configures
an IProcessResponse utility that parses incoming requests from the
BulkSMS service. The configuration options are as follows::

  *incoming_password*
    The password that will be used to check requests from BulkSMS. If
    the password provided in the requests does not match the password
    configured with this option, the request will be ignored.