"""hook to normalize tag names

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.server.hooksmanager import Hook


class AddUpdateTagHook(Hook):
    """ensure tag names are lower case and commas are forbidden"""
    events = ('before_add_entity', 'before_update_entity',)
    accepts = ('Tag',)

    def call(self, session, entity):
        if 'name' in entity:
            name = entity['name'].lower()
            name = ' - '.join(part.strip() for part in name.split(','))
            entity['name'] = name
