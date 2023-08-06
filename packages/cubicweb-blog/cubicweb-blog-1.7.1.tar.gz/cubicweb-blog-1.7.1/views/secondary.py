"""Secondary views for blogs

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from calendar import monthrange
from datetime import datetime

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.view import EntityView, StartupView
from cubicweb.selectors import paginated_rset, sorted_rset, implements, \
                               authenticated_user
from cubicweb.web.htmlwidgets import BoxLink, BoxWidget
from cubicweb.web.views import baseviews, boxes, calendar, navigation

class BlogEntryArchiveView(StartupView):
    """control the view of a blog archive"""
    __regid__ = 'blog_archive'
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
        nmb_entries = self._cw.execute(self.countrql, args)[0][0]
        label = u'%s %s [%s]' % (self._cw._(calendar.MONTHNAMES[month-1]), year,
                                 nmb_entries)
        vtitle = '%s %s' % (display_name(self._cw, 'BlogEntry', 'plural'), label)
        url = xml_escape(self._cw.build_url('view', rql=rql, month=month, year=year, vtitle=vtitle))
        link = u'<a href="%s" title="">%s</a>' % (url, label)
        items.append( u'<li class="">%s</li>\n' % link )

    def call(self, maxentries=None, **kwargs):
        """display a list of entities by calling their <item_vid> view
        """
        rset = self._cw.execute('Any CD ORDERBY CD DESC WHERE B is BlogEntry, B creation_date CD')

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
            url = self._cw.build_url('view', vid='blog_archive')
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
    __regid__ = 'blog_archives_box'
    title = _('boxes_blog_archives_box')
    order = 35

    def call(self, **kwargs):
        """display blogs archive"""
        # XXX turn into a selector
        count_blogentry = self._cw.execute('Any COUNT(B) WHERE B is BlogEntry')
        if count_blogentry[0][0] > 0:
            box = BoxWidget(self._cw._(self.title), id=self.__regid__, islist=False)
            box.append(boxes.BoxHtml(self._cw.view('blog_archive', None, maxentries=12)))
            box.render(self.w)


class BlogEntryListBox(boxes.BoxTemplate):
    """display a box with latest blogs and rss"""
    __regid__ = 'blog_latest_box'
    title = _('blog_latest_box')
    visible = True # enabled by default
    order = 34

    def call(self, view=None, **kwargs):
        # XXX turn into a selector
        rset = self._cw.execute('Any X,T,CD ORDERBY CD DESC LIMIT 5 '
                                'WHERE X is BlogEntry, X title T, '
                                'X creation_date CD')
        if not rset:
            return
        box = BoxWidget(self._cw._(self.title), self.__regid__, islist=True)
        # TODO - get the date between brakets after link
        # empty string for title argument to deactivate auto-title
        for i in xrange(rset.rowcount):
            entity = rset.get_entity(i, 0)
            box.append(BoxLink(entity.absolute_url(), xml_escape(entity.dc_title())))
        rqlst = rset.syntax_tree()
        rqlst.set_limit(None)
        rql = rqlst.as_string(kwargs=rset.args)
        url = self._cw.build_url('view', rql=rql, page_size=10)
        box.append(BoxLink(url,  u'[%s]' % self._cw._(u'see more')))
        rss_icon = self._cw.external_resource('RSS_LOGO_16')
        # FIXME - could use rss_url defined as a property if available
        rss_label = u'%s <img src="%s" alt="%s"/>' % (
            self._cw._(u'subscribe'), rss_icon, self._cw._('rss icon'))
        rss_url = self._cw.build_url('view', vid='rss', rql=rql)
        box.append(BoxLink(rss_url, rss_label))
        box.render(self.w)


class BlogEntrySummary(boxes.BoxTemplate):
    __regid__ = 'blog_summary_box'
    title = _('boxes_blog_summary_box')
    order = 36
    __select__ = boxes.BoxTemplate.__select__

    def call(self, view=None, **kwargs):
        box = BoxWidget(self._cw._(self.title), self.__regid__, islist=True)
        rql = 'Any U, COUNT(B) GROUPBY U WHERE U is CWUser, ' \
              'B is BlogEntry, B created_by U'
        rset = self._cw.execute(rql)
        for user in rset:
            euser = self._cw.entity_from_eid(user[0])
            box.append(BoxLink(self._cw.build_url('blogentry/%s' % euser.login),
                                              u'%s [%s]' % (euser.name(),
                                                            user[1])))
        box.render(self.w)

## list views ##################################################################

class BlogEntrySameETypeListView(baseviews.SameETypeListView):
    __select__ = baseviews.SameETypeListView.__select__ & implements('BlogEntry')
    countrql = 'Any COUNT(B) WHERE B is BlogEntry, B creation_date >=  %(firstday)s, B creation_date <= %(lastday)s'
    item_vid = 'blog'

    def call(self, **kwargs):
        self._cw.add_css('cubes.blog.css')
        super(BlogEntrySameETypeListView, self).call(**kwargs)
        if 'year' in self._cw.form and 'month' in self._cw.form:
            self.render_next_previous(int(self._cw.form['year']), int(self._cw.form['month']))

    def render_next_previous(self, year, month):
        if month == 12:
            nextmonth = 1
            year = year + 1
        else:
            nextmonth = month + 1
        if month == 1:
            previousmonth = 12
            year = year - 1
        else:
            previousmonth = month -1

        self.w(u'<div class="prevnext">')
        self.w(u'<span class="previousmonth">%s</span>' \
               % self.render_link(year, previousmonth,
                                  xml_escape(u'<< ' + self._cw._(u'previous month'))))
        self.w(u'<span class="nextmonth">%s</span>' \
               % self.render_link(year, nextmonth,
                                  xml_escape(self._cw._(u'next month') + u' >>')))
        self.w(u'</div>')

    def render_link(self, year, month, atitle):
        firstday = datetime(year, month, 1)
        lastday = datetime(year, month, monthrange(year, month)[1])
        rql = ('Any B, BD ORDERBY BD DESC '
               'WHERE B is BlogEntry, B creation_date BD, '
               'B creation_date >=  "%s", B creation_date <= "%s"' %
                (firstday.strftime('%Y-%m-%d'), lastday.strftime('%Y-%m-%d')))
        args = {'firstday':firstday, 'lastday':lastday}
        nmb_entries = self._cw.execute(self.countrql, args)[0][0]
        label = u'%s %s [%s]' % (self._cw._(calendar.MONTHNAMES[month-1]), year,
                                 nmb_entries)
        vtitle = '%s %s' % (display_name(self._cw, 'BlogEntry', 'plural'), label)
        url = xml_escape(self._cw.build_url('view', rql=rql, vtitle=vtitle,
                                        month=month, year=year))
        if self._cw.execute(rql):
            return u'<a href="%s" title="">%s</a>' % (url, atitle)
        return u''


class BlogEntryBlogView(EntityView):
    __regid__ = 'blog'
    __select__ = implements('BlogEntry')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        w = self.w
        _ = self._cw._
        w(u'<div class="post">')
        w(u'<h1>%s</h1>' % entity.view('incontext'))
        w(u'%s ' % entity.postinfo_description())
        creator = entity.creator
        if creator:
            vtitle = _('blog entries created by %s') % creator.name()
            rql = 'Any X ORDERBY D DESC WHERE X is BlogEntry, X created_by Y, '\
                  'Y eid %s, X creation_date D' % creator.eid
            url = self._cw.build_url('view', rql=rql, vtitle=vtitle, page_size=10)
            w(u'%s <a title="%s" href="%s">%s</a>' % (
                _('by'), xml_escape(vtitle), xml_escape(url), creator.name()))
        w(u'<div class="entry">')
        body = entity.printable_value('content')
        w(body)
        w(u'</div>')
        w(u'<div class="postmetadata">%s</div>' % entity.view('post-reldata'))
        w(u'</div>')


class BlogEntryPostMetaData(EntityView):
    __regid__ = 'post-reldata'
    __select__ = implements('BlogEntry')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        _ = lambda ertype, form='': display_name(self._cw, ertype, form)
        reldata = []
        w = reldata.append
        if 'comments' in self._cw.vreg.schema and 'BlogEntry' in self._cw.vreg.schema.rschema('comments').objects():
            count = self._cw.execute('Any COUNT(C) WHERE C comments B, B eid %(x)s',
                                     {'x': entity.eid}, 'x')[0][0]
            if count:
                url = xml_escape(entity.absolute_url())
                w(u'<a href="%s">%s %s</a>' % (url, count, _('Comment', 'plural')))
            else:
                w(u'%s %s' % (count, _('Comment')))
        if 'tags' in self._cw.vreg.schema and 'BlogEntry' in self._cw.vreg.schema.rschema('tags').objects():
            tag_rset = entity.related('tags', 'object')
            if tag_rset:
                w(u'%s %s' % (_('tags', 'object'), self._cw.view('csv', tag_rset)))
        rset = entity.related('entry_of', 'subject')
        if rset:
            w(u'%s %s' % (self._cw._('blogged in '),
                          self._cw.view('csv', rset, 'null')))
        self.w(u' | '.join(reldata))


class BlogNavigation(navigation.PageNavigation):
    __select__ = paginated_rset() & sorted_rset() & implements('BlogEntry')

    def index_display(self, start, stop):
        return u'%s' % (int(start / self.page_size)+1)

