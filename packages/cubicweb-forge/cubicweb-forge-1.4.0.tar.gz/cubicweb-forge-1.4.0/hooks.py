"""Forge cube hooks

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from itertools import chain
from datetime import datetime

from cubicweb.server.hook import Hook, Operation
from cubicweb.selectors import implements
from cubicweb.server import hook

from cubes.tracker import hooks as tracker
from cubes.nosylist import hooks as nosylist


# configure dependency cubes hooks #############################################

tracker.VersionStatusChangeHook.ticket_states_start_version.add('done')
tracker.VersionStatusChangeHook.ticket_states_start_version.add('validation pending')

# permission propagation configuration
# not necessary on: generate_bug, instance_of, recommends, mailinglist_of
tracker.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))
tracker.O_RELS |= set(('test_case_of', 'test_case_for', 'for_version',
                       'comments'))


nosylist.S_RELS |= tracker.S_RELS
nosylist.O_RELS |= tracker.O_RELS


# forge specific hooks #########################################################

class ChangeTicketStateOnVersionStatusChange(Hook):
    __regid__ = 'change_ticket_state_on_version_status_change'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & implements('TrInfo')

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Version':
            return
        if self.entity.new_state.name == 'published':
            for ticket in forentity.reverse_done_in:
                if ticket.state == 'done':
                    msg = self._cw._('version published')
                    ticket.fire_transition('ask validation',
                                           comment=msg,
                                           commentformat=u'text/plain')


class AdjustPendingTicketState(Operation):
    def precommit_event(self):
        if (self.ticket.state == 'validation pending' and
            (not self.ticket.done_in
             or self.ticket.done_in[0].state != 'published')):
            msg = self.session._('moved away from published version')
            self.ticket.change_state('open',
                                     comment=msg,
                                     commentformat=u'text/plain')


class ChangeTicketStateOnDoneInChange(Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'change_ticket_state_on_done'
    events = ('after_delete_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('done_in',)

    def __call__(self):
        asession = self._cw.actual_session()
        ticket = self._cw.entity_from_eid(self.eidfrom)
        version = self._cw.entity_from_eid(self.eidto)
        if ticket.state == 'validation pending':
            AdjustPendingTicketState(self._cw, ticket=ticket)


class ResetLoadLeftOnTicketStatusChange(Hook):
    __regid__ = 'reset_load_left_on_ticket'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & implements('TrInfo',)

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Ticket':
            return
        newstate = self.entity.new_state.name
        if newstate in ('done', 'rejected', 'deprecated'):
            # ticket is done, set load_left to 0
            forentity.set_attributes(load_left=0, _cw_unsafe=True)
            if newstate in ('rejected', 'deprecated'):
                # also reset load in that case, we don't want initial estimation
                # to be taken into account
                forentity.set_attributes(load=0, _cw_unsafe=True)


class SetTicketLoadLeft(Hook):
    """automatically set load_left according to load if unspecified"""
    __regid__ = 'set_ticket_load'
    events = ('before_add_entity', 'before_update_entity')
    __select__ = Hook.__select__ & implements('Ticket',)

    def __call__(self):
        # XXX use edited_attributes
        has_load_left = 'load_left' in self.entity
        if self.entity.load_left is None and 'load' in self.entity:
            self.entity.load_left = self.entity['load']
        elif not has_load_left and 'load_left' in self.entity:
            # cleanup, this may cause undesired changes
            del self.entity['load_left']


class SetNosyListBeforeAddComment(Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'set_nosy_list_before_add_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        if self._cw.is_internal_session:
            return
        asession = self._cw.actual_session()
        comment = self._cw.entity_from_eid(self.eidfrom)
        entity = comment.root()
        if 'nosy_list' in entity.e_schema.subject_relations():
            x = entity.eid
        else:
            x = comment.eid
        self._cw.unsafe_execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                               'NOT X nosy_list U',
                               {'x': x, 'u': asession.user.eid}, 'x')


class SetModificationDateAfterAddComment(Hook):
    """update root entity's modification date after adding a comment"""
    __regid__ = 'set_modification_date_after_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidto)
        while entity.e_schema == 'Comment':
            entity = entity.root()
        rql = 'SET X modification_date %(d)s WHERE X eid %(x)s'
        self._cw.unsafe_execute(rql, {'x': entity.eid, 'd': datetime.now()}, 'x')


class TicketDoneInProgressHook(Hook):
    __regid__ = 'ticket_done_in_progress'
    __select__ = Hook.__select__ & hook.match_rtype('done_in',)
    events = ('after_add_relation', 'after_delete_relation', )

    def __call__(self):
        version = self._cw.entity_from_eid(self.eidto)
        version.update_progress()


class TicketProgressHook(Hook):
    __regid__ = 'ticket_progress'
    __select__ = Hook.__select__ & implements('Ticket',)
    events = ('after_update_entity', )

    def __call__(self):
        if 'load' in self.entity.edited_attributes or \
               'load_left' in self.entity.edited_attributes:
            try:
                self.entity.done_in[0].update_progress()
            except IndexError:
                # not yet attached to a version
                pass
