################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Wello
################################################################

from p4a.ploneevent.recurrence.browser.event_view import EventView
from zope import interface 
from plone.memoize.instance import memoize
from datetime import date 
from dateable.kalends import IRecurrence
from dateutil.parser import parse
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized, getSecurityManager
from Products.CMFPlone.utils import base_hasattr
from Products.CMFCore.permissions import ModifyPortalContent, View

from vs.event.config import *
from vs.event.interfaces import IVSSubEvent

class VSEventView(EventView):
    """
    """
    @memoize    
    def filteredAttendees(self):
        """
        """
        attendees = self.context.getAttendees()
        result = []
        for attendee in attendees:
            if attendee['show']:
                result.append(attendee)
        return result


    def getMainEvent(self):
        """ return the main event from the list of backrefs """

        backrefs = self.context.getBRefs()
        if backrefs:
            return backrefs[0]
        return None

    def getSupplementaryEvents(self):
        """ return list of suppl. events in sorted order """

        sm = getSecurityManager()
        events = self.context.getSubEvents()
        events = [ev for ev in events if sm.checkPermission(View, ev)]
        events.sort(lambda e1,e2: cmp(e1.start(), e2.start()))
        return events

    @memoize
    def nextDates(self):
        """
        """
        return [ date.fromordinal(x) for x in IRecurrence(self.context, None).getOccurrenceDays()]
 
    @memoize
    def getExceptions(self):
        """
        """
        return [parse(x) for x in self.context.getExceptions()]     



    @memoize
    def toLocalizedTime(self, time, long_format=None):
        """Convert time to localized time
        """
        properties=getToolByName(self.context, 'portal_properties').site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            format=properties.localTimeFormat

        return time.strftime(format)

    @memoize
    def allowedToAddSubEvents(self):
        """ Security chess """
        return getSecurityManager().checkPermission(ModifyPortalContent, self)


    @memoize
    def subeventsEnabled(self):
        """Convert time to localized time
        """
        calendar = getToolByName(self.context, 'portal_calendar')
        return getattr(calendar, 'vs_event_supplementary_events', False)


    @memoize
    def isSubEvent(self):
        """ check if the current object is a VSSubEvent """
        return IVSSubEvent.providedBy(self.context)

InitializeClass(VSEventView)
