
# return a list of date strings for the current week
# where request/date is possibly the first day. However
# always start with a monday.

date = DateTime(context.REQUEST.date)

# find monday
for i in range(0, -7, -1):

    refDate = date -i 
    dow = refDate.dow()
    if dow == 1: # Monday
        break

lst = []
for i in range(0, 7):
    lst.append(refDate + i)

return lst

