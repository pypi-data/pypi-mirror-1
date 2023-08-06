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

import atexit
from time import sleep
from threading import Thread

import logging
import transaction

from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.event import notify
from zope.interface import implements

from mailman.Bouncers.BouncerAPI import ScanMessages

from zw.mail.incoming.events import NewEmailEvent, NewEmailFailureEvent
from zw.mail.incoming.interfaces import IIncomingMailProcessor, IInbox

class IncomingMailProcessor(Thread):
    implements(IIncomingMailProcessor)

    log = logging.getLogger("IncomingMailProcessorThread")
    __stopped = False

    def __init__(self, root, interval, inboxes):
        Thread.__init__(self)
        self.context = root
        self.pollingInterval = interval
        self.sources = tuple(inboxes)

    def run(self, forever=True):
        atexit.register(self.stop)
        while not self.__stopped:
            for box in self.sources:
                msg = None
                try:
                    msg = box.next()
                    
                    failures = ScanMessages(None, msg)
                    if failures:
                        notify( NewEmailFailureEvent( msg, box, failures, self.context ) )
                    else:
                        notify( NewEmailEvent( msg, box, self.context ) )
                        

                except StopIteration:
                    # That's fine.
                    pass

                except:
                    # Catch up any other exception to let this thread survive.
                    if msg is None:
                        self.log.error(
                            "Cannot access next message from inbox '%r'.",
                            box )
                    else:
                        self.log.error(
                            "Cannot process message '%s' from inbox '%r'.",
                            msg['Message-Id'], box )
                            
                else:
                    transaction.commit()

                
            else:
                if forever:
                    sleep(self.pollingInterval/1000.)

            if not forever:
                break
        
    def stop(self):
        self.__stopped = True

    
