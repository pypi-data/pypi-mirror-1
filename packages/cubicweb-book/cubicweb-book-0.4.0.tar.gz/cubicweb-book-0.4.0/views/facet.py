from cubicweb.selectors import implements
from cubicweb.web.facet import RangeFacet, DateRangeFacet, HasRelationFacet

class BookPagesFacet(RangeFacet):
    __regid__ = 'priority-facet'
    __select__ = RangeFacet.__select__ & implements('Book')
    rtype = 'pages'

class BookPubdateFacet(DateRangeFacet):
    __regid__ = 'pubdate-facet'
    __select__ = DateRangeFacet.__select__ & implements('Book')
    rtype = 'publish_date'

class HasCoverFacet(HasRelationFacet):
    __regid__ = 'hascover-facet'
    __select__ = HasRelationFacet.__select__ & implements('Book')
    rtype = 'has_cover'
