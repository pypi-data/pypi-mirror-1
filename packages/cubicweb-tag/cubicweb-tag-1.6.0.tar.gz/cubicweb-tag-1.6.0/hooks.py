"""hook to normalize tag names

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.server.hook import Hook
from cubicweb.selectors import implements

class AddUpdateTagHook(Hook):
    """ensure tag names are lower case and commas are forbidden"""
    __regid__ = 'add_update_tag'
    events = ('before_add_entity', 'before_update_entity',)
    __select__ = Hook.__select__ & implements('Tag')

    def __call__(self):
        if 'name' in self.entity:
            name = self.entity['name'].lower()
            name = ' - '.join(part.strip() for part in name.split(','))
            self.entity['name'] = name
