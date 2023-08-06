"""schema customization for the intranet application

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from yams.buildobjs import RelationDefinition

try:
    from cubes.card.schema import Card
    from cubes.blog.schema import BlogEntry
    from cubes.file.schema import File, Image
    from cubes.link.schema import Link
    from yams.reader import context
    defined_types = context.defined
except (ImportError, NameError):
    # old-style yams schema will raise NameError on EntityType, RelationType, etc.
    Card = import_erschema('Card')
    BlogEntry = import_erschema('BlogEntry')
    File = import_erschema('File')
    Image = import_erschema('Image')
    Link = import_erschema('Link')

PERMISSIONS = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'users',),
        'delete': ('managers', 'owners',),
        'update': ('managers', 'users', 'owners',),
        }

Card.__permissions__ = PERMISSIONS
BlogEntry.__permissions__ = PERMISSIONS
File.__permissions__ = PERMISSIONS
Image.__permissions__ = PERMISSIONS
Link.__permissions__ = PERMISSIONS

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'Event'


BASETYPES = ('Card', 'BlogEntry', 'File', 'Image', 'Event', 'Link', 'Task', 'Book')
if 'VersionedFile' in defined_types:
    BASETYPES += ('VersionedFile',)

class see_also(RelationDefinition):
    subject = BASETYPES
    object = BASETYPES

class comments(RelationDefinition):
    subject = 'Comment'
    object = BASETYPES

class tags(RelationDefinition):
    subject = 'Tag'
    object = BASETYPES
