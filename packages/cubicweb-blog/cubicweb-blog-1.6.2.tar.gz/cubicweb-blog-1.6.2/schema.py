from cubicweb.schema import format_constraint

class Blog(EntityType):
    title = String(maxsize=50, required=True)
    description_format = String(meta=True, internationalizable=True, maxsize=50,
                                default='text/rest', constraints=[format_constraint])
    description = String()
    rss_url = String(maxsize=128, description=_('blog\'s rss url (useful for when using external site such as feedburner)'))


class BlogEntry(EntityType):
    title = String(required=True, fulltextindexed=True, maxsize=256)
    content_format = String(meta=True, internationalizable=True, maxsize=50,
                            default='text/rest', constraints=[format_constraint])
    content = String(required=True, fulltextindexed=True)
    entry_of = SubjectRelation('Blog', cardinality='**')
