"""forge extproject and project entity classes

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached

from cubicweb.entities import AnyEntity, fetch_config

from cubes.forge.entities import fixed_orderby_rql

DEFAULT_STATE_RESTR = 'S name IN ("open","confirmed","waiting feedback","in-progress","validation pending")'

class ExtProject(AnyEntity):
    id = 'ExtProject'
    __permissions__ = ('developer', 'client')

    fetch_attrs, fetch_order = fetch_config(['name', 'description', 'description_format'])

    def dc_title(self, format='text/plain'):
        return self.name

class Project(ExtProject):
    id = 'Project'

    fetch_attrs = ('name', 'description', 'description_format', 'homepage', 'summary')

    def dc_long_title(self):
        if self.summary:
            return u'%s (%s)' % (self.name, self.summary)
        return self.name

    def add_related_schemas(self):
        # return empty list to avoid falling back on schema actions
        # if no explicit action could be selected
        return []

    @property
    def project(self):
        """project item interface"""
        return self

    @cached
    def latest_version(self, states=('published',), reverse=False):
        """return the latest version for the project in one of the given states

        when no states specified, return the latest published version

        NOTE: /!\ DO NOT CALL this method with named parameter: `cached` implementation
              doesn't support it yet
        """
        if reverse:
            order = 'ASC'
        else:
            order = 'DESC'
        rql = 'Any V,N ORDERBY version_sort_value(N) %s LIMIT 1 ' \
              'WHERE V num N, V in_state S, S name IN (%s), ' \
              'V version_of P, P eid %%(p)s' % (order, ','.join(repr(s) for s in states))
        rset = self.req.execute(rql, {'p': self.eid})
        if rset:
            return rset.get_entity(0, 0)
        return None

    # number of columns to display
    tickets_rql_nb_displayed_cols = 10
    sort_defs = (('in_state', 'S'), ('num', 'VN'), ('type', 'TT'),
                 ('priority', 'PR'))
    def tickets_rql(self, limit=None):
        rql = ('Any B,TT,NOW - CD, NOW - BMD, U,PR,S,C,V,group_concat(TN),BDF,BD,BC,VN,P,BT,CD,BMD,UL '
               'GROUPBY B,TT,CD,PR,S,C,V,U,VN,BDF,BD,BC,P,BT,BMD,UL %s WHERE '
               'B type TT, B priority PR, B in_state S, B creation_date CD, '
               'B description_format BDF, B description BD, B load_left BC, '
               'B title BT, B modification_date BMD, '
               'B load C, T? tags B, T name TN, B done_in V?, V num VN, '
               'B created_by U?, U login UL, B concerns P, P eid %s'
               ) % (fixed_orderby_rql(self.sort_defs), self.eid)
        if limit:
            rql += ' LIMIT ' + `limit`
        return rql

    def active_tickets_rql(self):
        return '%s, %s' % (self.tickets_rql(), DEFAULT_STATE_RESTR)
