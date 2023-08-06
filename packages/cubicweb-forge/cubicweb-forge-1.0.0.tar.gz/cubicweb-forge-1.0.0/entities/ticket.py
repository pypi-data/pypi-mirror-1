"""forge specific entities class for Ticket

:organization: Logilab
:copyright: 2006-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.interfaces import IPrevNext
from cubicweb.entities import AnyEntity

from cubes.forge.entities import fixed_orderby_rql


class Ticket(AnyEntity):
    id = 'Ticket'
    __permissions__ = ('developer', 'client')
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)

    fetch_attrs = ('title', 'type', 'priority', 'load', 'load_left', 'in_state')
    noload_cost = 10

    @classmethod
    def fetch_order(cls, attr, var):
        if attr == 'priority':
            return 'priority_sort_value(%s)' % var
        if attr in ('title', 'type'):
            return var
        return None

    @property
    def project(self):
        """project item interface"""
        return self.concerns[0]

    # hierarchy #############################################################

    def parent(self):
        parents = self.done_in or self.concerns
        if parents:
            return parents[0]

    # dublin core #############################################################

    def dc_title(self):
        return u'#%s: %s' % (self.eid, self.title)

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.dc_title())

    # ticket'specific logic ###################################################

    open_states = frozenset(('open', 'confirmed', 'waiting feedback', 'in-progress'))

    def is_open(self):
        return self.state in self.open_states

    def state_history(self):
        """returns a list of dates where the state changed from "open" to "not-open"
        :returns: a list couples of (date, is_open) 
        """
        dates = []
        for tr_info in self.reverse_wf_info_for:
            if not tr_info.previous_state:
                dates.append( (self.creation_date, True) )
                continue
            prevstate = tr_info.previous_state.name
            nextstate = tr_info.new_state.name
            if prevstate in self.open_states and nextstate not in self.open_states:
                dates.append( (tr_info.creation_date, False) )
            elif prevstate not in self.open_states and nextstate in self.open_states:
                dates.append( (tr_info.creation_date, True) )
        return sorted(dates)

    def in_version(self):
        versions = self.done_in
        if versions:
            return versions[0]

    def next_version(self):
        version = self.in_version()
        if version:
            return version.next_version()
        return self.project.latest_version(('planned', 'dev'), True)

    def corrected_load(self):
        if self.load is not None:
            return self.load
        return self.noload_cost

    def corrected_load_left(self):
        if self.load_left is not None:
            return self.load_left
        return self.corrected_load()

    def sortvalue(self, rtype=None):
        if rtype == 'priority':
            return ['minor', 'normal', 'important'].index(self.priority)
        return super(Ticket, self).sortvalue(rtype)

    def subject_done_in_vocabulary(self, rtype, limit=None):
        if not self.has_eid():
            peids = self.linked_to('concerns', 'subject')
            if peids:
                rset = self.req.execute(
                    'Any V, VN, P WHERE V version_of P, P eid %(p)s, V num VN, '
                    'V in_state ST, NOT ST name "published"', {'p': peids[0]})
                return sorted((v.view('combobox'), v.eid) for
                              v in rset.entities())
            return []
        return self.subject_relation_vocabulary(rtype, limit)

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.done_in:
            return self.done_in[0].rest_path(), {}
        return self.project.rest_path(), {}

    # IPrevNext interface #######################################

    def previous_entity(self):
        rql = ('Any X,T ORDERBY X DESC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid < %(x)s')
        rset = self.req.execute(rql, {'p': self.project.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        rql = ('Any X,T ORDERBY X ASC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid > %(x)s')
        rset = self.req.execute(rql, {'p': self.project.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0, 0)
