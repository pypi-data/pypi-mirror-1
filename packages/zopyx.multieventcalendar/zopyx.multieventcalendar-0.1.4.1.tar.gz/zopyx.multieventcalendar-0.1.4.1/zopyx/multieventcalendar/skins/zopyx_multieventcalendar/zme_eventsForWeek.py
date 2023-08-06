##parameters=firstDate

# return a list of events for next seven days

from Products.CMFPlone.utils import log

brains = context.portal_catalog(portal_type='Event')

lst = []

for i in range(0, 7):

    start = DateTime('%s 00:00:00' % (firstDate + i).strftime('%Y-%m-%d'))
    end = DateTime('%s 23:59:59' % (firstDate + i).strftime('%Y-%m-%d'))

    eventsForDate = []
    for b in brains:
        eventStart = b.start
        eventEnd = b.end

        if eventEnd < start or eventStart > end:
            continue 
        eventsForDate.append(b) 

    lst.append(eventsForDate)

return lst
