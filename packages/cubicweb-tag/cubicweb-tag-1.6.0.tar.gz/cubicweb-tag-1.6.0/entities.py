"""entity class for Tag entities

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config

class Tag(AnyEntity):
    """customized class for Tag entities"""
    __regid__ = 'Tag'
    fetch_attrs, fetch_order = fetch_config(['name'])

    def rss_feed_url(self):
        rql = ('Any X ORDERBY CD DESC LIMIT 15 '
               'WHERE T tags X, T eid %s, X modification_date CD') % self.eid
        return self._cw.build_url(rql=rql, vid='rss', vtitle=self.dc_title())

    def closest_tags_rset(self):
        return self._cw.execute('Any CT, COUNT(X) GROUPBY CT ORDERBY 2 DESC '
                                'LIMIT 5 '
                                'WHERE T tags X, T eid %(x)s, CT tags X, '
                                'NOT CT eid %(x)s', {'x': self.eid}, 'x')

