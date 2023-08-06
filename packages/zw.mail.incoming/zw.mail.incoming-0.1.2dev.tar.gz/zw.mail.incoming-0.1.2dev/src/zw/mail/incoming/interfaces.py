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

from zope import schema
from zope.interface import Attribute, Interface

from z3c.schema.email import RFC822MailAddress

class IInbox(Interface):
    """An inbox provides a very simple interface for our needs."""

    def pop():
        """Return an email.message.Message converted message and remove it.
        """

    def __iter__():
        """Iterate through all messages.
        """

    def next():
        """Return an email.message.Message converted message.
        """

    def delete(msg):
        """Delete msg from inbox.
        """


class IMaildirInbox(IInbox):
    """An inbox that receives its messages by an Maildir folder.
    """

    queuePath = schema.TextLine(
        title = _( u"Queue Path" ),
        description = _( u"Pathname of the Maildir directory." ) )


class IIMAPInbox(IInbox):
    """An inbox that receives its message via an IMAP connection.
    """


class IIncomingMailProcessor(Interface):
    """A mail queue processor that raise IIncomingMailEvent on new messages.
    """

    pollingInterval = schema.Int(
        title = _( u"Polling Interval" ),
        description = _( u"How often the mail sources are checked for "
                         u"new messages (in milliseconds)" ),
        default = 5000 )

    sources = schema.FrozenSet(
        title = _( u"Sources" ),
        description = _( u"Iterable of inbox utilities." ),
        required = True,
        value_type = schema.Object(
            title = _( u"Inbox source" ),
            schema = IInbox
            )
        )

        
class IIncomingEmailEvent(Interface):
    """A new mail arrived.
    """

    message = Attribute(u"""The new email.message message.""")

    inbox = schema.Object(
        title = _( u"The inbox" ),
        description = _( u"The mail folder the message is contained in" ),
        schema = IInbox )

    root = Attribute(u"""The root object""")
    

class IIncomingEmailFailureEvent(IIncomingEmailEvent):
    """A new mail arrived with a failure.
    """

    failures = schema.List(
        title = _( u"Failure addresses" ),
        description = _( u"Extracted list of failure addresses." ),
        value_type = RFC822MailAddress(
            title = u"Failure address" ),
        )
            
    delivery_report = Attribute(u"""The delivery report as email.message.Message.""")
