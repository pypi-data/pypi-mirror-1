## Script (Python) "rss_document_wrap"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text
##title=
##
if ":rss_feed:" in text:
	output = ''
	instances=context.rss_fetchinstances()
	for instance in instances:
		display=context.rss_feedcount(instance)
		count=int(instance.count)
		output = output + "<h5>%s</h5>" % instance.title
		for obj in context.rss_fetchfeeds(instance):

			output = output + '<div class="portletItem odd">'
			output = output + '	<div class="rssWarn">%s</div>' % obj
			output = output + '</div>'
	
		output = output + "<ul>"
		items = context.rss_fetchitems(instance)[:count]
		for obj in items:
			item = obj.getObject()
			output = output + '<li><img src="rss.gif">&nbsp;<a href="%s">%s</a>' % (obj.getURL(),item.title ) 
			output = output + '&nbsp;<span class="discreet">%s</span></li>' %  context.toLocalizedTime(item.rssDate) 

		output = output + '<a href="%s">%s</a></ul><P>&nbsp;</P>' % (context.rss_fetchsearch(instance),'More News...')

	text = text.replace(':rss_feed:',output)

return text
