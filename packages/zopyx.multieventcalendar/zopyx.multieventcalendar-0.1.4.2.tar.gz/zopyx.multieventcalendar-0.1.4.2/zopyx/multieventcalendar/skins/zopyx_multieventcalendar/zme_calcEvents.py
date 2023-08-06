
# pre-calc some datastructure for printing month calendars
# - list of pairs (year, month)
# - dict mapping a date string (YYYY/DD/MM) -> list of Event objects

import calendar

now = DateTime()
R = context.REQUEST

month = R.get('month', now.month())
year = R.get('year', now.year())
months = R.get('months', 1)
mode = R.get('mode', 'month')
subject = R.get('subject', None)
no_flatten = R.get('no_flatten', 0)
restrict_to_folder = R.get('restrict_to_folder', 0)

startDate = DateTime('%d/%d/1 00:00:00' % (year, month))

ranges = []

endMonth = month + months - 1
if endMonth > 12:
    year += 1
    endMonth = endMonth % 12 + 1

weekday, numDays = calendar.monthrange(year, endMonth)
endDate = DateTime('%d/%d/%d 23:59:59' % (year, endMonth, numDays))

for i in range(int(endDate-startDate -1)):
    d = (startDate + i)
    tp = (d.year(), d.month())
    if not tp in ranges:
        ranges.append(tp)

query = {'portal_type' : ('Event', )}
if restrict_to_folder:
    query.update({'path' : '/'.join(context.getPhysicalPath())})

if subject is not None:
    query.update({'Subject' : subject})


brains = context.portal_catalog(**query)

events = {}

for b in brains:
    event = b.getObject()
    dates = [(event.start(), event.end())]
    for i in range(1, 6):
        start = event.getField('date%dStart' % i).getAccessor(event)()
        end = event.getField('date%dEnd' % i).getAccessor(event)()
        if end is None:
            end = start
        dates.append((start, end))

    count = 0
    for start, end in dates:

        if count == 0:
            title = event.Title()
        else:
            title = event.getField('date%dText' % count).getAccessor(event)()

        count += 1

        if start is None and end is None: 
            continue

        if startDate <= start and end <= endDate:

            wholeDay = False
            if start.strftime('%Y/%m/%d') != end.strftime('%Y/%m/%d'):
                wholeDay = True
            elif start.strftime('%H:%M') == '00:00' and end.strftime('%H:%M') == '00:00':
                wholeDay = True

            if no_flatten:
                event_classes = []
                for subject in event.Subject():
                    event_classes.append('event-subject-%s' % subject.lower())

                d_s = start.strftime('%Y/%m/%d')
                if not events.has_key(d_s):
                    events[d_s] = []

                events[d_s].append({'event' : event,
                                    'title' : title,
                                    'url'   : event.absolute_url(),
                                    'uid'   : event.absolute_url() + str(start) + str(end),
                                    'start' : start,
                                    'end' : end,
                                    'whole_day' : wholeDay,
                                    })

            else:   

                for i in range(int(end - start) + 1):
                    d = start + i
                    d_s = d.strftime('%Y/%m/%d')

                    if not events.has_key(d_s):
                        events[d_s] = []

                    event_classes = []
                    for subject in event.Subject():
                        event_classes.append('event-subject-%s' % subject.lower())
                    event_classes.append(wholeDay and 'event-wholeday' or 'event-notwholeday')

                    events[d_s].append({'event' : event,
                                        'title' : title,
                                        'url'   : event.absolute_url(),
                                        'class' : ' '.join(event_classes),
                                        'start' : start,
                                        'end' : end,
                                        })
 
return (ranges, events)
