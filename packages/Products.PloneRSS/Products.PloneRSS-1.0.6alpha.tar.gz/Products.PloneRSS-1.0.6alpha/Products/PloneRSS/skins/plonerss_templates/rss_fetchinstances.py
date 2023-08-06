## Script (Python) "rss_fetchinstances"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFCore.utils import getToolByName
#
portal_url      = getToolByName(container, 'portal_url')
portal          = portal_url.getPortalObject()

folder = context
if not context.isPrincipiaFolderish:
	folder = context.aq_explicit.getParentNode()

res = []

while folder:
	results = folder.contentValues( filter={'portal_type':'rss_instance', 'review_state': 'published' }, )
	sort_on = (('effective', 'cmp', 'desc'), )
	if results:
		results = sequence.sort(results, sort_on)
		for result in results:
			if result.active == "Yes": res.append(result)
		if len(res):
			return res

	if folder == portal:
		return res

	folder = folder.aq_explicit.getParentNode()
	
return res
