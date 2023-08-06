# pylint: disable-msg=W0622
"""cubicweb-blog packaging information"""

modname = 'blog'
distname = "cubicweb-%s" % modname

numversion = (1, 7, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "blog component for the CubicWeb framework"
long_desc = """\
Summary
-------
The `blog` cube provides blogging functionnalities. It creates two entity types,
`Blog` and `BlogEntry`. There are related to each other by the relation
`BlogEntry entry_of Blog`.

Usage
-----

When a user submits a blog entry, it goes in a `draft` state until the blog
entry is published by an application managers. The blog entry will not be
visible until it reaches the `published` state.

When a blog entry is submitted, an email notification is automatically sent
to all the users belonging to the `managers` group of the application.

Specific boxes provided by this cube:

- `BlogEntryArchiveBox`, displays a box with the total number of blog entries
submitted by month for the last twelve months.

- `BlogEntryListBox`, displays a box with the latest five blog entries
published in your application as well as link to subscribe to a RSS feed.

- `BlogEntrySummary`, displays a box with the list of users who submitted
blog entries and the total number of blog entries they submitted.

This cube also provides some web services such as:

- http://xx:xxxx/blogentries/YYYY to retrieve the blog entries submitted
  during the year YYYY through a RSS feed

- http://xx:xxxx/blogentries/YYYY/MM to retrieve the blog entries submitted
  during the month MM of the year YYYY through a RSS feed

- http://xx:xxxx/blog/[eid]/blogentries/YYYY to retrieve the blog entries
  submitted in the blog of identifier [eid], during the year YYYY through
  a RSS feed

- http://xx:xxxx/blog/[eid]/blogentries/YYYY/MM to retrieve the blog entries
  submitted in the blog of identifier [eid], during the month MM of the
  year YYYY through a RSS feed
"""

classifiers = [
    'Environment :: Web Environment'
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = tuple(__depends_cubes__)

# package ###

from os import listdir as _listdir
from os.path import join, isdir, exists
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
