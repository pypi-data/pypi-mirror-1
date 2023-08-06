
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getMultiAdapter

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest

from Acquisition import aq_inner
from Products.Five.traversable import  FiveTraversable

from interfaces import ISearchProvider


class SearchHandler(object):

    implements(ITraversable)
    adapts(Interface, IHTTPRequest)

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

    def traverse(self, name, ignored):
        return getMultiAdapter((self.context, self.request, None),
                    ISearchProvider, name)

