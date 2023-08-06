## Script (Python) "rss_fetchsearch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
#
from Products.CMFCore.utils import getToolByName
#
portal_url      = getToolByName(container, 'portal_url')
portal          = portal_url.getPortalObject()
folder		= context
res 		= []
if not context.isPrincipiaFolderish: 
	folder = context.aq_explicit.getParentNode()

while folder:
	results = folder.contentValues( filter={'portal_type':'rss_instance', 'review_state': 'published' }, )
	if results:
		for result in results: 
			if result.active == "Yes": 
				res.append(result)
		if len(res): break

	if folder == portal: break
	folder = folder.aq_explicit.getParentNode()
	
ids=[]
for instance in res:
	refs = instance.getReferenceImpl('feeds')
	for ref in refs:
		feed = ref.getTargetObject()
		ids.append(feed.rssID)

print "search?portal_type=rss_item&sort_on=getRssDate&sort_order=reverse"
for id in ids:
	print "&getRssID:list=%s" % id
return printed
