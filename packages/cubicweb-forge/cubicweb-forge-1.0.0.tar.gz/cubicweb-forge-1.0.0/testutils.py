"""some utilities for testing forge security

:organization: Logilab
:copyright: 2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.devtools import BaseApptestConfiguration
from cubicweb.devtools.apptest import RepositoryBasedTC
from cubicweb.common import Unauthorized, ValidationError


def create_project_rql(pname):
    return 'INSERT Project X: X name %(name)s, X in_state S WHERE S name "active development"', \
           {'name': unicode(pname)}

def create_ticket_rql(title, pname):
    return 'INSERT Ticket X: X title %(title)s, X concerns P, X in_state S WHERE P name %(name)s, S name "open"', \
           {'title': unicode(title), 'name': unicode(pname)}

def create_version_rql(num, pname):
    return 'INSERT Version X: X num %(num)s, X version_of P, X in_state S '\
           'WHERE P name %(name)s, S name "planned", S state_of ET, ET name "Version"', \
           {'num': unicode(num), 'name': unicode(pname)}


class SecurityTC(RepositoryBasedTC):
    repo_config = BaseApptestConfiguration('data')
    _initialized = False
    def setUp(self):
        RepositoryBasedTC.setUp(self)
        self.__cnxs = {}
        # trick to avoid costly initialization for each test
        if not self._initialized:
            # implicitly test manager can add some entities
            self.execute(*create_project_rql("projet1"))[0][0]
            self.execute(*create_project_rql("projet2"))
            self.execute('INSERT CWGroup X: X name "projet1developers"')
            self.execute('INSERT CWGroup X: X name "projet1clients"')
            self.grant_permission('projet1', 'projet1developers', u'developer')
            self.grant_permission('projet1', 'projet1clients', u'client')
            self.execute('INSERT License X: X name "license"')
            self.execute('INSERT ExtProject X: X name "projet externe"')
            self.commit()
            self.create_user('stduser')
            self.create_user('staffuser', groups=('users', 'staff',))
            self.create_user('prj1developer', groups=('users', 'projet1developers',))
            self.create_user('prj1client', groups=('users', 'projet1clients'))
            self.maxeid = self.execute('Any MAX(X)')[0][0]
            SecurityTC._initialized = True
            cachedperms = self.execute('Any UL, PN WHERE U has_group_permission P, U login UL, P label PN')
            self.assertEquals(len(cachedperms), 2)
            self.assertEquals(dict(cachedperms),
                              {'prj1developer': 'projet1developers', 'prj1client': 'projet1clients'})
            
    def mylogin(self, user):
        if not user in self.__cnxs:
            self.__cnxs[user] = self.login(user)
        return self.__cnxs[user]

    def _test_tr_fail(self, user, x, state):
        cnx = self.mylogin(user)
        try:
            cu = cnx.cursor()
            # if the user can't see entity x, Unauthorized is raised, else if he
            # can't pass the transition, Validation is raised
            self.assertRaises((Unauthorized, ValidationError),
                              cu.execute,
                              'SET X in_state S WHERE X eid %(x)s, S name %(state)s',
                              {'x': x, 'state': state}, 'x')
        finally:
            cnx.rollback()
        
    def _test_tr_success(self, user, x, state):
        cnx = self.mylogin(user)
        try:
            cu = cnx.cursor()
            cu.execute('SET X in_state S WHERE X eid %(x)s, S name %(state)s',
                       {'x': x, 'state': state}, 'x')
            s = cu.execute('Any SN WHERE X eid %(x)s, X in_state S, S name SN', {'x': x}, 'x')[0][0]
            self.assertEquals(s, state)
            cnx.commit()
        except:
            cnx.rollback()
            raise

    def grant_permission(self, project, group, pname, etype='Project', plabel=None):
        """insert a permission on a project. Will have to commit the main
        connection to be considered
        """
        plabel = plabel or unicode(group)
        peid = self.execute('INSERT CWPermission X: X name %%(pname)s, X label %%(plabel)s,'
                            'X require_group G, '
                            'P require_permission X '
                            'WHERE G name %%(group)s, P is %s, P name %%(project)s' % etype,
                            locals())[0][0]
        return peid
        
