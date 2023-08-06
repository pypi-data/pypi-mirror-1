vs.event
========

``vs.event`` provides an extendes event functionality for Plone

Features
========

- recurring events (based on p4a.ploneevent)
- a new calendar widget 
- real support for all-day events
- working iCal/vCal export for all-day events
- full integration with Plone4Artists calendar (must be installed seperately)
- support for multi-events (one master event and several depending events)

Installation
============

Add ``vs.event`` to the ``eggs`` and ``zcml`` options of your buildout.cfg.
Create a new Plone site using the ``vs.event`` profile or install ``vs.event``
through the quick installer of Plone.

Known bugs and limitations
==========================

- the localization of the date picker widget support only 'en' and 'de'
  so far. The date picker widget will use/present the US date format for
  languages other than German.

- tooltip showing title/time within the P4A calendar does display  
  all-day events properly

License
=======

``vs.event`` is published under the GNU Public License 2.

Parts of the code of ``vs.event`` (iCal implementation) are based on work
in ATContentTypes.



Authors
=======

- Andreas Jung
- Veit Schiele
- Anne Wello
