from plone.indexer import indexer

from collective.blogging.interfaces import IEntryMarker

@indexer(IEntryMarker)
def year(obj):
    date = obj.getEffectiveDate() or obj.created()
    if date:
        return date.year()

@indexer(IEntryMarker)
def month(obj):
    date = obj.getEffectiveDate() or obj.created()
    if date:
        return date.month()
