# -*- coding: utf-8 -*-
"""
Url rewriting for books.

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

class BookReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/book/isbn/(.*)'),
         dict(rql='Any B WHERE B is Book, (B isbn13 "%(isbn)s") OR (B isbn10 "%(isbn)s")' % {'isbn': r'\1'})),
        ]
