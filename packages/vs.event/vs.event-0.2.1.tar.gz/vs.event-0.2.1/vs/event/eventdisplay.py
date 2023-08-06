# -*- coding: ISO-8859-15 -*-
# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: eventdisplay.py 69737 2008-08-11 19:02:44Z claytron $
"""Occurrence rendering logic"""

from datetime import timedelta, datetime, time
from AccessControl import getSecurityManager

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("calendar")

from p4a.common import dtutils

from dateable.chronos.browser.displaytable import Cell
from dateable.chronos.browser.interfaces import IEventDisplay


# XXX This is reused in several places by copy/paste.
# Some sort of refactoring here would be good.
def checkPermission(permission, object):
    user = getSecurityManager().getUser()
    return user.has_permission(permission, object)


class EventDisplay(Cell):
    """Adapts en event to IEventDisplay
    """

    implements(IEventDisplay)

    def __init__(self, event, view):
        """Creates and calculates render information"""

        self.event = event
        self.view = view

        # XXX Check permissions
        self.viewable = True
        # TODO: Here we could calculate short titles that fit into one row
        # and how much of the decription fits and stuff like that as well.
    
        if self.viewable:
            self.title = event.title
            self.description = event.description
            self.url = event.url
        else:
            self.title = self.description = _('Private Event')
            self.url = ''

        event_begins = event.start
        event_ends = event.end
        self.title_and_time = "%s %02d:%02d - %02d:%02d" % (self.title,
                                        event_begins.hour,event_begins.minute,
                                        event_ends.hour, event_ends.minute)


