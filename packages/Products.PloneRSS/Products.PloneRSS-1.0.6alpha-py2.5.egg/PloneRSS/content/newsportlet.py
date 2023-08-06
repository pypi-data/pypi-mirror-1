from zope import schema
from zope.schema import Int
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.Archetypes.debug import log

class RSSInstanceVocabulary(object):
	""" return a list of current RSS instances """
	implements(IVocabularyFactory)

	def __call__(self, context):
		context = getattr(context, 'context', context)
		catalog = getToolByName(context, 'portal_catalog')
		instances = catalog(portal_type='rss_instance',review_state='published')
		items = []
		for instance in instances:
			obj = instance.getObject()
			items.append((obj.title,obj.id))

		items.sort()
		return SimpleVocabulary.fromItems(items)

RSSInstanceVocabularyFactory = RSSInstanceVocabulary()

class IRSSPortlet(IPortletDataProvider):

	count = schema.Int(title=_(u'Number of items to display'),
		description=_(u'How many items to list.'),
		required=True,
		default=5)

	state = schema.Tuple(title=_(u"Workflow state"),
		description=_(u"Items in which workflow state to show."),
		default=('published', ),
		required=True,
		value_type=schema.Choice(
		vocabulary="plone.app.vocabularies.WorkflowStates")
		)

	instance = schema.Choice(
		title=_(u"RSS Instance"),
		description=_(u'Which RSS instance should be displayed'),
		required=True,
		vocabulary="plone.app.vocabularies.RSSInstances"
		)

class Assignment(base.Assignment):
	implements(IRSSPortlet)

	def __init__(self, count=5, state=('published', ),instance=''):
		self.count = count
		self.state = state
		self.instance = instance

	@property
	def title(self):
		return _(u"RSS News")

class Renderer(base.Renderer):

	_template = ViewPageTemplateFile('newsportlet.pt')
	_results = []
	_title = "RSS News"

	@ram.cache(render_cachekey)
	def render(self):
		return xhtml_compress(self._template())

	@property
	def available(self):
		return len(self._data())

	def published_news_items(self):
		return self._data()

	def all_news_link(self):
		portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
		portal_url = portal_state.portal_url()
		portal = portal_state.portal()
      
		if 'news' in portal.objectIds():
			return '%s/news' % portal_url
		else:
			return '%s/news_listing' % portal_url

	@memoize
	def _data(self):
		context = aq_inner(self.context)
		catalog = getToolByName(context, 'portal_catalog')
		limit = self.data.count
		state = self.data.state
		items=[]
		instances = catalog(id=self.data.instance)
		if len(instances)<>1: return []
		instance = instances[0].getObject()
		ids=[]
		refs = instance.getReferenceImpl('feeds')
		for ref in refs:
			feed = ref.getTargetObject()
			ids.append(feed.rssID)

		self._title = instance.title
		return catalog(portal_type='rss_item',sort_on='getRssDate',sort_order='reverse',getRssID=ids,review_state=state,sort_limit=limit)[:limit]


	def title(self):
		return self._title

class AddForm(base.AddForm):
	form_fields = form.Fields(IRSSPortlet)
	label = _(u"Add News Portlet")
	description = _(u"This portlet displays recent News Items.")

	def create(self, data):
		return Assignment(count=data.get('count', 5), state=data.get('state', ('published',)),instance=data.get('instance',''))

class EditForm(base.EditForm):
	form_fields = form.Fields(IRSSPortlet)
	label = _(u"Edit News Portlet")
	description = _(u"This portlet displays recent News Items.")
