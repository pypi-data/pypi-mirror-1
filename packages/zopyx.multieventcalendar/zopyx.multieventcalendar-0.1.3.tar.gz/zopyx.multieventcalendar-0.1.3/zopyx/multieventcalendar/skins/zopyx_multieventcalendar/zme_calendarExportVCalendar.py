

r = list()
write=r.append

context.REQUEST.set('no_flatten' , 1)
ranges, eventD = context.zme_calcEvents()
calname = context.Title()
try:
    relcalid = context.UID()
except AttributeError:
    relcalid = context.portal_url.getPortalObject().getId()

write('BEGIN:VCALENDAR')
write('VERSION:2.0')
write('X-WR-CALNAME:%s' % calname.upper())
write('PRODID:-//Plone 3.0\, Inc//(C) ZOPYX Ltd & Co. KG//EN')
write('X-WR-RELCALID:%s'%relcalid)
write('X-WR-TIMEZONE:Europe/Berlin')
write('CALSCALE:GREGORIAN')
write('METHOD:PUBLISH')

for datestr, event_items in eventD.items():

    print datestr, event_items

    for d in event_items:

        ev = d['event']
        start = d['start']
        end = d['end']
        startWholeDay = False
        endWholeDay = False
        if start.strftime('%H:%M') == '00:00':
            startWholeDay = True
        if end.strftime('%H:%M') == '00:00':
            endWholeDay = True

#        if start.strftime('%Y/%m/%d') != end.strftime('%Y/%m/%d'):
#            wholeDay = True
#        elif start.strftime('%H:%M') == '00:00' and end.strftime('%H:%M') == '00:00':
#            wholeDay = True

        write('BEGIN:VEVENT')
        write('UID:%s' % d['uid'])
        write('DTSTAMP;TZID=Europe/Berlin:%s' % start.strftime('%Y%m%dT%H%M%S'))

        if startWholeDay:
            write('DTSTART;VALUE=DATE:%s' % start.strftime('%Y%m%d'))
        else:
            write('DTSTART:%s' % start.strftime('%Y%m%dT%H%M%S'))

        if endWholeDay:
            write('DTEND;VALUE=DATE-TIME:%s' % end.strftime('%Y%m%dT235969Z'))
        else:
            write('DTEND:%s' % end.strftime('%Y%m%dT%H%M%S'))

#        if wholeDay:
#            write('DTSTART;VALUE=DATE:%s' % start.strftime('%Y%m%d'))
#            write('DTEND;VALUE=DATE:%s' % end.strftime('%Y%m%d'))
#        else:
##            write('DTSTART;TZID=Europe/Berlin:%s' % start.strftime('%Y%m%dT%H%M%S'))
##            write('DTEND;TZID=Europe/Berlin:%s' % end.strftime('%Y%m%dT%H%M%S'))
#            write('DTSTART:%s' % start.strftime('%Y%m%dT%H%M%S'))
#            write('DTEND:%s' % end.strftime('%Y%m%dT%H%M%S'))

        write('SUMMARY;CHARSET=UTF-8:%s' % d['title'])
        write('URL;VALUE=URI:%s' % d['url'])
        write('SEQUENCE:1')
        write('END:VEVENT')

write('END:VCALENDAR')


body = '\n'.join(r)

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/x-vcalendar')
context.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=plone-cal.ics')
context.REQUEST.RESPONSE.write(body)
