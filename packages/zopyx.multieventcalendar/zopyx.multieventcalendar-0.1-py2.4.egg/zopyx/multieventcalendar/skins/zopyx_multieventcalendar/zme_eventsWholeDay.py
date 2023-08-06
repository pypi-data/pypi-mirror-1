##parameters=events, date

startDate = DateTime('%s 00:00:00' % date.strftime('%Y-%m-%d'))

lst = []
for e in events:
    if e.start <= startDate: # event starts earler or equal to 00:00:00
        lst.append(e)
return lst
