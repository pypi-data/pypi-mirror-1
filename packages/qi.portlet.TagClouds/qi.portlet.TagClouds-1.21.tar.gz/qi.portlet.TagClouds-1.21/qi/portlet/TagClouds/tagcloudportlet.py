import base64
from time import time
from operator import itemgetter

from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema
from zope.formlib import form
from zope.i18n import translate

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.layout.navigation.root import getNavigationRoot
from plone.memoize import ram

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import url_quote

from qi.portlet.TagClouds import TagCloudPortletMessageFactory as _

def _cachekey(method,self):
    #one hour cache
    lang = self.request.get('LANGUAGE', 'en')
    return hash((lang, time() // self.data.refreshInterval))

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

class StatesVocabulary(object):
    """Vocabulary factory for states in the default workflow
    """
    implements(IVocabularyFactory)
    
    def __call__(self,context):
        wt = getToolByName(context,'portal_workflow')
        id = wt.getDefaultChain()[0]
        defWf = wt.getWorkflowById(id)
        terms = [SimpleTerm(value=s.id,token=s.id,title=s.title) for s in defWf.states.objectValues()]
        return SimpleVocabulary(terms)
        
StatesVocabularyFactory = StatesVocabulary()

class ITagCloudPortlet(IPortletDataProvider):
    """
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

    count = schema.Int(
        title = _(u"Maximum number of shown tags."),
        description = _(u"If greater than zero this number will limit the tags shown."),
        required = True,
        min = 0,
        default = 0
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

    root = schema.Choice(
            title=_(u"Root node"),
            description=_(u"You may search for and choose a folder "
                          "to act as the root of the navigation tree. "
                          "Leave blank to use the Plone site root."),
            required=False,
            source=SearchableTextSourceBinder({'is_folderish' : True},
                                              default_query='path:'))
    wfStates = schema.List(
            required = True,
            title = _(u"Workflow states to show"),
            description = _(u"Which workflow states to include in the search."),
            value_type = schema.Choice(vocabulary='qi.portlet.TagClouds.states'),)

    refreshInterval = schema.Int(
        title = _(u"Refresh interval"),
        description = _(u"The maximum time in seconds for which the portal will cache the results. Be careful not to use low values."),
        required = True,
        min = 1,
        default = 3600,
        )

class Assignment(base.Assignment):
    """
    """

    implements(ITagCloudPortlet)
    
    def __init__(self, portletTitle="TagCloud", levels=5, count=0,shouldRestrictBySubject=True, restrictSubjects=[], shouldRestrictByType=True, restrictTypes=[],root=u"",wfStates=[],refreshInterval=3600):
        self.portletTitle = portletTitle
        self.levels = levels
        self.count = count
        self.shouldRestrictBySubject = shouldRestrictBySubject
        self.restrictSubjects = restrictSubjects
        self.shouldRestrictByType = shouldRestrictByType
        self.restrictTypes = restrictTypes
        self.wfStates = wfStates
        self.refreshInterval = refreshInterval
        self.root = root

    @property
    def title(self):
        """
        """
        return "Tag Cloud portlet"


class Renderer(base.Renderer):
    """
    """

    render = ViewPageTemplateFile('tagcloudportlet.pt')

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)       
        self.portal_url = getToolByName(context, 'portal_url')()
        self.catalog = getToolByName(context, 'portal_catalog')
        self.putils = getToolByName(context, 'plone_utils')
        self.levels = data.levels
        self.wfStates = data.wfStates
        self.count = data.count

    @ram.cache(_cachekey)
    def getTags(self):
        tagOccs = self.getTagOccurrences()
        # If count has been set sort by occurences and keep the "count" first
        
        if self.count:
            sortedOccs = sorted(tagOccs.items(), key=itemgetter(1),reverse=True)[:self.count]
            tagOccs = dict(sortedOccs)
            
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
            d["href"] = self.portal_url + "/search?Subject%3Alist=" + url_quote(tag)
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
            result = self.catalog.searchResults(Subject=tag, 
                portal_type=types, 
                review_state=self.wfStates,
                path=getNavigationRoot(self.context, relativeRoot=self.data.root))          
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
    """
    """
    
    form_fields = form.Fields(ITagCloudPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget

    def create(self, data):
        """
        """
        return Assignment(**data)

class EditForm(base.EditForm):
    """
    """
    form_fields = form.Fields(ITagCloudPortlet)
    form_fields['root'].custom_widget = UberSelectionWidget
