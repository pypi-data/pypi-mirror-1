# -*- coding: utf-8 -*-
"""
Boxes for books

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements, score_entity
from cubicweb.web.box import EntityBoxTemplate
from cubicweb.web.htmlwidgets import SideBoxWidget, BoxLink

def has_isbn(entity):
    return entity.isbn13 is not None

class BookSeeAlso(EntityBoxTemplate):
    __regid__ = 'book_seealso_box'
    __select__ = EntityBoxTemplate.__select__ & implements('Book') & score_entity(has_isbn)
    order = 25

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        isbn = entity.isbn13 or u''
        box = SideBoxWidget(self._cw._('This book on other sites'), 
                            'book_sites%i' % entity.eid)
        box.append(BoxLink('http://openlibrary.org/isbn/%s' % isbn, 'OpenLibrary'))
        box.append(BoxLink('http://books.google.com/books?q=isbn:%s' % isbn, 'Google Books'))
        box.append(BoxLink('http://www.amazon.com/gp/search/ref=sr_adv_b/?field-isbn=%s' % isbn, 'Amazon Books'))
        self.w(box.render())
