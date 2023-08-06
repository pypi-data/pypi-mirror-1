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
from os import unlink

from zope.interface import implements
from zope.sendmail.maildir import Maildir

from zw.mail.incoming.interfaces import IMaildirInbox
      
class MaildirInbox(object):
    implements(IMaildirInbox)

    def __init__(self, path):
        self.queuePath = path
        self.maildir = Maildir(path, True)

    def __repr__(self):
        return '<%s %r>' % ( self.__class__.__name__, self.queuePath )

    def pop(self):
        filename = iter(self.maildir).next()
        msg = email.message_from_file(
            open(filename, 'r') )
        unlink(filename)
        return msg

    def next(self):
        filename = iter(self.maildir).next()
        return email.message_from_file(
            open(filename, 'r') )
    
    def __iter__(self):
        return iter(
            [ email.message_from_file(open(filename, 'r')) \
                  for filename in self.maildir ] )
    
    def delete(self, msg):
        for filename in self.maildir:
            if email.message_from_file(
                open(filename, 'r') ).as_string() == msg.as_string():
                unlink(filename)
                break
