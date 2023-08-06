from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.config import CACHE_TOOL_ID
from Products.CMFPlone import PloneMessageFactory as _


class HeaderSetVocabulary(object):
    """Vocabulary with all known headers sets.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        pcs=getToolByName(context, CACHE_TOOL_ID, None)
        if pcs is None:
            return SimpleVocabulary([])

        display_id=pcs.getDisplayPolicy().getId()
        headers=[(header.getId(), header.Title())
                for header in pcs.getHeaderSets(display_id)]
        headers.sort(key=lambda x: x[1])
        terms=[SimpleTerm(x[0], x[0], x[1]) for x in headers]
        terms.append(SimpleTerm(None, "none", _(u"No cache headers")))

        return SimpleVocabulary(terms)


HeaderSetVocabularyFactory = HeaderSetVocabulary()

