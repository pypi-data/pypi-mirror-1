=================
WASP Demo Service
=================

This package provides a demo service for testing the `wasp`
package. It will either echo output to the console or let you simulate
incoming input using a browser view. The sections below demonstrate
it's configuration and usage.

For all usage, you need to make sure the meta.zcml that defines the
directives used is loaded. This is done by adding the following to
your site.zcml::

>>> load_zcml('''
... <include package="wasp.demo" file="meta.zcml" />
... ''')

Sending Message Simulation
==========================

The `wasp.demo` package can simulate all possible types of message
sending. This is done by using different configuration directives that
should all be included in your site.zcml at some point after the
meta.zcml has been loaded as described above.

The simplest form of this is as follows::

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:sender />
... </configure>
... ''')

We can now use the `wasp.send` function and see that the demo sender
just echos the parameters it was called with to the console::

>>> from wasp import send
>>> send('123','message','xyz')
Send to: '123'
Message: 'message'
     Id: 'xyz'
True

For this particular use case, you don't actually have to load
meta.zcml or use the `wasp:sender` directive, you can just use a
normal utility registration:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.SendMessage"/>
... </configure>
... ''')

This behaves exactly the same as the previous example::

>>> from wasp import send
>>> send('123','message','xyz')
Send to: '123'
Message: 'message'
     Id: 'xyz'
True

You'll notice that in both the above example, a value of True is
returned from the `wasp.send` function. As documented in ISendMessage,
this indicates that the message was sent successfully.

We can also simulate the return of a False value, indicating that a
notification will be returned later:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope"
...     xmlns:wasp="http://namespaces.simplistix.co.uk/wasp">
...     <wasp:sender response="False"/>
... </configure>
... ''')

This behaves the same as before except `wasp.send` now returns a False
value::

>>> from wasp import send
>>> send('123','message')
Send to: '123'
Message: 'message'
     Id: None
False

Receiving Incoming Posts
========================

As an application developer it's often useful to be able to simulate
receiving notifications and messages from a WASP without actually
having to wire up a real wasp. As a WASP implementation developer,
it's often useful to be able to see what a real WASP is posting back.
`wasp.demo` helps out with both of these situations.

For each case, the Receiver view needs to be configured as normal. In
this case we bind the view to all objects::

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

Now, for developers of WASP implementations, `wasp.demo` provides a
handy IProcessResponse utility that just echos what it receives to the
console. This is configured as follows:: 

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.EchoResponse"/>
... </configure>
... ''')

This works for posts or gets where all the data is in the request::

>>> browser.open('http://localhost/@@wasp?x=1&y=2')
method: GET
  form: {u'y': u'2', u'x': u'1'}
  body: ''

It also works for posts where the data is in the body of the request::

>>> browser.post('http://localhost/@@wasp', 
...              'the post data',
...              content_type='text/plain')
method: POST
  form: {}
  body: 'the post data'

For application developers, `wasp.demo` provides an IProcessResponse
utility that takes simple urls and turns them into either a message or
a notification as required. This is configured as follows::

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.ProcessResponse"/>
... </configure>
... ''')

Of course, if we try and use this now, we will get an error because we
haven't configured anything to receive the incoming messages:

>>> browser.open('http://localhost/@@wasp?type=message&msisdn=1234&message_text=Foo')
Traceback (most recent call last):
...
ComponentLookupError: (<InterfaceClass wasp.interfaces.IReceiveMessage>, '')

Thankfully, `wasp.demo` provides two components that can receive
messages and notifications and echo their results to the console. They
are described in the following two sections.

Message Notification Simulation
===============================

To simulate receiving a notification about a message you've previously
sent with `wasp.send`, once you have configured the Receiver view and
wired in the `wasp.demo.ProcessResponse` utility as described above,
you can go to a url such as the following:

>>> url = 'http://localhost/@@wasp?type=notification&message_id=123&status=delivered&details=ok'

The `message_id` should be the id you passed as the `message_id` when
calling `wasp.send`. `status` must be the name of one of the statuses
in `wasp.status`. `details` can be any message explaining the status.

Of course, if we try this url now, we'll get an error as no
INotifyMessage utility has been configured:

>>> browser.open(url)
Traceback (most recent call last):
...
ComponentLookupError: (<InterfaceClass wasp.interfaces.INotifyMessage>, '')

This type of utility would normally be implemented by the application
developer, but `wasp.demo` also provides a handy version that just
echos the notification to the console:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.EchoNotification"/>
... </configure>
... ''')

Now when we open the url, we just get the notification echoed to the
console::

>>> browser.open(url)
message_id: u'123'
    status: <wasp.status.Delivered instance at ...>
   details: u'ok'
 
Receiving Message Simulation
============================

To simulate receiving a message, once you have configured the Receiver
view and wired in the `wasp.demo.ProcessResponse` utility as described
above, you can go to a url such as the following:

>>> url = 'http://localhost/@@wasp?type=message&msisdn=123&message_text=my+message'

The `msisdn` represents the msisdn that sent the message while
`message_text` should contain the text of the message.

Of course, if we try this url now, we'll get an error as no
IReceiveMessage utility has been configured:

>>> browser.open(url)
Traceback (most recent call last):
...
ComponentLookupError: (<InterfaceClass wasp.interfaces.IReceiveMessage>, '')

This type of utility would normally be implemented by the application
developer, but `wasp.demo` also provides a handy version that just
echos the notification to the console:

>>> load_zcml('''
... <configure 
...     xmlns="http://namespaces.zope.org/zope">
...     <utility factory="wasp.demo.EchoMessage"/>
... </configure>
... ''')

Now when we open the url, we just get the notification echoed to the
console::

>>> browser.open(url)
      msisdn: u'123'
message_text: u'my message'
