from yams.buildobjs import (EntityType, SubjectRelation, ObjectRelation,
                            String, Int, Date)
try:
    from yams.buildobjs import RichString
except ImportError:
    from cubicweb.schema import RichString

_ = unicode

class Book(EntityType):
    title = String(required=True, fulltextindexed=True, indexed=True,
                 maxsize=128, description=_('book title'))
    isbn10 = String(fulltextindexed=True, indexed=True,
                 maxsize=10, description=_('Old International Standard Book Number'))
    isbn13 = String(fulltextindexed=True, indexed=True,
                 maxsize=13, description=_('New International Standard Book Number'))
    pages = Int()
    publish_date = Date()
    language = String(fulltextindexed=True, indexed=True, maxsize=50)
    summary = String(fulltextindexed=True, indexed=True,
                    description=_('Short summary of the book'))
    content = String(fulltextindexed=True, indexed=True)
    authors = SubjectRelation('Person', cardinality='**')
    publisher = SubjectRelation('Editor', cardinality='*1')
    editor = SubjectRelation('Person', cardinality='**')
    collection = SubjectRelation('Collection', cardinality='*1')
    has_cover = SubjectRelation('Image', cardinality='**', composite='subject')

class Collection(EntityType):
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=50)
    has_collection = ObjectRelation('Editor', cardinality='**')

class Editor(EntityType):
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=50)
    has_address = SubjectRelation('PostalAddress', cardinality='*1')

