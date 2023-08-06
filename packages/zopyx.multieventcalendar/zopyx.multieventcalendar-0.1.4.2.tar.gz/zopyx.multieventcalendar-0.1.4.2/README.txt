zopyx.multieventcalendar
------------------------

zopyx.multieventcalendar extends the standard Plone 'Event' type with five
supplementary date fields. The purpose of this extender is to support events
with multiple dates associated. E.g. a conference takes place at a particular
date but often has additional associated dates like for a call-for-papers or a
registration deadline.  Instead of having multiple unassociated events within
Plone, you can manage all that with one event instance.

In addition zopyx.multieventcalendar provides a week and month calendar
supporting this event extender. The implementation also supports
export/subscription with iCal.


Requirements
============

- Plone 3.0 or higher

Installation
============

- either by choosing the ``zopyx_multieventcalendar`` extension profile while creating
  a new Plone site
- or using the Plone control panel

Usage
=====

- create a new ``Event``
- check out the ``MoreDates`` fieldset while editing the event instance
- visit ``http://yourhost:yourport/your-plone/zme_calendar``


Author
======

``zopyx.multieventcalendar`` was written by Andreas Jung for ZOPYX Ltd. & Co.
KG, Tuebingen, Germany and partly funded by the Friedrich-Miescher-Laboratory
of the Max-Planck-Society, Tuebingen, Germany and the Max Planck Institute for
Biological Cybernetics, Tuebingen, Germany.


License
=======

``zopyx.multieventcalendar`` is published under the Zope Public License (ZPL 2.1)

Known issues
============

- ``zopyx.multieventcalendar`` does not support the standard Plone calendar portlet.
  (only the default date will be shown within the calendar portlet).
- no i18n support
- european date format hardcoded within templates 

To do
=====

- custom ``event_view.pt`` should be replace with a viewlet-based implementation




Contact
=======

| ZOPYX Ltd. & Co. KG
| c/o Andreas Jung, 
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com

