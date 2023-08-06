#-*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#   Copyright (c) 2007-2009 Gregor Giesen <vogon@zaehlwerk.net>             #
#                                                                           #
# This program is free software; you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation; either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################
""" 
$Id$
"""
__docformat__ = 'reStructuredText'

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zw.mail.incoming')

import email

from zope.interface import implements
from zw.mail.incoming.interfaces import IIncomingEmailEvent, \
    IIncomingEmailFailureEvent


class NewEmailEvent(object):
    implements(IIncomingEmailEvent)

    def __init__(self, msg, inbox, root):
        self.message = msg
        self.inbox = inbox
        self.root = root


def extractDeliveryReport(msg):
    assert isinstance(msg, email.message.Message), \
        "Message is not an instance of 'email.message.Message'."
    for part in msg.walk():
        if part['Content-Type'] == 'message/delivery-status':
            return part


class NewEmailFailureEvent(NewEmailEvent):
    implements(IIncomingEmailFailureEvent)
    
    def __init__(self, msg, inbox, failures, root):
        super(NewEmailFailureEvent, self).__init__(msg, inbox, root)
        self.failures = failures
        self.delivery_report = extractDeliveryReport(msg)
    
