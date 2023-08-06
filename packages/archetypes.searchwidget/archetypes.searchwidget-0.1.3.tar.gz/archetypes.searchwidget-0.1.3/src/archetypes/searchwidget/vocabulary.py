
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName


def PloneTagsVocabulary(context):
    catalog = getToolByName(context, 'portal_catalog')
    return SimpleVocabulary.fromValues(catalog.uniqueValuesFor('Subject'))

