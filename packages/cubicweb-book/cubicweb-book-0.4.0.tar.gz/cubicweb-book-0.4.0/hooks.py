# -*- coding: utf-8 -*-
"""
:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb import Binary
from cubicweb.selectors import implements
from cubicweb.server import hook

from cubes.book import olapi

def set_if_unset(entity, key, book, otherkey):
    if 'key' not in entity:
        if otherkey in book:
            value = book[otherkey]
            if isinstance(value, list):
                value = value[0]
            # NOTE: simplejson (v>=2.0.0) uses str for ascii strings
            entity[key] = unicode(value)


class BookCreationHook(hook.Hook):
    __regid__ = 'book_fetchinfo'
    __select__ = hook.Hook.__select__ & implements('Book')

    events = ('before_add_entity', )

    def __call__(self):
        entity = self.entity
        book = None
        if 'isbn13' in entity.edited_attributes:
            try:
                book = olapi.get_bookinfo_isbn13(entity['isbn13'], cover_required=False)
            except olapi.OpenLibraryFailure:
                self._cw.info('failed to fetch book info from OpenLibrary for ISBN %s', entity['isbn13'])
                return
        elif 'isbn10' in entity.edited_attributes:
            try:
                book = olapi.get_bookinfo_isbn10(entity['isbn10'], cover_required=False)
            except olapi.OpenLibraryFailure:
                self._cw.info('failed to fetch book info from OpenLibrary for ISBN %s', entity['isbn10'])
                return
        if book:
            set_if_unset(entity, 'title', book, 'title')
            set_if_unset(entity, 'pages', book, 'number_of_pages')
            set_if_unset(entity, 'isbn10', book, 'isbn_10')
            if 'publish_date' in book:
                date = book['publish_date']
                try:
                    if ',' in date:
                        date = datetime.strptime(date, '%B %d, %Y')
                    elif date.isdigit():
                        date = datetime(int(date), 1, 1)
                    else:
                        raise ValueError('unknown date format')
                    if not entity.get('publish_date'):
                        entity['publish_date'] = date
                except ValueError:
                    self._cw.info('failed to parse publish_date %s', date)
        BookCoverPreCommit(self._cw, entity=entity, book=book)


class BookCoverPreCommit(hook.Operation):

    def precommit_event(self):
        if not self.entity.has_cover and 'cover' in self.book:
            name = u'cover for %s' % self.book['title']
            self.session.execute('INSERT Image I: I title %(n)s, I data %(d)s, '
                                 'I data_format %(f)s, B has_cover I WHERE '
                                 'B eid %(x)s', {'n': name, 'x': self.entity.eid,
                                                 'd': Binary(self.book['cover']),
                                                 'f': u'image/jpeg'})
