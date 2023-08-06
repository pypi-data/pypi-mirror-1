"""specific view classes for intranet

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements

from cubes.tag.views import TagsCloudBox

TagsCloudBox.visible = True
TagsCloudBox.__select__ &= implements('BlogEntry', 'Link', 'Card', 'File', 'Image')
