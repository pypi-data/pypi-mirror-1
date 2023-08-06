"""schema customization for the intranet application

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

PERMISSIONS = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'users',),
        'delete': ('managers', 'owners',),
        'update': ('managers', 'users', 'owners',),
        }

Card = import_erschema('Card')
Card.permissions = PERMISSIONS

BlogEntry = import_erschema('BlogEntry')
BlogEntry.permissions = PERMISSIONS

File = import_erschema('File')
File.permissions = PERMISSIONS

Image = import_erschema('Image')
Image.permissions = PERMISSIONS

Link = import_erschema('Link')
Link.permissions = PERMISSIONS

class interested_in(RelationDefinition):
    subject = 'CWUser'
    object = 'Event'


BASETYPES = ('Card', 'BlogEntry', 'File', 'Image', 'Event', 'Link', 'Task', 'Book')
if 'VersionedFile' in defined_types:
    BASETYPES += ('VersionedFile',)

class see_also(RelationType):
    symetric = True
    subject = BASETYPES
    object = BASETYPES

class comments(RelationDefinition):
    subject = 'Comment'
    object = BASETYPES

class tags(RelationDefinition):
    subject = 'Tag'
    object = BASETYPES
