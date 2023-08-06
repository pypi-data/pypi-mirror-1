"""This cube handles classification schemes.

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

class Classification(MetaUserEntityType):
    """classification schemes are used by users to classify entities.
    """
    permissions = {
        'read' : ('managers', 'users', 'guests'),
        'add' : ('managers',),
        'delete' : ('managers',),
        'update' : ('managers',),
        }
    name = String(required=True, fulltextindexed=True, unique=True,
                  maxsize=128)
    classifies = SubjectRelation('CWEType',
                                 # see relation type docstring
                                 constraints = [RQLConstraint('RDEF to_entity O, RDEF relation_type R, R name "applied_to"')])


class classifies(MetaUserRelationType):
    """entity types classified by the classification. Only entity type
    supporting the applied_to relation can be selectioned
    """


class Keyword(MetaUserEntityType):
    """A keyword is like a tag but is application specific
    and used to define a classification scheme
    """
    permissions = {
        #'read' : ('managers', 'users', 'guests'),
        'read' : ('managers',
                  ERQLExpression('X in_state ST, ST name "keyword validated"'),
                  ERQLExpression('X owned_by U')),
        'add' : ('managers', 'users'),
        'delete' : ('managers',),
        'update' : ('managers',),
        }
    name = String(required=True, fulltextindexed=True, indexed=True, maxsize=128)

    subkeyword_of = SubjectRelation('Keyword', cardinality='?*',
                                    description=_('which keyword (if any) this keyword specializes'),
                                    # if no included_in set, it'll be automatically added by a hook
                                    constraints=[RQLConstraint('NOT S included_in CS1 OR EXISTS(S included_in CS2, O included_in CS2)')])
    included_in = SubjectRelation('Classification', cardinality='1*')

    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, S is ET')],
                               description=_('keyword status'))
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')



class subkeyword_of(MetaUserRelationType):
    """a keyword can specialize another keyword"""


class included_in(MetaUserRelationType):
    """a keyword is included in a classification scheme"""
    inlined = True


# define in parent application which entity types may be linked to a keyword
# by the applied_to relation
class applied_to(MetaUserRelationType):
    """tagged objects"""
    fulltext_container = 'object'
    constraints = [RQLConstraint('S included_in CS, O is ET, CS classifies ET')]
