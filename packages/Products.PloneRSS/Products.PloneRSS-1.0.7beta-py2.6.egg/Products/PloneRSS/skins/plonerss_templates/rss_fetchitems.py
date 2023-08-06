## Script (Python) "rss_fetchitems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=instance,state
##title=
##
#
ret=[]
ids=[]
refs = instance.getReferenceImpl('feeds')
for ref in refs:
	feed = ref.getTargetObject()
	ret.append(feed)
	ids.append(feed.rssID)

results = context.portal_catalog.searchResults(portal_type='rss_item',sort_on='getRssDate',sort_order='reverse',getRssID=ids,review_state=state)

return results
