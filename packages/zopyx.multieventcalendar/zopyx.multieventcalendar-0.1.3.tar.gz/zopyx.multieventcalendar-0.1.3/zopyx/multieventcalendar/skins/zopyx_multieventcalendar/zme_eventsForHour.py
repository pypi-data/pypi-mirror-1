##parameters=events, date, hour

startDate = DateTime('%s 00:00:00' % date.strftime('%Y-%m-%d'))
endDate = DateTime('%s 23:59:59' % date.strftime('%Y-%m-%d'))

d1 = DateTime('%s %02d:00:00' % (date.strftime('%Y-%m-%d'), hour))
d2 = DateTime('%s %02d:59:59' % (date.strftime('%Y-%m-%d'), hour))

lst = []

for e in events:

    if e.start <= startDate and e.end >= endDate:
        continue

    if d1 <= e.start and e.start <= d2:
        lst.append(e) 

return lst
