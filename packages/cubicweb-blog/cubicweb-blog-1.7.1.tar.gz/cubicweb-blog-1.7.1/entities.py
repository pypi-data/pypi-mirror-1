"""entity classes for Blog entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE)
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: Lesser General Public License version 2 or above - http://www.gnu.org/
"""
__docformat__ = "restructuredtext en"

from logilab.common.date import todate

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import (ICalendarViews, ICalendarable,
                                 ISiocItem, ISiocContainer, IPrevNext)


class Blog(AnyEntity):
    """customized class for Blog entities"""

    __regid__ = 'Blog'
    __implements__ = AnyEntity.__implements__ + (ISiocContainer,)

    def rss_feed_url(self):
        if self.rss_url:
            return self.rss_url
        rql = ('Any E ORDERBY D DESC '
               'WHERE E is BlogEntry, E entry_of X, X eid %s, E creation_date D'
               )
        return self._cw.build_url(rql=rql % self.eid, vid='rss',
                              vtitle=self.dc_title())

    # isioc interface ##########################################################

    def isioc_type(self):
        return 'Weblog'

    def isioc_items(self):
        return self.reverse_entry_of


class BlogEntry(AnyEntity):
    """customized class for BlogEntry entities"""
    __regid__ = 'BlogEntry'
    fetch_attrs, fetch_order = fetch_config(['creation_date', 'title'], order='DESC')
    __implements__ = AnyEntity.__implements__ + (
        ICalendarViews, ICalendarable, ISiocItem, IPrevNext)

    def dc_title(self):
        return self.title

    def dc_description(self, format='text/plain'):
        return self.printable_value('content', format=format)

    def dc_date(self, date_format=None):# XXX default to ISO 8601 ?
        """return latest modification date of this entity"""
        return self._cw.format_date(self.creation_date, date_format=date_format)

    def parent(self):
        return self.entry_of and self.entry_of[0] or None

    # calendar interfaces ######################################################

    @property
    def start(self):
        return self.creation_date

    @property
    def stop(self):
        return self.creation_date

    def matching_dates(self, begin, end):
        """calendar views interface"""
        mydate = self.creation_date
        if not mydate:
            return []
        mydate = todate(mydate)
        if begin < mydate < end:
            return [mydate]
        return []

    def postinfo_description(self):
        _ = self._cw._
        descr = u'%s %s' % (_('posted on'), self._cw.format_date(self.creation_date))
        return descr

    # isioc interface ##########################################################

    def isioc_content(self):
        return self.content

    def isioc_container(self):
        return self.parent()

    def isioc_type(self):
        return 'BlogPost'

    def isioc_replies(self):
        # XXX link to comments
        return []

    def isioc_topics(self):
        # XXX link to tags, folders?
        return []

    # IPrevNext interface #####################################################
    def _sibling_entry(self, order, operator):
        if self.entry_of:
            rql = ('Any B ORDERBY B %s LIMIT 1 '
                   'WHERE B is BlogEntry, B entry_of BL, BL eid %%(blog)s, '
                   'B eid %s %%(eid)s')
            rset = self._cw.execute(rql % (order, operator),
                                    {'blog': self.entry_of[0].eid, 'eid': self.eid})
        else:
            rql = ('Any B ORDERBY B %s LIMIT 1 '
                   'WHERE B is BlogEntry, B eid %s %%(eid)s')
            rset = self._cw.execute(rql % (order, operator), {'eid': self.eid})
        if rset:
            return rset.get_entity(0,0)

    def next_entity(self):
        return self._sibling_entry('ASC', '>')

    def previous_entity(self):
        return self._sibling_entry('DESC', '<')
