from calendar import monthrange
from datetime import datetime

from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

class BlogReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/blogentry/([a-z_]+)'),
         dict(rql='Any X ORDERBY CD DESC WHERE X is BlogEntry, X creation_date CD, X created_by U, U login "%(user)s"' % {'user': r'\1'},
              user = r'\1')),
        (rgx('/blogentry/([a-z_]+)\.rss'),
         dict(rql='Any X ORDERBY CD DESC LIMIT 20 WHERE X is BlogEntry, X creation_date CD, X created_by U, U login "%(user)s"' % {'user': r'\1'}, vid='rss')),
        (rgx('/blogentries/([0-9]{4})'),
         dict(rql='Any B ORDERBY CD DESC WHERE B is BlogEntry, B creation_date CD, '
                  'B creation_date >= "%(param)s-01-01", '
                  'B creation_date <= "%(param)s-12-31"' % {'param': r'\1'},
              )),
        (rgx('/blogentries/([0-9]{4})/([0-9]{2})'),
         dict(rql='Any B, BD ORDERBY BD DESC '
                  'WHERE B is BlogEntry, B creation_date BD, '
                  'B creation_date >=  "%(year)s/%(month)s/01", B creation_date <= "%(year)s/%(month)s/30"' % {'year': r'\1', 'month': r'\2'},
              )),
        (rgx('/blog/([0-9]+)/blogentries'),
         dict(rql='Any B ORDERBY CD DESC WHERE B is BlogEntry, B creation_date CD, '
                  'B entry_of BL, BL eid %(eid)s' % {'eid': r'\1'},
              )),
        (rgx('/blog/([0-9]+)/blogentries/([0-9]{4})'),
         dict(rql='Any B ORDERBY CD DESC WHERE B is BlogEntry, B creation_date CD, '
                  'B creation_date >= "%(param)s-01-01", '
                  'B creation_date <= "%(param)s-12-31", B entry_of BL, BL eid %(eid)s' % {'eid': r'\1', 'param': r'\2'},
              )),
        (rgx('/blog/([0-9]+)/blogentries/([0-9]{4})/([0-9]{2})'),
         dict(rql='Any B, BD ORDERBY BD DESC '
                  'WHERE B is BlogEntry, B creation_date BD, B entry_of BL, BL eid %(eid)s, '
                  'B creation_date >=  "%(year)s/%(month)s/01", B creation_date <= "%(year)s/%(month)s/30"' % {'eid': r'\1', 'year': r'\2', 'month': r'\3'},
              )),

        ]
