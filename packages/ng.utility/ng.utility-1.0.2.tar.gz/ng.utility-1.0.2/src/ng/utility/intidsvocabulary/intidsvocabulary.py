from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm

from zope.app.intid.interfaces import IIntIds
import zope.app.zapi

def IntIdsVocabulary(context):
    """IntIds utility vocabulary"""
    utils = zope.app.zapi.getUtilitiesFor(IIntIds, context)
    return SimpleVocabulary.fromValues(dict(utils).keys())
