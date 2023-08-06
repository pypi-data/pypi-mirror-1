## Script (Python) "rss_fetchfeeds"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=instance
##title=
##
from Products.CMFCore.utils import getToolByName

wftool = getToolByName(container, 'portal_workflow')

results = []
refs = instance.getReferenceImpl('feeds')
for ref in refs:
	feed = ref.getTargetObject()
	review_state = wftool.getInfoFor(feed, 'review_state')
	if review_state <> "published":
		icon="<img src='error_icon.gif' width='16' height='16' alt='error_icon.gif'>"
		results.append("<a href='%s'>%s&nbsp;%s</a> is [%s] and needs to be [published]" % (feed.absolute_url(),icon,feed.title,review_state))

return results
