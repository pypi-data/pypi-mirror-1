import urllib

from zope.interface import implements
from zope.component import getUtility

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder

from plone.registry.interfaces import IRegistry

from z3c.formwidget.query.interfaces import IQuerySource

from collective.gtags.interfaces import ITagSettings

class TagsSource(object):
    implements(IQuerySource)

    def __init__(self, context, allow_uncommon=None):
        settings = getUtility(IRegistry).for_interface(ITagSettings)
        
        if allow_uncommon is None:
            self.allow_uncommon = settings.allow_uncommon
        else:
            self.allow_uncommon = allow_uncommon

        self.vocab = SimpleVocabulary.fromItems([
                (self._quote(value), unicode(value)) for value in settings.tags
            ])
    
    def __contains__(self, value):
        
        # If we allow uncommon terms, then anything is in the vocabulary
        if self.allow_uncommon:
            return True
        
        return self.vocab.__contains__(value)
        
    def __iter__(self):
        return self.vocab.__iter__()
    
    def __len__(self):
        return self.vocab.__len__()
    
    def getTerm(self, value):
        if self.allow_uncommon:
            return SimpleTerm(value=value, token=self._quote(value))
        else:
            return self.vocab.getTerm(value)
    
    def getTermByToken(self, token):
        if self.allow_uncommon:
            return SimpleTerm(value=self._unquote(str(token)), token=token)
        else:
            return self.vocab.getTermByToken(token)
    
    def search(self, query_string):
        q = query_string.lower()
        return [term for term in self.vocab if q in term.token.lower()]
    
    def _quote(self, value):
        return urllib.quote_plus(value.encode('utf-8', 'ignore'))
    
    def _unquote(self, token):
        return unicode(urllib.unquote_plus(token), encoding='utf-8')
    
class TagsSourceBinder(object):
    implements(IContextSourceBinder)

    def __init__(self, allow_uncommon=None):
        self.allow_uncommon = allow_uncommon

    def __call__(self, context):
        return TagsSource(context, self.allow_uncommon)