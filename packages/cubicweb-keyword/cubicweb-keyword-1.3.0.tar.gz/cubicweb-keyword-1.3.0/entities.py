"""entity classes for classification schemes entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.common.mixins import TreeMixIn
from cubicweb.entities import AnyEntity, fetch_config

class Classification(AnyEntity):
    id = 'Classification'
    fetch_attrs, fetch_order = fetch_config(['name'])

    def parent(self):
        """overriden from TreeMixIn"""
        return None

    def children(self, entities=True):
        """TreeMixIn interface"""
        return self.related('included_in', 'object', entities=entities)


class Keyword(TreeMixIn, AnyEntity):
    id = 'Keyword'
    fetch_attrs, fetch_order = fetch_config(['name'])
    tree_attribute = 'subkeyword_of'

    @property
    def classification(self):
        return self.included_in[0]

    def parent(self):
        if self.subkeyword_of:
            return self.subkeyword_of[0]
        return self.classification

    def dc_long_title(self):
        try:
            return '%s (%s)' % (self.name, self.req._(self.state))
        except IndexError:
            # XXX no state yet, due to notification before state has been set
            return self.name
