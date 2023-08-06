
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import registerType
from Products.ATContentTypes.content.schemata import ATContentTypeSchema as BaseSchema
from Products.ATContentTypes.content.base import ATCTContent as BaseContent

from archetypes.searchwidget.widget import SearchWidget

schema = BaseSchema.copy() +  Schema((

    ReferenceField('single',
        multiValued=0,
        allowed_types=('Document','File', 'RefBrowserDemo'),
        relationship='Rel1',
        widget=SearchWidget(
            description='This is the first field. Pick an object.')),

    ReferenceField('multi',
        multiValued=1,
        allowed_types=('Document','File', 'RefBrowserDemo'),
        relationship='Rel1',
        widget=SearchWidget(
            description='This is the first field. Pick an object.')),
    ))


class SearchWidgetDemo(BaseContent):
    """
    Demo from archetypes.searchwidget
    """
    content_icon = "document_icon.gif"
    schema = schema

registerType(SearchWidgetDemo, 'archetypes.searchwidget')

