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
from zope.component import adapter, queryUtility
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import Path, Tokens
from zope.interface import Interface
from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.app.appsetup.interfaces import IDatabaseOpenedWithRootEvent

from zw.mail.incoming.interfaces import IInbox
from zw.mail.incoming.inbox import MaildirInbox
from zw.mail.incoming.processor import IncomingMailProcessor

class IIncomingMailProcessorDirective(Interface):
    """This directive register an event on IDataBaseOpenedWithRoot
    to launch an incoming mail processor.
    """
    
    name = schema.TextLine(
        title = _( u'label-IIncomingMailProcessorDirective.name',
                   u"Name" ),
        description = _( u'help-IIncomingMailProcessorDirective.name',
                         u"Specifies the name of the mail processor." ),
        default = u"Incoming Mail",
        required = False )

    pollingInterval = schema.Int(
        title = _( u"Polling Interval" ),
        description = _( u"How often the mail sources are checked for "
                         u"new messages (in milliseconds)" ),
        default = 5000 )

    sources = Tokens(
        title = _( u"Sources" ),
        description = _( u"Iterable of names of IInbox utilities." ),
        required = True,
        value_type = schema.TextLine(
            title = _( u"Inbox utility name" )
            )
        )
        

def incomingMailProcessor(_context, sources, pollingInterval = 5000, 
                          name = u"Incoming Mail" ):

    @adapter(IDatabaseOpenedWithRootEvent)
    def createIncomingMailProcessor(event):
        db, conn, root, root_folder = getInformationFromEvent(event)

        inboxes = []
        for name in sources:
            inbox = queryUtility(IInbox, name)
            if inbox is None:
                raise ConfigurationError("Inbox %r is not defined." % name)
            inboxes.append(inbox)

        thread = IncomingMailProcessor(root_folder, pollingInterval, inboxes)
        thread.start()

    _context.action(
        discriminator = None,
        callable = handler,
        args = ('registerHandler',
                createIncomingMailProcessor, (IDatabaseOpenedWithRootEvent,),
                u'', _context.info),
        )
    
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', IDatabaseOpenedWithRootEvent)
        )


class IInboxDirective(Interface):
    """A generic directive registering an inbox.
    """

    name = schema.TextLine(
        title = _( u'label-IInboxDirective.name',
                   u"Name" ),
        description = _( u'help-IInboxDirective.name',
                         u"Specifies the Inbox name of the utility." ),
        required = True )

class IMaildirInboxDirective(IInboxDirective):
    """Registers a new maildir inbox.
    """
    
    path = Path(
        title = _( u'label-IMaildirInboxDirective.path',
                   u"Maildir Path" ),
        description = _( u'help-IMaildirInboxDirective.path',
                         u"Defines the path to the inbox maildir directory." ),
        required = True )

def maildirInbox(_context, name, path):
    _context.action(
        discriminator = ('utility', IInbox, name),
        callable = handler,
        args = ('registerUtility',
                MaildirInbox(path), IInbox, name)
        )
