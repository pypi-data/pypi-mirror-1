
from zope.interface import implements
from zope.component import getMultiAdapter

from z3c.form.form import Form
from z3c.form.field import Fields
from z3c.form.button import buttonAndHandler
from z3c.form.interfaces import IFormLayer
from plone.z3cform import z2
from plone.memoize.instance import memoize

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.AdvancedQuery import MatchRegexp, Or, And

from collective.searchtool import MessageFactory as _
from collective.searchtool.interfaces import ISearchResultItem
from collective.searchtool.interfaces import ISearchProvider
from collective.searchtool.interfaces import ISimpleSearchForm


class SimpleSearchResult(BrowserView):
    __call__ = render = ViewPageTemplateFile('simple_results.pt')

    def __init__(self, context, request, view=None):
        self.context = aq_inner(context)
        self.request = request
        self.__parent__ = view

        self.syndication = getToolByName(self.context, 'portal_syndication')
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
    
    def render_item(self, item):
        return getMultiAdapter((self.__parent__, item), ISearchResultItem).render()


class SimpleSearchForm(Form):
    label = _('Simple search')
    ignoreContext = True
    fields = Fields(ISimpleSearchForm)
    result_data = []

    @buttonAndHandler(_(u'Search'))
    def search(self, action):
        data, errors = self.extractData()
        if errors: return False
        if not data['search_term']: return True 
        catalog = getToolByName(self.context, 'portal_catalog')
        self.result_data = catalog.evalAdvancedQuery(
            MatchRegexp('SearchableText', '*' + data['search_term'] + '*' ))
        return True


class SimpleSearch(BrowserView):
    implements(ISearchProvider)
     
    form = SimpleSearchForm
    results = SimpleSearchResult
    
    def __init__(self, context, request, view=None):
        self.context = aq_inner(context)
        self.request = request
        self.__parent__ = view

        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()

    def __call__(self):
        return self.render()

    def render(self):
        z2.switch_on(self, request_layer=IFormLayer)
        form = self.form(self.context.aq_inner, self.request)
        results = self.results(self.context.aq_inner, self.request, self)
        html = form()
        results.result_data = form.result_data
        return '<div class="searchPage">'+html+'</div>' + \
               '<div class="seachResultPage">'+results.__of__(self.context)()+'</div>'

    @property
    def label(self):
        return self.form.label

    def update(self):
        pass

    def getPhysicalPath(self):
        """ needed so its possible to do path search over catalog 
              ExtendedPathIndex needs it ... maybe a bug  """
        return self.context.getPhysicalPath()


class PloneSimpleSearch(SimpleSearch):

    def render(self):
        z2.switch_on(self, request_layer=IFormLayer)
        form = self.form(self.context.aq_inner, self.request)
        results = self.results(self.context.aq_inner, self.request, self)
        html = form()
        results.result_data = form.result_data
        results = results.__of__(self.context)()
        return ViewPageTemplateFile('simple_plone.pt').__of__(self.context)(
                                                                search_form=form,
                                                                search_results=results)


