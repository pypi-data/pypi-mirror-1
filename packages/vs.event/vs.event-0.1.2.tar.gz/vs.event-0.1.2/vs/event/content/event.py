# -*- coding: utf-8 -*-
# $Id: event.py 340 2009-06-12 06:57:51Z ajung $



from AccessControl import ClassSecurityInfo
from zope.interface import implements

from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.permissions import View
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from vs.event.config import *
from vs.event.interfaces import IVSEvent, IVSSubEvent
from vs.event import MessageFactory as _
from vs.event import validators 
from vs.event.fieldsandwidgets.calendarwidget import VSCalendarWidget
import event_util

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi


from logging import getLogger
log = getLogger(">> event : ")

VSEventSchema = atapi.Schema((

    atapi.ReferenceField(
        name='subEvents',
        allowed_types=('VSSubEvent',),
        multiValued=True,
        relationship='isSubEvent',
        widget=ReferenceBrowserWidget(
            visible={'view': 'invisible', 'edit':'invisible'},
        ),
    ), 
    atapi.LinesField(
        name='weekdays',
        schemata='recurrence',
        vocabulary=atapi.DisplayList((
            ('0', _(u'vs_label_mo')),
            ('1', _(u'vs_label_di')),
            ('2', _(u'vs_label_mi')),
            ('3', _(u'vs_label_do')),
            ('4', _(u'vs_label_fr')),
            ('5', _(u'vs_label_sa')),
            ('6', _(u'vs_label_so')) 
        )),
        widget=atapi.MultiSelectionWidget(
            format="checkbox",
            label=_(u'vs_event_label_weekdays',),
            description=_(u'vs_event_help_weekdays'),
        ),
    ),
    atapi.StringField(
        name='bysetpos',
        schemata='recurrence',
        validators=('isLineOfInts',),
        widget=atapi.StringWidget(
            label=_(u'vs_event_label_bysetpos'),
            description=_(u'vs_event_help_bysetpos'),
        ),
    ),
    atapi.LinesField(
        name='exceptions',
        schemata='recurrence',
        validators=('linesOfDates',),
        widget=atapi.LinesWidget(
            label=_(u'vs_event_label_exceptions'),
            description=_(u'vs_event_help_exceptions'),
        ),
    )
))

VSEventSchema = VSEventSchema + ATEvent.schema.copy()
finalizeATCTSchema(VSEventSchema, folderish=False, moveDiscussion=True)


def modifyEventSchema(schema):
    schema.addField(atapi.BooleanField('wholeDay',
                                       description_msg='help_whole_day_event',
                                       label='Whole day event',
                                       label_msgid='label_whole_day_event',
                                       i18n_domain='plone',
                                       ))
    schema.addField(atapi.BooleanField('useEndDate',
                                       default=True,
                                       description_msg='help_has_end_date',
                                       label='useEndDate',
                                       label_msgid='label_use_end_date',
                                       i18n_domain='plone',
                                       ))
    schema.moveField('wholeDay', before='startDate')
    schema.moveField('useEndDate', after='wholeDay')
    schema['startDate'].widget = VSCalendarWidget(description= "",
                                                description_msgid = "help_event_start",
                                                label="Event Starts",
                                                label_msgid = "label_event_start",
                                                i18n_domain = "plone",
                                                with_time=1,
                                                with_popup=1,
                                                js_shortcuts=0,
                                                ignore_unset_time=1)

    schema['endDate'].widget = VSCalendarWidget(description = "",
                                              description_msgid = "help_event_end",
                                              label = "Event Ends",
                                              label_msgid = "label_event_end",
                                              i18n_domain = "plone",
                                              with_time=1,
                                              with_popup=1,
                                              js_shortcuts=0,
                                              ignore_unset_time=1)

    return schema

class VSEvent(ATEvent):
    """ vs.event """

    security = ClassSecurityInfo()
    implements(IVSEvent)
    meta_type = 'VSEvent'
    _at_rename_after_creation = True
    schema = modifyEventSchema(VSEventSchema)

    security.declareProtected(View, 'getICal')
    def getICal(self):
        """get iCal data """
        return event_util.getICal(self)

    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get VCal data """
        return event_util.getVCal(self)


    def at_post_edit_script(self):
        """ Ensure that for single-day dates without an end date
            the end date is equal to the start date.
        """
        if not self.getUseEndDate():
            self.setEndDate(self.start())



atapi.registerType(VSEvent, PROJECTNAME)


def modifySubEventSchema(schema):
    # remove unwanted fields for subevents
    for id in ('attendees', 'contactName', 'contactEmail', 'contactPhone', 'eventType', 'eventUrl'):
        schema[id].widget.visible = False
    for field in schema.fields():
        if field.schemata in ('dates', 'categorization', 'ownership', 'settings'):
            field.widget.visible = False

    schema.addField(atapi.BooleanField('wholeDay',
                                       default=False,
                                       description_msg='help_whole_day_event',
                                       label='Whole day event',
                                       label_msgid='label_whole_day_event',
                                       i18n_domain='plone',
                                       ))
    schema.addField(atapi.BooleanField('useEndDate',
                                       default=True,
                                       description_msg='help_has_end_date',
                                       label='useEndDate',
                                       label_msgid='label_use_end_date',
                                       i18n_domain='plone',
                                       ))
    schema.moveField('wholeDay', before='startDate')
    schema.moveField('useEndDate', after='wholeDay')

    schema['startDate'].widget = VSCalendarWidget(description= "",
                                                description_msgid = "help_event_start",
                                                label="Event Starts",
                                                label_msgid = "label_event_start",
                                                i18n_domain = "plone",
                                                with_time=1,
                                                with_popup=1,
                                                js_shortcuts=0,
                                                ignore_unset_time=1)

    schema['endDate'].widget = VSCalendarWidget(description = "",
                                              description_msgid = "help_event_end",
                                              label = "Event Ends",
                                              label_msgid = "label_event_end",
                                              i18n_domain = "plone",
                                              with_time=1,
                                              with_popup=1,
                                              js_shortcuts=0,
                                              ignore_unset_time=1)

    return schema

VSSubEventSchema = ATEvent.schema.copy()
finalizeATCTSchema(VSSubEventSchema, folderish=False, moveDiscussion=True)

class VSSubEvent(ATEvent):
    """ vs.event """

    security = ClassSecurityInfo()
    implements(IVSSubEvent)
    meta_type = 'VSSubEvent'
    _at_rename_after_creation = True
    schema = modifySubEventSchema(VSSubEventSchema)

    security.declareProtected(View, 'getICal')
    def getICal(self):
        """get iCal data """
        return event_util.getICal(self)

    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get VCal data """
        return event_util.getVCal(self)

    def at_post_edit_script(self):
        """ Ensure that for single-day dates without an end date
            the end date is equal to the start date.
        """
        if not self.getUseEndDate():
            self.setEndDate(self.start())

atapi.registerType(VSSubEvent, PROJECTNAME)
