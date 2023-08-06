from zope.app.schema.vocabulary import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements

class AddableContentTypes(object):
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        context = getattr(context, 'context', context)
        omit = context
        items = [ctype for ctype in context.getAllowedTypes() 
                 if ctype.id not in context.getNotAddableTypes()]
        items.sort(lambda x,y: cmp(x.Title(), y.Title()))
        items = [SimpleTerm(ctype, ctype.getId(), ctype.Title()) for ctype in items]
        return SimpleVocabulary(items)
        
AddableContentTypesFactory = AddableContentTypes()
