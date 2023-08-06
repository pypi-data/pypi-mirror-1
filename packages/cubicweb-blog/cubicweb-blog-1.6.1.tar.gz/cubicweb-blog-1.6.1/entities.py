"""entity classes for Blog entities

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE)
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: Lesser General Public License version 2 or above - http://www.gnu.org/
"""
__docformat__ = "restructuredtext en"

from cubicweb.utils import todate
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ICalendarViews, ICalendarable, ISiocItem, ISiocContainer

class BlogEntry(AnyEntity):
    """customized class for BlogEntry entities"""
    id = 'BlogEntry'
    fetch_attrs, fetch_order = fetch_config(['creation_date', 'title'], order='DESC')
    __implements__ = (ICalendarViews, ICalendarable, ISiocItem)

    def dc_title(self):
        return self.title

    def dc_description(self, format='text/plain'):
        return self.printable_value('content', format=format)

    ## calendar interfaces ####################################################
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
        _ = self.req._
        descr = u'%s %s' % (_('posted on'), self.format_date(self.creation_date))
        return descr

    # isioc interface
    def isioc_content(self):
        return self.content

    def isioc_container(self):
        rset = self.related('entry_of')
        entity = rset.get_entity(0, 0)
        return entity

    def isioc_type(self):
        return 'BlogPost'

    def isioc_replies(self):
        return []

    def isioc_topics(self):
        return []


class Blog(AnyEntity):
    """customized class for Blog entities"""

    id = 'Blog'
    __implements__ = AnyEntity.__implements__ + (ISiocContainer,)

    def rss_feed_url(self):
        if self.rss_url:
            return self.rss_url
        rql = 'Any E ORDERBY D DESC WHERE E is BlogEntry, E entry_of X, X eid %s, E creation_date D' % self.eid
        return self.build_url(rql=rql, vid='rss', vtitle=self.dc_title())

    # isioc interface
    def isioc_type(self):
        return 'Weblog'

    def isioc_items(self):
        return self.reverse_entry_of


