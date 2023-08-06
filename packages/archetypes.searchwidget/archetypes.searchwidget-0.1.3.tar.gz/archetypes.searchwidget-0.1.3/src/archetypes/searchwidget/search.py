
from z3c.form.form import Form
from z3c.form.field import Fields
from z3c.form.button import buttonAndHandler
from zope.interface import implements

from plone.memoize.instance import memoize
from collective.searchtool.simple import SimpleSearch
from collective.searchtool.simple import SimpleSearchResult
from collective.searchtool.result import ResultItem
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.AdvancedQuery import MatchRegexp, In, Eq
from Products.CMFCore.utils import getToolByName

from archetypes.searchwidget.interfaces import ISearchFormWithTags
from archetypes.searchwidget.interfaces import ISearchWidgetProvider
from archetypes.searchwidget import MessageFactory as _


def copy(klass):
    class myklass(klass):
        pass
    return myklass

class SearchTagsForTypeForm(Form):
    label = _('Tags')
    portal_type = None
    result_data = []
    ignoreContext = True
    fields = Fields(ISearchFormWithTags)

    def query(self, data):
        query = None
        if self.portal_type:
            if type(self.portal_type) == list:
                query = In('portal_type', self.portal_type)
            elif type(self.portal_type) == str:
                query = Eq('portal_type', self.portal_type)
        if data['search_term'] and query:
            query = query & MatchRegexp('SearchableText', '*' + data['search_term'] + '*' )
        elif data['search_term'] and not query:
            query = MatchRegexp('SearchableText', '*' + data['search_term'] + '*' )
        if data['tags'] and query:
            query = query & In('Subjects', data['tags'])
        elif data['tags'] and not query:
            query = Eq('Subjects', data['tags'])
        return query

    @buttonAndHandler(_(u'Search'))
    def search(self, action):
        data, errors = self.extractData()
        if errors: return False

        query = self.query(data)
        if not query: return True

        catalog = getToolByName(self.context, 'portal_catalog')
        self.result_data = catalog.evalAdvancedQuery(query)
        return True


class SearchWidgetResult(SimpleSearchResult):
    __call__ = render = ViewPageTemplateFile('search_results.pt')

class SearchImages(SimpleSearch):
    implements(ISearchWidgetProvider)
    form = copy(SearchTagsForTypeForm)
    form.label = _(u'Images')
    form.portal_type = 'Image'
    results = SearchWidgetResult

class SearchFiles(SimpleSearch):
    implements(ISearchWidgetProvider)
    form = copy(SearchTagsForTypeForm)
    form.label = _(u'Files')
    form.portal_type = 'File'
    results = SearchWidgetResult
    
class SearchDocuments(SimpleSearch):
    implements(ISearchWidgetProvider)
    form = copy(SearchTagsForTypeForm)
    form.label = _(u'Documents')
    form.portal_type = ['Document', 'News item', 'Event']
    results = SearchWidgetResult
    


class ImageResultItem(ResultItem):
    render = ViewPageTemplateFile('searchresult_image.pt')

#class FileResultItem(ResultItem):
#    render = ViewPageTemplateFile('searchresult_file.pt')

#class DocumentResultItem(ResultItem):
#    render = ViewPageTemplateFile('searchresult_document.pt')

#class EventResultItem(ResultItem):
#    render = ViewPageTemplateFile('searchresult_event.pt')

#class NewsItemResultItem(ResultItem):
#    render = ViewPageTemplateFile('searchresult_newsitem.pt')



