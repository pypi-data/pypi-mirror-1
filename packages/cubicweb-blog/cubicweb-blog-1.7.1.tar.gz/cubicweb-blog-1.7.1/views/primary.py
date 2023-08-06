"""Primary views for blogs

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.selectors import implements
from cubicweb.web import uicfg
from cubicweb.web.views import primary

uicfg.primaryview_section.tag_attribute(('Blog', 'title'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Blog', 'rss_url'), 'hidden')
uicfg.primaryview_section.tag_attribute(('BlogEntry', 'title'), 'hidden')
uicfg.primaryview_section.tag_object_of(('*', 'entry_of', 'Blog'), 'hidden')
uicfg.primaryview_section.tag_subject_of(('BlogEntry', 'entry_of', '*'),
                                         'relations')

uicfg.actionbox_appearsin_addmenu.tag_object_of(('*', 'entry_of', 'Blog'), True)


class BlogPrimaryView(primary.PrimaryView):
    __select__ = implements('Blog')

    def render_entity_attributes(self, entity):
        super(BlogPrimaryView, self).render_entity_attributes(entity)
        self.w('<a class="right" href="%s">%s <img src="%s" alt="%s"/></a>' % (
            xml_escape(entity.rss_feed_url()), self._cw._(u'subscribe'),
            self._cw.external_resource('RSS_LOGO_16'), self._cw._('rss icon')))

    def render_entity_relations(self, entity):
        super(BlogPrimaryView, self).render_entity_relations(entity)
        rset = entity.related('entry_of', 'object')
        if rset:
            strio = UStringIO()
            self.paginate(self._cw, w=strio.write, page_size=10, rset=rset)
            self.wview('sameetypelist', rset)
            self.w(strio.getvalue())

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_title()))


class BlogEntryPrimaryView(primary.PrimaryView):
    __select__ = implements('BlogEntry')
    show_attr_label = False

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.dc_title()))

    def render_entity_relations(self, entity):
        rset = entity.related('entry_of', 'subject')
        if rset:
            self.w(self._cw._('blogged in '))
            self.wview('csv', rset, 'null')
