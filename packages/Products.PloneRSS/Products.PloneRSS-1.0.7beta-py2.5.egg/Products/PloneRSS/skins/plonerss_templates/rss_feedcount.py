## Script (Python) "rss_feedcount"
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
refs = instance.getReferenceImpl('feeds')
return len(refs)
