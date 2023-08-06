"""
Primaries views for Book.

:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.selectors import implements
from cubicweb.web.views.primary import PrimaryView
from cubicweb.web import uicfg

uicfg.primaryview_section.tag_subject_of(('Book', 'has_cover', 'Image'), 'hidden')

class BookPrimaryView(PrimaryView):
    __select__ = implements('Book')

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_title()))

    def render_entity_attributes(self, entity):
        self._cw.add_css('cubes.book.css')
        self.w(u'<div class="contener">')
        self.w(u'<div class="left">')
        self.render_cover(entity)
        self.w(u'</div>')
        self.w(u'<div>')
        self.w(u'<h3>')
        self.w(u'%s ' % self._cw._('by'))
        self.wview('csv', entity.related('authors'), 'null')
        self.w(u'</h3>')
        self.w(u'%s : %s' % (self._cw._('Summary'), xml_escape(entity.summary or u'')))
        self.w(u'</div>')
        self.w(u'</div>')
        self.render_details(entity)
        self.w(u'<div><h3>%s</h3></div>' % self._cw._('Content'))
        self.w(u'<div>%s</div>' % xml_escape(entity.content or u''))

    def render_details(self, entity):
        _= self._cw._
        self.w(u'<div><h3>%s</h3>' % _('Details'))
        self.w(u'<ul>')
        self.w(u'<li> %s : %s </li>' % (_('Publication date'), entity.printable_value('publish_date') or u''))
        self.w(u'<li> %s : ' % _('Published by'))
        self.wview('oneline', entity.related('publisher'), 'null')
        self.w(u',  %s %s' % (entity.pages or u'?', _('pages')))
        self.w(u'</li>')
        self.w(u'<li> %s : ' % _('Editor'))
        self.wview('oneline', entity.related('editor'), 'null')
        self.w(u'</li>')
        self.w(u'<li> %s : ' % _('Collection'))
        self.wview('oneline', entity.related('collection'), 'null')
        self.w(u'</li>')
        self.w(u'<li> %s : %s' % (_('Language'), xml_escape(entity.language or u'')))
        self.w(u'</li>')
        self.w(u'<li> ISBN-10: %s' % xml_escape(entity.isbn10 or u''))
        self.w(u'</li>')
        self.w(u'<li>ISBN-13: %s' % xml_escape(entity.isbn13 or u''))
        self.w(u'</li>')
        self.w(u'</ul></div>')

    def render_cover(self, entity):
        if entity.has_cover:
            imgs = [(image.absolute_url(vid='download'), image.data_name)
                    for image in entity.has_cover]
        else:
            imgs = [(self._cw.external_resource('PICTO_NOCOVER'),
                     self._cw._('no cover'))]
        for src, alt in imgs:
            self.w(u'<img alt="%s" src="%s" style="align:right; width:110; height:130" />' %
                   (xml_escape(alt), xml_escape(src)))

