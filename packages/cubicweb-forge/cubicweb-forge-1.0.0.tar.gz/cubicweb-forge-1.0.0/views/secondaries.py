"""forge specific secondary views

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import html_escape

from cubicweb.selectors import one_line_rset, implements
from cubicweb.schema import display_name
from cubicweb.view import EntityView
from cubicweb.common import tags
from cubicweb.common.uilib import cut
from cubicweb.web.views import baseviews
from cubicweb.web.views.iprogress import ProgressTableView


class ExtProjectSecondaryView(baseviews.OutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = implements('ExtProject')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(u'&nbsp;')
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))


class ProjectSecondaryView(baseviews.OutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = implements('Project')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))
        # no summary on ext project
        if getattr(entity, 'summary', None):
            self.w(u'&nbsp;')
            self.w(html_escape(entity.summary))


class ProjectTextView(baseviews.TextView):
    __select__ = implements('Project')

    def cell_call(self, row, col):
        """ text_view representation of a project """
        entity = self.entity(row, col)
        self.w(entity.name)
        if entity.state != 'active development':
            self.w(u' [%s]' % self.req._(entity.state))


class ActiveTicketsTableView(EntityView):
    id = 'projecttickets'
    __select__ = one_line_rset() & implements('Project')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        # optimization: prefetch project's to fill entity / relations cache
        entity.reverse_version_of
        rset = self.req.execute(entity.tickets_rql(limit=1))
        self.req.form['actualrql'] = entity.active_tickets_rql()
        self.wview('editable-initialtable', rset, 'null',
                   subvid='incontext', displayactions=1,
                   divid='tickets%s'%entity.eid,
                   displaycols=range(entity.tickets_rql_nb_displayed_cols))


class VersionTextView(baseviews.TextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(entity.num)
        if entity.in_state:
            self.w(u' [%s]' % self.req._(entity.state))


class VersionIncontextView(baseviews.InContextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.num, href=entity.absolute_url()))


class VersionOutOfContextView(baseviews.OutOfContextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        if entity.version_of:
            project = entity.version_of[0]
            self.w(tags.a(project.name, href=project.absolute_url()))
        self.w(u'&nbsp;-&nbsp;')
        self.w(u'<a href="%s">' % html_escape(entity.absolute_url()))
        self.wdata(entity.num)
        if entity.in_state:
            self.wdata(u' [%s]' % self.req._(entity.state))
        self.w(u'</a>')


class VersionProgressTableView(ProgressTableView):
    __select__ = implements('Version')

    title = _('version progression')

    columns = (_('project'), _('milestone'), _('state'), _('planned_start'),
               _('planned_delivery'),
               _('cost'), _('progress'),
               _('depends_on'), _('todo_by'))

    def build_depends_on_cell(self, entity):
        vrset = entity.depends_on_rset()
        if vrset: # may be None
            vid = len(vrset) > 1 and 'list' or 'outofcontext'
            return self.view(vid, vrset, 'null')
        return u''

    def build_planned_start_cell(self, entity):
        """``starting_date`` column cell renderer"""
        if entity.starting_date:
            return self.format_date(entity.starting_date)
        return u''
    
    def header_for_cost(self, ecls):
        """``cost`` column cell renderer"""
        return self.req._('load')

    def build_planned_delivery_cell(self, entity):
        """``initial_prevision_date`` column cell renderer"""
        if entity.finished():
            return self.format_date(entity.completion_date())
        return self.format_date(entity.initial_prevision_date())
    

    
class TicketOneLineView(baseviews.OneLineView):
    """one representation of a story / bug:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    __select__ = implements('Ticket')
    
    def cell_call(self, row, col):
        self.wview('incontext', self.rset, row=row)
        entity = self.entity(row, col)
        if entity.in_state:
            self.w(u'&nbsp;[%s]' % html_escape(self.req._(entity.state)))


class TicketInContextView(baseviews.OneLineView):
    """one representation of a story / bug:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    id = 'incontext'
    __select__ = implements('Ticket')
    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.dc_title(), href=entity.absolute_url(), 
                      title=cut(entity.dc_description(), 80),
                      klass=entity.priority))



class TestInstanceOneLineView(baseviews.OneLineView):
    """text representation of a test instance:

    display title and state
    """
    __select__ = implements('TestInstance')
    def cell_call(self, row, col):
        super(TestInstanceOneLineView, self).cell_call(row, col)
        entity = self.entity(row, col)
        self.wdata(u' [%s]' % self.req._(entity.state))

