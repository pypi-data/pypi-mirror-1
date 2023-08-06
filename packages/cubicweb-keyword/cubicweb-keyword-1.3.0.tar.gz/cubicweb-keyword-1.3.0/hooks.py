"""specific hooks for Classification and Keyword entities

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from logilab.common.decorators import cached

from cubicweb import ValidationError
from cubicweb.selectors import implements
from cubicweb.server.hooksmanager import Hook
from cubicweb.server.pool import PreCommitOperation
from cubicweb.sobjects.notification import (ContentAddedView, NotificationView,
                                            StatusChangeMixIn)

class BeforeKeywordApplicationHook(Hook):
    """
    * when a keyword is applied to an entity, we make sure the entity
      type is actually related to the classification the keyword is
      included in
    """

    events = ('before_add_relation',)
    accepts = ('applied_to',)

    def call(self, session, fromeid, rtype, toeid):
        # XXX this could be expressed as a constraint in the schema, no?
        rset = session.execute('Any C WHERE C classifies ET, K included_in C, '
                               'X is ET, X eid %(x)s, K eid %(k)s',
                               {'x' : toeid, 'k' : fromeid})
        if not rset:
            msg = session._("this keyword can't be applied to this kind of entity")
            raise ValidationError(None, msg)


class SetIncludedInRelationOp(PreCommitOperation):
    """delay this operation to commit to avoid conflict with a late rql query
    already setting the relation
    """
    def precommit_event(self):
        session = self.session
        # test for indirect cycles
        toeid = self.toeid
        fromeid = self.fromeid
        parents = [toeid]
        parent = session.entity(toeid)
        while parent.subkeyword_of:
            parent = parent.subkeyword_of[0]
            if parent.eid in parents:
                raise ValidationError(None,
                                      session._('detected subkeyword cycle for keyword %(kw)s') %
                                      {'kw' : fromeid})
        subkw = session.eid_rset(fromeid).get_entity(0, 0)
        if subkw.included_in:
            kw = session.eid_rset(toeid).get_entity(0, 0)
            if subkw.included_in[0].eid != kw.included_in[0].eid:
                msgid = "keywords %(subkw)s and %(kw)s belong to different classifications"
                raise ValidationError(subkw.eid,  {'subkeyword_of': session._(msgid) %
                                                   {'subkw' : subkw.eid, 'kw' : kw.eid}})
        else:
            session.execute('SET SK included_in C WHERE SK eid %(x)s, '
                            'SK subkeyword_of K, K included_in C',
                            {'x': subkw.eid}, 'x')


class SetIncludedInRelationHook(Hook):
    """sets the included_in relation on a subkeyword if not already set
    """
    events = ('before_add_relation',)
    accepts = ('subkeyword_of',)

    def call(self, session, fromeid, rtype, toeid):
        # immediate test direct cycles
        if fromeid == toeid:
            raise ValidationError(None,
                                  session._('keyword %(kw)s cannot be subkeyword of himself') %
                                  {'kw' : fromeid})
        SetIncludedInRelationOp(session, vreg=self.vreg,
                                fromeid=fromeid, toeid=toeid)



class KeywordNotificationView(NotificationView):
    __select__ = implements('Keyword')
    msgid_timestamp = True

    def recipients(self):
        """Returns the project's interested people (entities)"""
        creator = self.entity(0).created_by[0]
        if not creator.is_in_group('managers') and creator.primary_email:
            return [(creator.primary_email[0].address, 'fr')]
        return []

    def context(self, **kwargs):
        context = NotificationView.context(self, **kwargs)
        entity = self.entity(0)
        context['kw'] = entity.name
        return context


class KeywordStatusChanged(StatusChangeMixIn, KeywordNotificationView):
    content = _("""
The state of keyword %(kw)s is now %(current_state)s
""")

    def subject(self):
        entity = self.entity(0)
        return self.req._('keyword %s is not in state %s') % (
            entity.name, self._kwargs['current_state'])


class KeywordNameChanged(KeywordNotificationView):
    id = 'notif_after_update_entity'

    content = _("keyword name changed from %(oldname)s to %(kw)s")

    @cached
    def get_oldname(self, entity):
        session = self.req
        try:
            return session.execute('Any N WHERE X eid %(x)s, X name N',
                                   {'x' : entity.eid}, 'x')[0][0]
        except IndexError:
            return u'?'

    def context(self, **kwargs):
        entity = self.entity(0)
        context = KeywordNotificationView.context(self, **kwargs)
        context['oldname'] = self.get_oldname(entity)
        return context

    def subject(self):
        entity = self.entity(0)
        return self.req._('keyword name changed from %s to %s') % (
            self.get_oldname(entity), entity.name)


class KeywordAddedView(ContentAddedView):
    """get notified from new keywords"""
    __select__ = implements('Keyword')
    content_attr = 'name'
    msgid_timestamp = True

    def recipients(self):
        dests = [add for add, in self.req.execute('Any A WHERE X is CWUser, X in_group G,'
                                                  'G name "managers", X in_state S, S name "activated",'
                                                  'X primary_email E, E address A')]
        if not dests:
            dests = self.config['default-dest-addrs']
        return [(add, 'fr') for add in dests]


class SetKeywordInitialStateOp(PreCommitOperation):
    """make initial state be a default state"""

    def precommit_event(self):
        session = self.session
        entity = self.entity
        if session.user.is_in_group('managers'):
            session.execute('SET X in_state ST WHERE ST name "keyword validated", X is ET, ST state_of ET, X eid %(x)s',
                            {'x' : entity.eid}, 'x')
        else:
            session.unsafe_execute('SET X in_state ST WHERE ST name "validation pending", X is ET, ST state_of ET, X eid %(x)s',
                                   {'x' : entity.eid}, 'x')


class AfterAddAnyEntity(Hook):
    """make initial state be a default state"""
    events = ('after_add_entity',)
    accepts = ('Keyword',)

    def call(self, session, entity):
        SetKeywordInitialStateOp(session, entity=entity)
