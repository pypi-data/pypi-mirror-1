##parameters=datestr

REQUEST=context.REQUEST

id = context.generateUniqueId('Event')
o = context.restrictedTraverse('portal_factory/Event/' + id)
REQUEST.RESPONSE.redirect(o.absolute_url() + '/edit?startDate=%s&endDate=%s' % (datestr, datestr))
