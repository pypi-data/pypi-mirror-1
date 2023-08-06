# Copyright (c) 2008 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
"""
This module contains constants for statuses returned in notifications
from WASPs about the delivery of messages sent wit hteh `send`
function.

They are implemented as classes in case they need to be adapted using
the component architecture at a later date.
"""

class Status:
    pass

class Delivered(Status):
    """
    The message was successfully delivered to its recipient.
    """

class Failed(Status):
    """
    The message delivery has failed.
    """

delivered = Delivered()
failed = Failed()
