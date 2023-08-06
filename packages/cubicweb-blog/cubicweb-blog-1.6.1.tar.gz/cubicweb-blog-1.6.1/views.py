"""Specific views for blogs

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from calendar import monthrange
from datetime import datetime

from logilab.mtconverter import html_escape

from cubicweb.view import EntityView, StartupView
from cubicweb.utils import UStringIO
from cubicweb.selectors import paginated_rset, sorted_rset, implements
from cubicweb.web import uicfg
from cubicweb.web.htmlwidgets import BoxLink, BoxWidget
from cubicweb.web.views import baseviews, primary, boxes, calendar, navigation

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
            html_escape(entity.rss_feed_url()), self.req._(u'subscribe'),
            self.req.external_resource('RSS_LOGO_16'), self.req._('rss icon')))

    def render_entity_relations(self, entity):
        super(BlogPrimaryView, self).render_entity_relations(entity)
        rset = entity.related('entry_of', 'object')
        strio = UStringIO()
        self.pagination(self.req, rset, strio.write, page_size=10)
        self.wview('full_list', rset, 'null')
        self.w(strio.getvalue())


class BlogEntryPrimaryView(primary.PrimaryView):
    __select__ = implements('BlogEntry')
    show_attr_label = False

    def render_entity_relations(self, entity):
        rset = entity.related('entry_of', 'subject')
        if rset:
            _ = self.req._
            self.w(_('blogged in '))
            self.wview('secondary', rset, 'null')


class BlogEntryArchiveView(StartupView):
    """control the view of a blog archive"""
    id = 'blog_archive'
    countrql = 'Any COUNT(B) WHERE B is BlogEntry, B creation_date >=  %(firstday)s, B creation_date <= %(lastday)s'

    def represent(self, items, year, month):
        """represent a single month entry"""
        firstday = datetime(year, month, 1)
        lastday = datetime(year, month, monthrange(year, month)[1])
        rql = ('Any B, BD ORDERBY BD DESC '
               'WHERE B is BlogEntry, B creation_date BD, '
               'B creation_date >=  "%s", B creation_date <= "%s"' %
                (firstday.strftime('%Y-%m-%d'), lastday.strftime('%Y-%m-%d')))
        args = {'firstday':firstday, 'lastday':lastday}
        nmb_entries = self.req.execute(self.countrql, args)[0][0]
        label = u'%s %s [%s]' % (self.req._(calendar.MONTHNAMES[month-1]), year,
                                 nmb_entries)
        vtitle = '%s %s' % (self.req._('BlogEntry_plural'), label)
        url = html_escape(self.build_url('view', rql=rql, vtitle=vtitle,
                                         vid='full_list'))
        link = u'<a href="%s" title="">%s</a>' % (url, label)
        items.append( u'<li class="">%s</li>\n' % link )

    def call(self, maxentries=None, **kwargs):
        """display a list of entities by calling their <item_vid> view
        """
        rset = self.req.execute('Any CD ORDERBY CD DESC WHERE B is BlogEntry, B creation_date CD')

        blogmonths = []
        items = []
        for (blogdate,) in rset:
            year, month = blogdate.year, blogdate.month
            if (year, month) not in blogmonths:
                blogmonths.append( (year, month) )
        if maxentries is None:
            displayed_months = blogmonths
            needmore = False
        else:
            needmore = len(blogmonths) > maxentries
            displayed_months = blogmonths[:maxentries]
        for year, month in displayed_months:
            self.represent(items, year, month)
        if needmore:
            url = self.build_url('view', vid='blog_archive')
            link = u'<a href="%s" title="">[see more archives]</a>' % url
            items.append( u'<li class="">%s</li>\n' % link )
        self.w(u'<div class="boxFrame">')
        if items:
            self.w(u'<div class="boxContent">\n')
            self.w(u'<ul class="boxListing">')
            self.w(''.join(items))
            self.w(u'</ul>\n</div>\n')
        self.w(u'</div>')


class BlogEntryArchiveBox(boxes.BoxTemplate):
    """blog side box displaying a Blog Archive"""
    id = 'blog_archives_box'
    title = _('boxes_blog_archives_box')
    order = 35

    def call(self, **kwargs):
        """display blogs archive"""
        count_blogentry = self.req.execute('Any COUNT(B) WHERE B is BlogEntry')
        _ = self.req._

        if count_blogentry[0][0] > 0:
            box = BoxWidget(_(self.title), id=self.id, islist=False)
            box.append(boxes.BoxHtml(self.view('blog_archive', None, maxentries=12)))
            box.render(self.w)


class BlogEntryListBox(boxes.BoxTemplate):
    """display a box with latest blogs and rss"""
    id = 'blog_latest_box'
    title = _('blog_latest_box')
    visible = True # enabled by default
    order = 34

    def call(self, view=None, **kwargs):
        box = BoxWidget(self.req._(self.title), self.id, islist=True)
        rset = self.req.execute('Any X,T,CD ORDERBY CD DESC LIMIT 5 '
                                'WHERE X is BlogEntry, X title T, '
                                'X creation_date CD')
        if not rset:
            return
        # TODO - get the date between brakets after link
        # empty string for title argument to deactivate auto-title
        for i in xrange(rset.rowcount):
            entity = rset.get_entity(i, 0)
            box.append(BoxLink(entity.absolute_url(), html_escape(entity.dc_title())))
        rqlst = rset.syntax_tree()
        rqlst.set_limit(None)
        rql = rqlst.as_string(kwargs=rset.args) # en gros...
        url = self.build_url('view', vid='full_list', rql=rql, page_size=10)
        box.append(BoxLink(url,  u'[%s]' % self.req._(u'see more')))
        rss_icon = self.req.external_resource('RSS_LOGO_16')
        # FIXME - could use rss_url defined as a property if available
        rss_label = u'%s <img src="%s" alt="%s"/>' % (
                           self.req._(u'subscribe'), rss_icon, self.req._('rss icon'))
        rss_url = self.build_url('view', vid='rss', rql=rql)
        box.append(BoxLink(rss_url, rss_label))
        box.render(self.w)


## list views #################################################################

class BlogEntryListView(baseviews.ListView):
    __select__ = implements('BlogEntry')

    def call(self, klass='invisible', title=None, **kwargs):
        """display a list of entities by calling their <item_vid> view
        """
        entity = self.entity(0,0)
        self.req.add_css('cubes.blog.css')
        # XXX: no title if subvid specified to try to avoid cases where we want
        # the original list view...
        if title is None and not ('vtitle' in self.req.form or 'subvid' in kwargs):
            self.w(u'<h1>%s</h1>' % display_name(self.req, 'BlogEntry', form='plural'))
        super(BlogEntryListView, self).call(klass=klass, **kwargs)


class BlogEntryListItemView(baseviews.ListItemView):
    id = 'full_list'
    __select__ = implements('BlogEntry')
    redirect_vid = 'blog'


class BlogEntryBlogView(baseviews.ListItemView):
    id = 'blog'
    __select__ = implements('BlogEntry')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        w = self.w
        _ = self.req._
        w(u'<div class="post">')
        w(u'<h1>%s</h1>' % entity.view('incontext'))
        w(u'%s ' % entity.postinfo_description())
        creator = entity.creator
        if creator:
            vtitle = _('blog entries created by %s %s') % (creator.firstname,
                                                           creator.surname)
            rql = 'Any X ORDERBY D DESC WHERE X is BlogEntry, X created_by Y, '\
                  'Y eid %s, X creation_date D' % creator.eid
            url = self.build_url('view', vid="full_list", rql=rql, vtitle=vtitle,
                                 page_size = 10)
            w(u'%s <a href="%s">%s %s</a>' % (_('by'), html_escape(url),
                                              creator.firstname,
                                              creator.surname))

        w(u'<div class="entry">')
        body = entity.printable_value('content')
        w(body)
        w(u'</div>')
        w(u'<div class="postmetadata">%s</div>' % entity.view('post-reldata'))
        w(u'</div>')


class BlogEntryPostMetaData(EntityView):
    id = 'post-reldata'
    __select__ = implements('BlogEntry')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        _ = lambda ertype, form='': display_name(self.req, ertype, form)
        reldata = []
        w = reldata.append
        if 'comments' in self.schema and 'BlogEntry' in self.schema.rschema('comments').objects():
            count = self.req.execute('Any COUNT(C) WHERE C comments B, B eid %(x)s',
                                     {'x': entity.eid}, 'x')[0][0]
            if count:
                url = html_escape(entity.absolute_url())
                w(u'<a href="%s">%s %s</a>' % (url, count, _('Comment', 'plural')))
            else:
                w(u'%s %s' % (count, _('Comment')))
        if 'tags' in self.schema and 'BlogEntry' in self.schema.rschema('tags').objects():
            tag_rset = entity.related('tags', 'object')
            if tag_rset:
                w(u'%s %s' % (_('tags', 'object'), self.view('csv', tag_rset)))
        rset = entity.related('entry_of', 'subject')
        if rset:
            w(u'%s %s' % (self.req._('blogged in '),
                          self.view('secondary', rset, 'null')))
        self.w(u' | '.join(reldata))


class BlogNavigation(navigation.PageNavigation):
    __select__ = paginated_rset() & sorted_rset() & implements('BlogEntry')

    def index_display(self, start, stop):
        return u'%s' % (int(start / self.page_size)+1)

