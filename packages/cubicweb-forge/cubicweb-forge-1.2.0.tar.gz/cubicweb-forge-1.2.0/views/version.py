"""views for Project entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import implements
from cubicweb.web import component

from cubes.tracker.views import version as tracker


class VersionBurndownChartVComponent(component.EntityVComponent):
    id = 'versionburndown'
    __select__ = component.EntityVComponent.__select__ & implements('Version')
    rql = ('Any X,CD,L,LL where X load L, X load_left LL, '
           'X creation_date CD, X done_in V, V eid %s')

    def cell_call(self, row, col, view=None):
        version = self.rset.entities().next()
        alt = self.req._('Burn Down Chart')
        self.w('<h3>%s</h3>' % alt)
        # the following rql is useful to detect Ticket which is
        # created directly with a done state (validation pending,
        # resolved, deprecated or rejected). In this case, graph is
        # probably wrong.
        rset = self.req.execute("Any T GROUPBY T  WHERE T done_in V, V eid %s, "
                                "T in_state S, S name IN ('validation pending',"
                                "'resolved', 'deprecated', 'rejected'), "
                                "TR wf_info_for T HAVING COUNT(TR)=1"
                                % version.eid)
        if rset:
            self.w(u'<div class="needsvalidation">%s</div>'
                   % _(u"Some tickets don't have a regular workflow, "
                       "the graph may be wrong."))
        tickets_rset = self.req.execute(self.rql % self.rset[row][col])
        if tickets_rset:
            self.wview('burndown_chart', tickets_rset, width=800, height=500)


class VersionTestCardBarVComponent(component.RelatedObjectsVComponent):
    """display version's test instances of test card"""
    id = 'versiontests'
    __select__ = component.RelatedObjectsVComponent.__select__ & implements('Version')

    rtype = 'for_version'
    target = 'subject'

    title = _('Test case instances')
    context = 'navcontentbottom'
    vid = 'table'

    def rql(self):
        return 'Any X,S WHERE X for_version E, E eid %(x)s, X in_state S'


class VersionProgressTableView(tracker.VersionProgressTableView):
    columns = (_('project'), _('milestone'), _('state'), _('planned_start'),
               _('planned_delivery'),
               _('cost'), _('progress'),
               _('depends_on'), _('todo_by'))

    def header_for_cost(self, ecls):
        """``cost`` column cell renderer"""
        return self.req._('load')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (VersionProgressTableView,))
    vreg.register_and_replace(VersionProgressTableView,
                              tracker.VersionProgressTableView)
