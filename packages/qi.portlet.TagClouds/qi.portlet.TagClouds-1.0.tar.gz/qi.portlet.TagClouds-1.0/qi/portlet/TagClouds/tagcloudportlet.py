import base64
from time import time

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize import ram

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from qi.portlet.TagClouds import TagCloudPortletMessageFactory as _

def _cachekey(method,self):
	#one hour cache
	return str(time() //  self.data.refreshInterval)

class SubjectsVocabulary(object):
	"""Vocabulary factory for subjects.
	This confuses me. I need this to work with non-english tags which seem to confuse zope vocabularies...
	Need to find a more elegant way of dealing with the issue ;)
	"""
	implements(IVocabularyFactory)
	
	def __call__(self, context):
		catalog = getToolByName(context, 'portal_catalog')
		subjects = list(catalog.uniqueValuesFor('Subject'))
		subjects.sort();
		terms = [SimpleTerm(value=k, token=base64.b64encode(k), title=k) for k in subjects]
		return SimpleVocabulary(terms)

SubjectsVocabularyFactory = SubjectsVocabulary()

class ITagCloudPortlet(IPortletDataProvider):
	"""A portlet

	It inherits from IPortletDataProvider because for this portlet, the
	data that is being rendered and the portlet assignment itself are the
	same.
	"""
	portletTitle = schema.TextLine(
		title = _(u"Portlet title"),
		description = _(u"The title of the tagcloud."),
		required = True,
		default = u"Tag Cloud"
		)
	
	levels = schema.Int(
		title = _(u"Number of different sizes"),
		description = _(u"This number will also determine the biggest size."),
		required = True,
		min = 1,
		max = 6,
		default = 5
		)

	shouldRestrictBySubject = schema.Bool(
			title = _(u"label_portletTagCloud_restrict_subjects", default=u"Restrict by keywords"),
			description = _(u"desc_portletTagCloud_restrict_subjects",
							default = u"If not checked all keywords will be searched"),
			default = False)

	restrictSubjects = schema.List(
		required = False,
		title = _(u"Restrict by keywords"),
		description = _(u"Restrict the cloud keywords by searching through items filed under these keywords"),
		value_type = schema.Choice(vocabulary='qi.portlet.TagClouds.subjects'),
		)

	shouldRestrictByType = schema.Bool(
			title = _(u"label_portletTagCloud_restrict_objects", default=u"Resctict by type"),
			description = _(u"desc_portletTagCloud_restrict_objects",
							default = u"If not checked all portal types will be searched"),
			default = False)

	restrictTypes = schema.List(
		required = False,
		title = _(u"Restrict by types"),
		description = _(u"Restrict the cloud keywords by searching through items of these types"),
		value_type = schema.Choice(vocabulary='plone.app.vocabularies.ReallyUserFriendlyTypes'),
		)

	refreshInterval = schema.Int(
		title = _(u"Refresh interval"),
		description = _(u"The maximum time in seconds for which the portal will cache the results. Be careful not to use low values."),
		required = True,
		min = 1,
		default = 3600,
		)

class Assignment(base.Assignment):
	"""Portlet assignment.

	This is what is actually managed through the portlets UI and associated
	with columns.
	"""

	implements(ITagCloudPortlet)
	
	def __init__(self, portletTitle="TagCloud", levels=5, shouldRestrictBySubject=True, restrictSubjects=[], shouldRestrictByType=True, restrictTypes=[],refreshInterval=3600):
		self.portletTitle = portletTitle
		self.levels = levels
		self.shouldRestrictBySubject = shouldRestrictBySubject
		self.restrictSubjects = restrictSubjects
		self.shouldRestrictByType = shouldRestrictByType
		self.restrictTypes = restrictTypes
		self.refreshInterval = refreshInterval

	@property
	def title(self):
		"""This property is used to give the title of the portlet in the
		"manage portlets" screen.
		"""
		return "Tag Cloud portlet"


class Renderer(base.Renderer):
	"""Portlet renderer.

	This is registered in configure.zcml. The referenced page template is
	rendered, and the implicit variable 'view' will refer to an instance
	of this class. Other methods can be added and referenced in the template.
	"""

	render = ViewPageTemplateFile('tagcloudportlet.pt')
	def __init__(self, context, request, view, manager, data):
		super(Renderer, self).__init__(context, request, view, manager, data)		
		self.portal_url = getToolByName(context, 'portal_url')()
		self.catalog = getToolByName(context, 'portal_catalog')
		self.putils = getToolByName(context, 'plone_utils')
		self.levels = data.levels
	
	@ram.cache(_cachekey)
	def getTags(self):
		tagOccs = self.getTagOccurrences()
		thresholds = self.getThresholds(tagOccs.values())
		tags = list(tagOccs.keys())
		tags.sort()
		res = []
		for tag in tags :
			d = {}
			size = self.getTagSize(tagOccs[tag], thresholds)
			if size == 0 :
				continue
			d["text"] = tag
			d["class"] = "cloud" + str(size)
			d["href"] = self.portal_url + "/search?Subject=" + tag
			res.append(d)
		return res
	
	def getPortletTitle(self):
		return self.data.portletTitle
	
	def getSearchSubjects(self):
		if (self.data.shouldRestrictBySubject) :
			result = self.data.restrictSubjects
		else:
			result = self.catalog.uniqueValuesFor('Subject')
		return result
	
	def getSearchTypes(self):
		if (self.data.shouldRestrictByType) :
			return self.data.restrictTypes
		else :
			return self.putils.getUserFriendlyTypes()
	
	def getTagOccurrences(self):
		types = self.getSearchTypes()
		tags = self.getSearchSubjects()
		tagOccs = {}
		for tag in tags :
			result = self.catalog.searchResults(Subject=tag, portal_type=types, review_state='published')			
			length = len(result)
			if length > 0 :
				tagOccs[tag] = length
		return tagOccs
			
	def getTagSize(self, tagWeight, thresholds):
		size = 0
		if tagWeight:
			for t in thresholds:
				size += 1
				if tagWeight <= t:
					break
		return size
	
	def getThresholds(self, sizes):
		if not sizes:
			return [1 for i in range(0, self.levels)]
		minimum =  min(sizes)
		maximum = max(sizes)
		#this algorithm was taken from Anders Pearson's blog: http://thraxil.com/users/anders/posts/2005/12/13/scaling-tag-clouds/
		return [pow(maximum - minimum + 1, float(i) / float(self.levels)) for i in range(0, self.levels)]
	
	@property
	def available(self):
		return self.getSearchTypes() and self.getSearchSubjects()
	
class AddForm(base.AddForm):
	"""Portlet add form.

	This is registered in configure.zcml. The form_fields variable tells
	zope.formlib which fields to display. The create() method actually
	constructs the assignment that is being added.
	"""
	form_fields = form.Fields(ITagCloudPortlet)

	def create(self, data):
		"""
		"""
		return Assignment(**data)

class EditForm(base.EditForm):
	"""Portlet edit form.

	This is registered with configure.zcml. The form_fields variable tells
	zope.formlib which fields to display.
	"""
	form_fields = form.Fields(ITagCloudPortlet)
