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
"""Usage: dropmail maildir_path

dropmail simply reads a mail from stdin and write it to maildir_path.
"""
__docformat__ = 'reStructuredText'


import sys

from zope.sendmail.maildir import Maildir

def usage(code, msg=''):
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def main(*argv):
    if len(argv) != 1:
        usage(0)

    md = Maildir(argv[0])
    msg = sys.stdin.read()
    writer = md.newMessage()
    writer.write(msg)
    writer.commit()


if __name__ == '__main__':
    main(*sys.argv[1:])
