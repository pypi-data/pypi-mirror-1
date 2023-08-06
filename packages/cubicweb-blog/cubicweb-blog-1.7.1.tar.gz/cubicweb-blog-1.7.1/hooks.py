from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class BlogEntryAddedView(ContentAddedView):
    """get notified from new blogs"""
    __select__ = implements('BlogEntry',)
    content_attr = 'content'

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return '[%s] %s' % (self._cw.vreg.config.appid, entity.dc_title())
