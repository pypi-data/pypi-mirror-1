# -*- coding: utf-8 -*-
"""
Simple API for OpenLibrary <http://openlibrary.org/dev/docs>

Try running::

  $ python olapi.py isbn 9780596001889
  $ python olapi.py search tom sawyer

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from urllib2 import urlopen, HTTPError
from urllib import urlencode
from simplejson import loads, dumps

class OpenLibraryFailure(Exception):
    """raised on API failure"""

def openlibrary_fetch(url):
    result = loads(urlopen(url).read()) # XXX handle timeouts
    if result[u'status'] != u'ok':
        raise OpenLibraryFailure(result[u'message'])
    return result[u'result']

def openlibrary_query(type, **kwargs):
    query = dict(type=type, **kwargs)
    url = 'http://openlibrary.org/api/things?%s' % urlencode({'query': dumps(query)})
    return openlibrary_fetch(url)

def openlibrary_get(key):
    url = 'http://openlibrary.org/api/get?key=%s' % key
    return openlibrary_fetch(url)

def get_bookinfo_key(key, cover_required=False):
    book = openlibrary_get(key)
    isbn = book.get('isbn_13', book.get('isbn_10'))
    if isbn:
        try:
            book['cover'] = get_bookcover(isbn[0])
        except OpenLibraryFailure, exc:
            if cover_required:
                raise exc
    return book

def get_bookinfo_isbn13(isbn, cover_required=False):
    keys = openlibrary_query('/type/edition', isbn_13=isbn)
    if keys:
        return get_bookinfo_key(keys[0], cover_required)
    else:
        return {}

def get_bookinfo_isbn10(isbn, cover_required=False):
    keys = openlibrary_query('/type/edition', isbn_10=isbn)
    if keys:
        return get_bookinfo_key(keys[0], cover_required)
    else:
        return {}

def get_bookcover(isbn, size='M'):
    try:
        url = 'http://covers.openlibrary.org/b/isbn/%s-%s.jpg?default=false' % (isbn, size)
        data = urlopen(url).read()
    except HTTPError, exc:
        raise OpenLibraryFailure(str(exc))
    return data

def search_books(phrase):
    query = dict(query=phrase)
    url = 'http://openlibrary.org/api/search?%s' % urlencode({'q': dumps(query)})
    return openlibrary_fetch(url)

if __name__ == '__main__':
    import sys, pprint
    if sys.argv[1] == 'isbn':
        pprint.pprint(get_bookinfo_isbn13(sys.argv[2]))
    elif sys.argv[1] == 'search':
        pprint.pprint(search_books(sys.argv[2]))
