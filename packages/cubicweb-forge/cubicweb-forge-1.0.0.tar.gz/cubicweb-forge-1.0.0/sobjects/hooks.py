"""Forge specific hooks

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

import sys
from itertools import chain
from datetime import datetime

from cubicweb import ValidationError, RepositoryError
from cubicweb.server.hooksmanager import Hook
from cubicweb.server.hookhelper import previous_state
from cubicweb.sobjects.notification import RenderAndSendNotificationView

class BeforeStatusChangeHook(Hook):
    """
    * when a Version is going from "planned" to "in developent", search
      for related test cards and create a test instance for each of them

    * when a ticket is done, automatically set its version'state
      to 'dev' if necessary
    """
    events = ('before_add_relation',)
    accepts = ('in_state',)

    def call(self, session, fromeid, rtype, toeid):
        etype = session.describe(fromeid)[0]
        if etype not in ('Version', 'Ticket'):
            return
        state = previous_state(session, fromeid)
        if state is None or state.eid == toeid:
            # not a transition
            return
        newstate = session.entity(toeid).name
        if etype == 'Version' and newstate == 'dev':
            self.copy_cards(session, fromeid)
        elif etype == 'Ticket':
            if newstate in ('in-progress', 'validation pending'):
                entity = session.entity(fromeid)
                self.start_version_dev(entity)
            if newstate in ('validation pending', 'rejected', 'deprecated'):
                session.unsafe_execute('SET X load_left 0 WHERE X eid %(x)s',
                                       {'x': fromeid}, 'x')
                if newstate in ('rejected', 'deprecated'):
                    entity = session.entity(fromeid)
                    if entity.load is None:
                        session.unsafe_execute('SET X load 0 WHERE X eid %(x)s',
                                               {'x': fromeid}, 'x')

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
                                   'X instance_of C, X for_version V, X in_state S '
                                   'WHERE C eid %(c)s, V eid %(v)s, S name "todo"',
                                   {'v': veid, 'c': eid, 'name': title})

    def start_version_dev(self, bsentity):
        version = bsentity.in_version()
        if version and version.in_state[0].name == 'planned':
            version.req.execute('SET X in_state S WHERE X eid %(x)s, S name "dev"',
                                {'x': version.eid}, 'x')


class InVersionChangeHook(Hook):
    """
    * when a ticket is attached to a version and it's identical to another
      one, attach the other one as well

    * when a ticket status change and it's identical to another one, change
      the state of the other one as well
    """
    events = ('after_add_relation',)
    accepts = ('in_state', 'done_in',)


    def call(self, session, fromeid, rtype, toeid):
        etype = session.describe(fromeid)[0]
        if etype != 'Ticket':
            return
        entity = session.entity(fromeid)
        if rtype == 'done_in':
            self.sync_version(entity, toeid)
        else: # in_state
            self.sync_state(entity, toeid)

    def sync_version(self, entity, veid):
        execute = entity.req.execute
        for identic in entity.identical_to:
            iversion = identic.in_version()
            iveid = iversion and iversion.eid
            if iveid == veid:
                continue
            try:
                execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                        {'x': identic.eid, 'v': veid}, 'x')
            except:
                self.exception("can't synchronize version")

    def sync_state(self, entity, seid):
        pstate = previous_state(entity.req, entity.eid)
        execute = entity.req.execute
        for identic in entity.identical_to:
            if not identic.in_state or (
                identic.in_state[0].eid == pstate.eid
                and identic.in_state[0].eid != seid):
                execute('SET X in_state S WHERE X eid %(x)s, S eid %(s)s',
                        {'x': identic.eid, 's': seid}, 'x')


class ProjectAddedHook(Hook):
    """automatically register the user creating a project as interested by it
    """
    events = ('after_add_entity',)
    accepts = ('Project',)

    def call(self, session, entity):
        if not session.is_internal_session:
            asession = session.actual_session()
            asession.execute('SET U interested_in X WHERE X eid %(x)s, U eid %(u)s',
                             {'x': entity.eid, 'u': asession.user.eid}, 'x')


class SetTicketLoadLeft(Hook):
    """automatically set load_left according to load if unspecified"""
    events = ('before_add_entity', 'before_update_entity')
    accepts = ('Ticket',)

    def call(self, session, entity):
        has_load_left = 'load_left' in entity
        if entity.load_left is None and 'load' in entity:
            entity['load_left'] = entity['load']
        elif not has_load_left and 'load_left' in entity:
            # cleanup, this may cause undesired changes
            del entity['load_left']

class CheckVersionNameOfAProject(Hook):
    """check that the vesion name does not already exist"""
    events = ('before_add_relation',)
    accepts = ('version_of',)

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity(fromeid)
        project = session.entity(toeid)
        rset = session.execute(
            'Any X WHERE X num %(num)s, X version_of P, P eid %(p)s',
            {'num': entity.num, 'p': project.eid})
        if rset and (len(rset)>1 or rset[0][0] != entity.eid):
            msg = _(u'%(vnum)s release number already exists for the project %(prj)s') % {
                'vnum': entity.num, 'prj': project.name}
            raise ValidationError(entity.eid, {"num": msg})

class SetModificationDateAfterChangeState(Hook):
    """update entity's modification date after changing its state"""
    events = ('after_add_relation',)
    accepts = ('in_state',)

    def call(self, session, fromeid, rtype, toeid):
        # XXX move to cw
        entity = session.entity(fromeid)
        rql = 'SET X modification_date %(d)s WHERE X eid %(x)s'
        try:
            session.unsafe_execute(rql, {'x': entity.eid, 'd': datetime.now()}, 'x')
        except RepositoryError, ex:
            # usually occurs if entity is coming from a read-only source
            # (eg ldap user)
            self.warning('cant change modification date for %s: %s', entity, ex)


class SetModificationDateAfterAddComment(Hook):
    """update entity's modification date after adding a comment"""
    events = ('after_add_relation',)
    accepts = ('comments',)

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity(toeid)
        while entity.e_schema == 'Comment':
            entity = entity.root()
        rql = 'SET X modification_date %(d)s WHERE X eid %(x)s'
        session.unsafe_execute(rql, {'x': entity.eid, 'd': datetime.now()}, 'x')


class BeforeUpdateTicket(Hook):
    events = ('before_update_entity',)
    accepts = ('Ticket',)

    def call(self, session, entity):
        if 'priority' in entity:
            view = session.vreg.select_view('notif_priority_changed',
                                            session, entity.as_rset(), row=0)

            oldpriority = session.execute('Any P WHERE X eid %(x)s, X priority P',
                                       {'x' : entity.eid})[0][0]
            RenderAndSendNotificationView(session, view=view,
                                          viewargs={'oldpriority': oldpriority})
