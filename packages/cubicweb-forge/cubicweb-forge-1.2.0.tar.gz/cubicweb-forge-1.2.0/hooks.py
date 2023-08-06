"""Forge cube hooks

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from itertools import chain
from datetime import datetime

from cubicweb.server import hooksmanager

from cubes.tracker import hooks as tracker
from cubes.nosylist import hooks as nosylist


# configure dependency cubes hooks #############################################

tracker.VersionStatusChangeHook.ticket_states_start_version.add('in-progress')
tracker.VersionStatusChangeHook.ticket_states_start_version.add('validation pending')

# permission propagation configuration
# not necessary on: generate_bug, instance_of, recommends, mailinglist_of
tracker.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))
tracker.O_RELS |= set(('test_case_of', 'test_case_for', 'for_version',
                       'comments'))


nosylist.INotificationBaseAddedHook.accepts.append('Project')
nosylist.INotificationBaseAddedHook.accepts.append('Ticket')
nosylist.S_RELS |= tracker.S_RELS
nosylist.O_RELS |= tracker.O_RELS


# forge specific hooks #########################################################

class MakeTestInstancesOnVersionStatusChange(hooksmanager.Hook):
    """when a Version is going from 'planned' to 'in development', search
    for related test cards and create a test instance for each of them
    """
    events = ('after_add_entity',)
    accepts = ('TrInfo',)

    def call(self, session, entity):
        forentity = entity.for_entity
        if forentity.e_schema  != 'Version':
            return
        if forentity.state == 'dev':
            self.copy_cards(session, forentity.eid)

    def copy_cards(self, session, veid):
        # get cards for past stories
        rset1 = session.execute('Any X,XT WHERE X test_case_of P, X test_case_for S, S in_state ST,'
                                'ST name "done", V version_of P, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid}, 'v')
        # get cards for stories in this version
        rset2 = session.execute('Any X,XT WHERE X test_case_of P, X test_case_for S,'
                                'S done_in V, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid}, 'v')
        # get general cards (not related to a particular story
        rset3 = session.execute('Any X,XT WHERE X test_case_of P, NOT X test_case_for S,'
                                'V version_of P, V eid %(v)s, X title XT,'
                                'NOT EXISTS(TI instance_of X, TI for_version V)',
                               {'v': veid}, 'v')
        done = set()
        for eid, title in chain(rset1, rset2, rset3):
            if eid in done:
                continue
            done.add(eid)
            session.unsafe_execute('INSERT TestInstance X: X name %(name)s,'
                                   'X instance_of C, X for_version V '
                                   'WHERE C eid %(c)s, V eid %(v)s',
                                   {'v': veid, 'c': eid, 'name': title})


class ResetLoadLeftOnTicketStatusChange(hooksmanager.Hook):
    events = ('after_add_entity',)
    accepts = ('TrInfo',)

    def call(self, session, entity):
        forentity = entity.for_entity
        if forentity.e_schema != 'Ticket':
            return
        newstate = forentity.state
        if newstate in ('validation pending', 'rejected', 'deprecated'):
            # ticket is done, set load_left to 0
            forentity.set_attributes(load_left=0, _cw_unsafe=True)
            if newstate in ('rejected', 'deprecated'):
                # also reset load in that case, we don't want initial estimation
                # to be taken into account
                forentity.set_attributes(load=0, _cw_unsafe=True)


class SetTicketLoadLeft(hooksmanager.Hook):
    """automatically set load_left according to load if unspecified"""
    events = ('before_add_entity', 'before_update_entity')
    accepts = ('Ticket',)

    def call(self, session, entity):
        # XXX use edited_attributes
        has_load_left = 'load_left' in entity
        if entity.load_left is None and 'load' in entity:
            entity.load_left = entity['load']
        elif not has_load_left and 'load_left' in entity:
            # cleanup, this may cause undesired changes
            del entity['load_left']


class SetNosyListBeforeAddComment(hooksmanager.Hook):
    """automatically add user who adds a comment to the nosy list"""
    events = ('after_add_relation',)
    accepts = ('comments',)

    def call(self, session, fromeid, rtype, toeid):
        if session.is_internal_session:
            return
        asession = session.actual_session()
        comment = session.entity_from_eid(fromeid)
        entity = comment.root()
        if 'nosy_list' in entity.e_schema.subject_relations():
            x = entity.eid
        else:
            x = comment.eid
        session.unsafe_execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                               'NOT X nosy_list U',
                               {'x': x, 'u': asession.user.eid}, 'x')


class SetModificationDateAfterAddComment(hooksmanager.Hook):
    """update root entity's modification date after adding a comment"""
    events = ('after_add_relation',)
    accepts = ('comments',)

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity_from_eid(toeid)
        while entity.e_schema == 'Comment':
            entity = entity.root()
        rql = 'SET X modification_date %(d)s WHERE X eid %(x)s'
        session.unsafe_execute(rql, {'x': entity.eid, 'd': datetime.now()}, 'x')


class TicketDoneInProgressHook(hooksmanager.Hook):

    accepts = ('done_in',)
    events = ('after_add_relation', 'after_delete_relation', )

    def call(self, session, from_eid, rtype, to_eid):
        version = session.entity_from_eid(to_eid)
        version.update_progress()


class TicketProgressHook(hooksmanager.Hook):

    accepts = ('Ticket',)
    events = ('after_update_entity', )

    def call(self, session, entity):
        if 'load' in entity.edited_attributes or \
               'load_left' in entity.edited_attributes:
            try:
                entity.done_in[0].update_progress()
            except IndexError:
                # not yet attached to a version
                pass
