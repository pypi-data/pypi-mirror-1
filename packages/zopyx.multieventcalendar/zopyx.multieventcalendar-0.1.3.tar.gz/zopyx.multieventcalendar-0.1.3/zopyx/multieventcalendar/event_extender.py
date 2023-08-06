################################################################
# zopyx.multieventcalendar
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################


from Products.Archetypes.public import CalendarWidget, StringWidget
from Products.Archetypes.public import DateTimeField,StringField
from archetypes.schemaextender.field import ExtensionField

class MyDateTimeField(ExtensionField, DateTimeField):
    """A trivial field."""

class MyStringField(ExtensionField, StringField):
    """A trivial field."""

from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import BooleanWidget
from Products.ATContentTypes.content.event import ATEvent

class EventExtender(object):
    adapts(ATEvent)
    implements(ISchemaExtender)

    fields = list()

    for i in range(1, 6):
        fields.append(
            MyStringField('date%dText' % i,
                        default=None,
                        schemata='MoreDates',
                        widget=StringWidget(label="Text additional date %d" % i,
                                            description='Another date directly related to this event, e. g. '
                                                        'registration or submission deadline. An associated extra event will be generated.',
                                            size=60,
                                            )
                             )
            )

        fields.append(
            MyDateTimeField('date%dStart' % i,
                           default=None,
                           index='DateIndex:schema',
                           schemata='MoreDates',
                           widget=CalendarWidget(label="Start date %d" % i,
                                                 description='Set start and end to the same date if this date has no duration'
                                                 )
                             )
            )

        fields.append(
            MyDateTimeField('date%dEnd' % i,
                           default=None,
                           index='DateIndex:schema',
                           schemata='MoreDates',
                           widget=CalendarWidget(label="End date %d" % i,
                                                 )
                             )
            )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

