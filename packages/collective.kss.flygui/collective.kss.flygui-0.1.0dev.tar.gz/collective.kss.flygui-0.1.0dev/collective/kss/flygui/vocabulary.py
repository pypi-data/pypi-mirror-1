from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.schema.vocabulary import IVocabularyFactory

from Products.CMFCore.utils import getToolByName

class PortalTypesVocabulary(object):
    """Vocabulary factory listig portal types
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        ttool = getToolByName(context, 'portal_types', None)

        items = [
            SimpleTerm(t, t, "%s [%s]" % (ttool[t].Title(), ttool[t].getId()))
            for t in ttool.listContentTypes()]
        return SimpleVocabulary(items)

PortalTypesVocabularyFactory = PortalTypesVocabulary()