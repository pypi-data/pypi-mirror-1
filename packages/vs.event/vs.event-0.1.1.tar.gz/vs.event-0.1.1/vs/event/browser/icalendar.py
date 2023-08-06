################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Wello
################################################################

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Globals import InitializeClass

class iCalendarView(BrowserView):
    """ """

    def icalendar_export(self, **kw):
        """ create a new dependent event"""

        catalog = getToolByName(self.context, 'portal_catalog')
        calendar = getToolByName(self.context, 'portal_calendar')

        cal_types = list(calendar.getCalendarTypes())
        query = kw.copy()
        query.update(dict(portal_type=cal_types))

        result = list()
        write = result.append
        calname = self.context.Title()

        try:
            relcalid = self.context.UID()
        except AttributeError:
            relcalid = self.context.portal_url.getPortalObject().getId()

        write('BEGIN:VCALENDAR')
        write('VERSION:2.0')
        write('X-WR-CALNAME:%s' % calname.upper())
        write('PRODID:-//Plone 3.0\, Inc//(C) ZOPYX Ltd & Co. KG//EN')
        write('X-WR-RELCALID:%s'%relcalid)
        write('X-WR-TIMEZONE:Europe/Berlin')
        write('CALSCALE:GREGORIAN')
        write('METHOD:PUBLISH')

        for brain in catalog(query):
            event = brain.getObject()
            ical_out = event.getICal()
            for line in ical_out.split('\n'):
                write(line)

        write('END:VCALENDAR')

        body = '\n'.join(result)
        self.context.request.response.setHeader('Content-Length', len(body))
        self.context.request.response.setHeader('Content-Type', 'text/x-vcalendar')
        self.context.request.response.setHeader('Content-Disposition', 'attachment; filename=plone-cal.ics')
        return self.context.request.response.write(body)

InitializeClass(iCalendarView)
