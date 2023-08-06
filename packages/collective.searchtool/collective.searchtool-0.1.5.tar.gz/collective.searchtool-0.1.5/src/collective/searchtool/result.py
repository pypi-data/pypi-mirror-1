
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from interfaces import ISearchResultItem


class ResultItem(object):

    implements(ISearchResultItem)

    def __init__(self, provider, brain):
        self.provider = provider
        self.brain = brain

    def render(self):
        utils = getToolByName(self.provider.context, 'plone_utils')
        properties = getToolByName(self.provider.context, 'portal_properties')
        try:
            item = getMultiAdapter(
                        (self.provider, self.brain), ISearchResultItem,
                        self.brain.Type)
            if getattr(item, 'custom_render', None):
                return item.custom_render()
            else:
                return item.render.__of__(self.provider)(
                            site_properties = properties['site_properties'],
                            brain = self.brain,
                            utils = utils, )
        except:
            return (ViewPageTemplateFile('result.pt').__of__(self.provider))(
                        site_properties = properties['site_properties'],
                        brain = self.brain,
                        utils = utils, )

