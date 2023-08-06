from datetime import timedelta

from cubes.tracker.test.test_multisources import BaseMSTC

class TwoSourcesTC(BaseMSTC):

    def test_projects_interested_in(self):
        rset = self.execute('Any P,N WHERE P name N, X interested_in P, X eid %(x)s', {'x': self.session.user.eid}, 'x')
        self.assertEquals(len(rset), 3)

    def test_nonregr2(self):
        self.execute('INSERT Card X: X title "test1", X test_case_of P WHERE P eid %(x)s', {'x': self.ip1eid})
        self.execute('INSERT Card X: X title "test2", X test_case_for T WHERE T eid %(x)s', {'x': self.ip1t1eid})
        self.commit()
        # test we can a change a ticket state (and implicitly its version'state by commiting
        self.fire_transition(self.ip1t1eid, 'start')
        self.commit()
        ip1v1 = self.execute('Any X WHERE X eid %(x)s', {'x': self.ip1v1eid}, 'x').get_entity(0, 0)
        self.assertEquals(ip1v1.state, 'dev')

    def test_nonregr6(self):
        rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                            {'text': 'extern'})
        self.assertEquals(len(rset), 2)
        rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                            {'text': 'intern'})
        self.assertEquals(len(rset), 3)
        rset = self.execute('Any E,F ORDERBY F WHERE X has_text %(text)s, X in_state E, E name F',
                            {'text': 'project'})
        # 3 projects in two external sources, 3 projects + 2 tickets in internal source
        self.assertEquals(len(rset), 8)
        self.assertEquals(set(sn for s, sn in rset), set(('active development', 'open')))

    def test_nonregr7(self):
        rset = self.execute('Any B,TT,NOW - CD,PR,S,C,V,group_concat(TN) '
                            'GROUPBY B,TT,CD,PR,S,C,V,VN '
                            'ORDERBY S, version_sort_value(VN), TT, priority_sort_value(PR) '
                            'LIMIT 1 '
                            'WHERE B type TT, B priority PR, B in_state S, B creation_date CD, B load C, T? tags B, T name TN, B done_in V?, V num VN, B concerns P, P eid %s'
                            % self.ip1eid)
        rset.rows[0][4] = 'STATE'
        self.assertEquals(rset.rows, [[self.ip1t1eid, u'bug', timedelta(0), u'normal', 'STATE', None, self.ip1v1eid, u'']])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
