
from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory('archetypes.searchwidget')

from Products.CMFCore.utils import ContentInit
from Products.Archetypes.atapi import process_types, listTypes
from Products.CMFCore.permissions import AddPortalContent
from archetypes.searchwidget.widget import SearchWidget

def initialize(context):
    import demo

    PROJECTNAME = 'archetypes.searchwidget'
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = AddPortalContent,
        extra_constructors = constructors,
        ).initialize(context)

