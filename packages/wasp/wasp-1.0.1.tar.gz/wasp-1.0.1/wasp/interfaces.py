# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from zope.interface import Interface

class IReceiveMessage(Interface):

    def __call__(msisdn,message_text):
        """
        This method is called to handle incoming messages.
        The implementation should do whatever is required by the
        application.

        msisdn - the msisdn that sent the incoming message

        message_text - the text of the message
        """

class INotifyMessage(Interface):

    def __call__(message_id,status,details):
        """
        This method is called when status notifications about a
        previously sent message are recieved.

        message_id - will be that passed in the call to the `send`
                     method

        status - will be the 
        """

# You only need to know details of the following interfaces if you're
# implementing a particular WASP.

class ISendMessage(Interface):

    def __call__(msisdn,message_text,message_id=None):
        """
        Send the message_text to the specified msisdn.
        The message_id is a unique id for this message. If supplied,
        it will be returned to any configured INotifyMessage.

        This returns either:

        True - indicating that the message has been
               successfully delivered

        False - indicating that a notification of delivery status will
                be sent.
                (NB: an IRecieveMessage must be configured in this
                     case)

        In other cases, an exception should be raised indicating the
        nature of the problem that occurred.
        """

class IProcessResponse(Interface):
    """
    Each WASP implementation should provide a utility implementing
    this interface.
    """

    def process(request,form,body):
        """
        This method is called by the reciever view with information
        from the request received. This should be parsed and an
        iterable returned that yields wasp.Notification and
        wasp.Message objects. For more information on these see their
        docstrings and code.
        It's acceptable to return an empty sequence or a sequence
        containing one item.
        """

    def response():
        """
        This should return a string containing the values to be
        returned by the Receiver view.
        This will need to be done in the event that the WASP
        implementation requires a specific response to any HTTP POSTs
        or GETs that it sends.
        """
        
