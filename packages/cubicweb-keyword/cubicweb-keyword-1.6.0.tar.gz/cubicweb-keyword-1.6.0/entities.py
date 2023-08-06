"""entity classes for classification schemes entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.mixins import MI_REL_TRIGGERS, TreeMixIn
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ITree


class Classification(AnyEntity):
    __regid__ = 'Classification'
    fetch_attrs, fetch_order = fetch_config(['name'])
    __implements__ = AnyEntity.__implements__ + (ITree,)

    def root(self):
        """returns the root object"""
        return None

    def parent(self):
        """returns the parent entity"""
        return None

    def iterparents(self):
        """returns parent entities"""
        yield self

    def children(self, entities=True):
        """returns the item's children"""
        return self.related('included_in', 'object', entities=entities)

    def children_rql(self):
        """XXX returns RQL to get children"""
        return self.related_rql('included_in', 'object')

    def is_leaf(self):
        """returns true if this node as no child"""
        return bool(self.children())

    def is_root(self):
        """returns true if this node has no parent"""
        return True

    def first_level_keywords(self):
        return self.req.execute('Any K,N ORDERBY N WHERE K included_in C, '
                                'NOT K subkeyword_of KK, K name N, '
                                'C eid %(x)s', {'x': self.eid})


class Keyword(TreeMixIn, AnyEntity):
    __regid__ = 'Keyword'
    fetch_attrs, fetch_order = fetch_config(['name'])
    __implements__ = AnyEntity.__implements__ + (ITree,)

    tree_attribute = 'subkeyword_of'

    @property
    def classification(self):
        if self.included_in:
            return self.included_in[0]
        return None

    def parent(self):
        """IBreadcrumbs implementation"""
        if self.subkeyword_of:
            return self.subkeyword_of[0]
        return self.classification

    def iterparents(self):
        """returns parent keyword entities
        """
        if self.subkeyword_of:
            parent = self.subkeyword_of[0]
            while parent is not None:
                yield parent
                if parent.subkeyword_of:
                    parent = parent.subkeyword_of[0]
                else:
                    parent = None

    def children(self, entities=True):
        """returns the item's children

        we have only one direct child by ``subkeyword_of`` relation"""
        assert 1 == len(self.reverse_subkeyword_of)
        return iter(self.reverse_subkeyword_of)

    def iterchildren(self):
        """returns children entities"""
        if self.reverse_subkeyword_of:
            child = self.reverse_subkeyword_of[0]
            while child is not None:
                yield child
                if child.reverse_subkeyword_of:
                    child = child.reverse_subkeyword_of[0]
                else:
                    child = None

    def is_leaf(self):
        if self.reverse_subkeyword_of:
            return False
        return True

    def children_rql(self):
        return 'Any K WHERE  K subkeyword_of X, X eid %(x)s'

    """
    # FIXME unittest
    def subkeywords(self, recursive=True):
        rset = self.req.execute(self.children_rql(), {'x': self.eid})
        subentities = list(rset.entities())
        if recursive:
            for entity in subentities[:]:
                subentities.extend(entity.subkeywords(recursive=True))
        return subentities
    """

class CodeKeyword(Keyword):
    __regid__ = 'CodeKeyword'
    rest_attr = 'code'
    fetch_attrs, fetch_order = fetch_config(['code','name'])

    def dc_title(self):
        return u'%s - %s' % (self.code, self.name)


class ClassifiableMixIn(object):
    """mixin automatically plugged to entity types supporting the applied_to
    relation
    """
    def classification_keywords(self, name):
        """return keywords of the given classification linked to this entity"""
        return self.req.execute('Any K, KN WHERE K applied_to X, X eid %(x)s, '
                                'K name KN, K included_in CS, CS name %(name)s',
                                {'x': self.eid, 'name': name}, 'x')

MI_REL_TRIGGERS[('applied_to', 'object')] = ClassifiableMixIn
