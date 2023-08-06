
from zope.interface import Interface
from zope.schema import TextLine, Set, Choice
from collective.searchtool.interfaces import ISearchProvider
from archetypes.searchwidget import MessageFactory as _


class ISearchFormWithTags(Interface):

    search_term = TextLine(
        required = False,
        title = _(u'Search term'))
    tags = Choice(
        required = False,
        title = _(u'Tags'),
        vocabulary = "plone tags")

class ISearchWidgetProvider(ISearchProvider):
    """ marker for our search providers """

