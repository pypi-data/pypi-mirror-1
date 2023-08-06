## Script (Python) "rss_manager_view_overview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName

request		= context.REQUEST
current_time	= DateTime()

portal_url      = getToolByName(container, 'portal_url')
portal_types    = getToolByName(container, 'portal_types')
archetype_tool	= getToolByName(container, 'archetype_tool')
wftool 		= getToolByName(container, 'portal_workflow')
portal          = portal_url.getPortalObject()

def process_feeds(refs):
	""" """
	startat = DateTime()
	summary = ""
	print "<p>"
	print "This is the Plone RSS News Manager interface which controls "
	print "updating of the local RSS feed database. All RSS News items "
	print "are stored within this folder and can be found using either "
	print "the supplied portlet or via site search functions.</p>"
	print "<p>The number of feed items detected is [<b>%d</b>]</p>" % len(refs)
	print "<p>Print we will now examine each feed in turn to see whether it "
	print "is due to be updated. If it is, we will then call the RSS grabber "
	print "to draw down the update and populate the local ZODB database.<p>"

	print "<table class='rssTable' width='100%'>"
	print "<tr><th>Feed Name</th><th>SQL Status</th><th>Update Freq</th><th>Age</th><th>Target</th><th>Action</th></tr>"
	for feed in refs:
		print "<tr>"
		print "<td><a href='%s'>%s</a></td>" % (feed.absolute_url(),feed.title)

		found = False
		history=context.objectIds(spec="rss_history")
		for entry in history:
			obj=getattr(context,entry)
			if obj.url == feed.remoteURL:
				found = True
				break

		if not found:
			print "<td>Creating</td>"
			kw			= {}
			kw['id']        	= context.generateUniqueId()
			kw['type_name'] 	= 'rss_history'
			kw['creators']  	= 'PloneRSS'
			kw['url']       	= feed.remoteURL
			kw['date']       	= 0
			kw['feedID']		= feed.id
			context.invokeFactory(**kw)

			found = False
			history=context.objectIds(spec="rss_history")
			for entry in history:
				obj=getattr(context,entry)
				if obj.url == feed.remoteURL:
					found = True
					break

			if not found:
				print "ERROR: failed to create history object!"
				return printed,printed

		else:
			print "<td>Found</td>"
		

		if feed.rssID <> obj.id: 
			kw = {}
			kw['id'] = feed.id;
			kw['rssID'] = obj.id   
			feed.update(**kw)

		age = int(float(current_time)-float(DateTime(obj.last_date)))
		mins = age/60
		freq = feed.frequency.split(" ")
		qty = freq[1][:3]
		freq = int(freq[0])
		if qty == 'day':
			freq = freq*3600*24
		elif qty == 'hou':
			freq = freq*3600
		else:
			freq = freq*60

		print "<td>%s</td><td>%d</td><td>%d</td>" % (feed.frequency,age,freq)

		review_state = wftool.getInfoFor(feed, 'review_state')
		try:
			publish = context.publish
		except:
			publish = "Yes"

		if publish == "Yes" and review_state <> "published":
			print "<td style='color: blue;'>Not Published</td>"
		elif not age or (age > freq):
			parsed	= context.feedparser(feed.remoteURL)
			kw			= {}
			kw['last_date']		= current_time
			kw['last_count']	= parsed['count']
			kw['last_status'] 	= parsed['status']
			kw['body']		= context.pickle_save(parsed)
			kw['url']       	= feed.remoteURL
			try:
				obj.update(**kw)
				print "<td style='color: red;'>Update</td>"
			except:
				xml={}
				xml['status'] = parsed['status']
				xml['count'] = parsed['count']
				xml['entries'] = []
				for i in parsed['entries']:
					entry={}
					entry['title'] 		= str(i['title'].encode("utf-8","replace")).replace("\\","")
					entry['description'] 	= str(i['description'].encode("utf-8","replace")).replace("\\","")
					entry['link'] 		= str(i['link'].encode("utf-8","replace")).replace("\\","")
					xml['entries'].append(entry)

				kw['body']		= context.pickle_save(xml)

				try:
					obj.update(**kw)
					print "<td style='color: red;'>Update</td>"
				except:
					print xml
		else:
			print "<td>Ok</td>"

		summary += "Feed=[%-40s] State=[%10s] Freq=[%-7s] Age=[%8d] Target=[%8d]\n" % (feed.title,review_state,feed.frequency,age,freq)

		print "</tr>"
	print "</table>"
	print "<p>At this point, all the RSS feeds should be up-to-date so now we're going to go through all "
	print "of the available feeds and see if any items that appear are new to us. For each new item we will "
	print "create a matching object in the local ZODB.<p>"
	print "<p>Note: items are keyed on the [title] and [link] fields.</p>"

	print "<table class='rssTable' width='100%'>"
	print "<tr><th>URL of RSS Feed</th><th>New</th><th>Total</th><th>Status</th></tr>"

	for entry in context.objectIds(spec="rss_history"):
		feed = getattr(context,entry)

		newitems = 0
		lines = ''
		try:
			parsed	= context.pickle_load(str(feed.body))
			if not parsed.has_key('entries'): continue
		except:
			continue

		items = parsed['entries']
		for item in items:
			kw	= {}
			key = context.calculate_md5(item['link'],item['title'])
			res = context.portal_catalog.searchResults(portal_type='rss_item',getRssKey=key)

			if not(len(res)):
				newitems += 1
				kw['id']        = context.generateUniqueId()
				kw['type_name']		= 'rss_item'
				kw['creators'] 		= 'PloneRSS'
				kw['remoteUrl']        	= item.get('link','[No Link]')
				kw['title']        	= item.get('title','[No Title]')
				kw['description']    	= item.get('description','[No Description]')
				kw['rssKey']       	= key
				kw['rssID']        	= str(feed.id)
				try:
					d = item.get('modified_parsed')[:6]
					kw['rssDate'] = DateTime('%02d-%02d-%04d %02d:%02d:%02d' % (d))
				except:
					kw['rssDate'] = current_time

				context.invokeFactory(**kw)
				obj = getattr(context,kw['id'])
				context.portal_workflow.doActionFor(obj,'publish',comment='News item imported by PloneRSS')
				lines = lines + "<tr><td colspan='4'><span style='color: red;'>Created</span> &nbsp; - &nbsp;"
				lines = lines + "<span style='color: gray;'><a href='%s'>%s</a></span></td>" % (obj.absolute_url(),kw['title'])	
				summary += "Created: %s\n" % item['title']
		print "<tr><td><a href='%s'>%s</a></td><td>%d</td><td>%d</td><td>%s</td></tr>" % (feed.url,feed.url[:60],newitems,len(items),feed.last_status)
		print lines

	print "</table>"
	taken = (DateTime().time - startat.time)*100000
	print "<p>Time Taken (%.02f) secs</p>" % (taken)
	
	print "<H3>Checking expiration status:</H3>"
	print "<UL>"

	summary += "\n"
	startat=DateTime()
	ids = []
	tot = 0
	for feed in refs:
		try:
			maxage = feed.maxage
			age = maxage.split(" ")
			units = int(age[0])
			if age[1][0]=='w':	units = units * 7
			if age[1][0]=='m':	units = units * 30
		except:
			units = 9999 * 30

		results = context.portal_catalog.searchResults(portal_type='rss_item',getRssID=feed.rssID)
		total = len(results)

		maxage = current_time-units
		results = context.portal_catalog.searchResults(portal_type='rss_item',getRssID=feed.rssID,created={"query":maxage,"range":"max"})

		for result in results: ids.append(result.id)

		print "<LI>Expiring <b>%d</b> of <b>%d</b> items from <b>%s</b></LI>" % (len(results),total,feed.title)
		summary += "Expiring (%5d) of (%5d) items from (%s)\n" % (len(results),total,feed.title)
		tot += total
	
	ids=ids[:10]
	print "</UL>"

	context.manage_delObjects(ids)
	taken = (DateTime().time - startat.time)*100000
	print "<p>Time Taken (%.02f) secs</p>" % (taken)
	summary += "\nTime Taken (%.02f) secs\n" % (taken)

	print "<h2>Help Information</h2>"
	print "<p>Use the above information to determine the health of your RSS feeds. If you see for example "
	print "a status that's not set to '200', it means that the last attempt to recover that feed failes and "
	print "the number listed is the HTTP error code for the failure. [Click on the feed URL to debug]</p>"
	print "<p>'Not Published' in the top table means that someone has added a feed and it hasn't yet been "
	print "published by a reviewer. (or of course they've not 'submitted' it) If you want to let people "
	print "add feeds without any sort of review process, set the global 'Require Publication' flag to "
	print "'No' by editing this page.</p>"

	return printed,summary

instances = context.portal_catalog.searchResults(portal_type='rss_instance')
refs = []
for instance in instances:
	obj = instance.getObject()
	feeds = obj.getReferenceImpl('feeds')

	for feed in feeds:
		ref = feed.getTargetObject()
		if not ref in refs: refs.append(ref)

#
verbose,summary = process_feeds(refs)
#
user 	= str(request['AUTHENTICATED_USER'])
#
if user == "cron": return summary
return verbose

