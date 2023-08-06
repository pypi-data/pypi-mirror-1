"""Blog unit tests"""
import re

from logilab.common.testlib import unittest_main, mock_object
from cubicweb.devtools.testlib import CubicWebTC, MAILBOX

from email.Header import decode_header
from cubicweb.sobjects.notification import RenderAndSendNotificationView
from cubicweb.server.hookhelper import SendMailOp


class BlogTestsCubicWebTC(CubicWebTC):
    """test blog specific behaviours"""

    def test_notifications(self):
        req = self.request()
        cubicweb_blog = req.create_entity('Blog', title=u'cubicweb', description=u"cubicweb c'est beau")
        blog_entry_1 = req.create_entity('BlogEntry', title=u"hop", content=u"cubicweb hop")
        self.execute('SET E entry_of B WHERE B eid %(beid)s, E eid %(eeid)s' % {'beid' :cubicweb_blog.eid, 'eeid' : blog_entry_1.eid})
        blog_entry_2 = req.create_entity('BlogEntry', title=u"yes",  content=u"cubicweb yes")
        self.execute('SET E entry_of B WHERE B eid %(beid)s, E eid %(eeid)s' % {'beid' :cubicweb_blog.eid, 'eeid' : blog_entry_2.eid})
        self.assertEquals(len(MAILBOX), 0)
        self.commit()
        self.assertEquals(len(MAILBOX), 2)
        mail = MAILBOX[0]
        self.assertEquals(mail.subject, '[data] hop')
        mail = MAILBOX[1]
        self.assertEquals(mail.subject, '[data] yes')


if __name__ == '__main__':
    unittest_main()
