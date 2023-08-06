
from zope.schema import TextLine
from zope.interface import Interface
from zope.contentprovider.interfaces import IContentProvider

from collective.searchtool import MessageFactory as _


class ISearchLayer(Interface):
    """ Search Tool layer"""

class ISearchProvider(IContentProvider):
    """ Marker interface that marks browser pages or
        other content provider that promisess searchform
        functionalities """

class ISearchResultItem(Interface):
    """ Marker instance that marks classes that are used 
        to render individual result item"""


class ISimpleSearchForm(Interface):
    """ simple search form (/@@search) """

    search_term = TextLine(
        required    = False,
        title       = _(u'Search term'),)
        #description = _(
        #    u'Automatic "and" queries, eg: "car citroen". Search will returns'
        #    u'pages that include all of your search terms.'))


