from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName

def getPingSites(context):
    pp = getToolByName(context, 'portal_pingtool', None)
    values = []
    if pp:
        values = tuple([(i.Title(), i.id) for i in pp.objectValues()])
    return SimpleVocabulary.fromItems(values)
