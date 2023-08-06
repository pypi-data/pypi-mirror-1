"""forge hooks for permission propagation

:organization: Logilab
:copyright: 2008-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.server.hooksmanager import Hook
from cubicweb.server.pool import PreCommitOperation

# relations where the "main" entity is the subject
S_RELS = ('documented_by', 'attachment', 'screenshot') 
# relations where the "main" entity is the object
O_RELS = ('concerns', 'version_of',
          'test_case_of', 'test_case_for', 'for_version', 
          'comments',
          )
# XXX: uses, recommends, see_also

class RQLPrecommitOperation(PreCommitOperation):
    def precommit_event(self):
        execute = self.session.unsafe_execute
        for rql in self.rqls:
            execute(*rql)
    

class AddEntitySecurityPropagationHook(Hook):
    """propagate permissions when new entity are added"""
    events = ('after_add_relation',)
    accepts = S_RELS + O_RELS

    # not necessary on:
    #
    # * "secondary" relations: todo_by, done_in, appeared_in, depends_on,
    #   generate_bug, instance_of
    #
    # * no propagation needed: mailinglist_of, wf_info_for
    
    def call(self, session, fromeid, rtype, toeid):
        for eid in (fromeid, toeid):
            etype = session.describe(eid)[0]
            if not self.schema.eschema(etype).has_subject_relation('require_permission'):
                return
        if rtype in S_RELS:
            meid, seid = fromeid, toeid
        else:
            meid, seid = toeid, fromeid
        RQLPrecommitOperation(session, rqls=[
            ('SET E require_permission P WHERE X require_permission P, '
             'X eid %(x)s, E eid %(e)s, NOT E require_permission P',
             {'x': meid, 'e': seid}, ('x', 'e'))])


class AddPermissionSecurityPropagationHook(Hook):
    """propagate on existing entities when a permission is added"""
    events = ('after_add_relation',)
    accepts = ('require_permission',)

    def call(self, session, fromeid, rtype, toeid):
        eschema = self.schema.eschema(session.describe(fromeid)[0])
        rqls = []
        for rel in S_RELS:
            if eschema.has_subject_relation(rel):
                rqls.append(('SET R require_permission P WHERE '
                             'X eid %%(x)s, P eid %%(p)s, X %s R, '
                             'NOT R require_permission P' % rel,
                             {'x': fromeid, 'p': toeid}, 'x'))
        for rel in O_RELS:
            if eschema.has_object_relation(rel):
                rqls.append(('SET R require_permission P WHERE '
                             'X eid %%(x)s, P eid %%(p)s, R %s X, '
                             'NOT R require_permission P' % rel,
                             {'x': fromeid, 'p': toeid}, 'x'))
        if rqls:
            RQLPrecommitOperation(session, rqls=rqls)


class DelPermissionSecurityPropagationHook(Hook):
    """propagate on existing entities when a permission is deleted"""
    events = ('after_delete_relation',)
    accepts = ('require_permission',)

    def call(self, session, fromeid, rtype, toeid):
        eschema = self.schema.eschema(session.describe(fromeid)[0])
        rqls = []
        for rel in S_RELS:
            if eschema.has_subject_relation(rel):
                rqls.append(('DELETE R require_permission P WHERE '
                             'X eid %%(x)s, P eid %%(p)s, X %s R' % rel,
                             {'x': fromeid, 'p': toeid}, 'x'))
        for rel in O_RELS:
            if eschema.has_object_relation(rel):
                rqls.append(('DELETE R require_permission P WHERE '
                             'X eid %%(x)s, P eid %%(p)s, R %s X' % rel,
                             {'x': fromeid, 'p': toeid}, 'x'))
        if rqls:
            RQLPrecommitOperation(session, rqls=rqls)


class AddGroupPermissionSecurityPropagationHook(Hook):
    """propagate on group users when a permission is granted to a group"""
    events = ('after_add_relation',)
    accepts = ('require_group',)
    rql = ('SET U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT U has_group_permission P')

    def call(self, session, fromeid, rtype, toeid):
        if session.describe(fromeid)[0] != 'CWPermission':
            return
        session.unsafe_execute(self.rql, {'p': fromeid, 'g': toeid},)


class DelGroupPermissionSecurityPropagationHook(AddGroupPermissionSecurityPropagationHook):
    """propagate on group users when a permission is removed to a group"""
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT EXISTS(U in_group G2, P require_group G2)')


class AddInGroupSecurityPropagationHook(Hook):
    """propagate group permission to users when a permission is granted to a group"""
    events = ('after_add_relation',)
    accepts = ('in_group',)
    rql = ('SET U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT U has_group_permission P')

    def call(self, session, fromeid, rtype, toeid):
        session.unsafe_execute(self.rql, {'u': fromeid, 'g': toeid})


class DelInGroupSecurityPropagationHook(AddInGroupSecurityPropagationHook):
    """propagate on existing entities when a permission is deleted"""
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT EXISTS(U in_group G2, P require_group G2)')
