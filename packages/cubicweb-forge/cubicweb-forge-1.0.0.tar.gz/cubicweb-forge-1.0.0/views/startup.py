"""forge specific startup views

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from logilab.common import table as _table
from logilab.mtconverter import html_escape

from cubicweb.view import EntityStartupView, StartupView
from cubicweb.selectors import none_rset, implements
from cubicweb.web.views import schema, startup

class IndexView(startup.ManageView):
    id = 'index'
    title = _('Index')
    add_etype_links = ('Project',)

    def call(self):
        _ = self.req._
        user = self.req.user
        self.whead(u'<link  rel="meta" type="application/rdf+xml" title="FOAF" '
                   u'href="%s"/>' % self.build_url('foaf.rdf'))
        stitle = self.req.property_value('ui.site-title')
        if stitle:
            self.w(u'<h1>%s</h1>' % self.req.property_value('ui.site-title'))
        self.w(u'<table width="100%"><tr>\n')
        self.w(u'<td style="width: 50%;">')
        if not user.matching_groups(('managers', 'staff', 'users')):
            self.w(u'<div>')
            self._main_index()
            self.w(u'</div>')
        else:
            self.w(u'<div class="quickLinks">')
            self.w(u'<ul class="createLink">')
            for etype in self.add_etype_links:
                eschema = self.schema.eschema(etype)
                if eschema.has_perm(self.req, 'add'):
                    self.w(u'<li><a href="%s">%s</a></li>' % (
                           self.req.build_url('add/%s' % eschema),
                           self.req.__('add a %s' % eschema).capitalize()))
            self.w(u'</ul>')
            self.w(u'<div class="hr">&nbsp;</div>')
            self.w(u'<h5>%s</h5>' % _('Projects I\'m interested in'))
            self.w(u'<div>')
            self.w(u'<table width="100%"><tr><td>')
            projects = [proj for proj in user.interested_in
                        if ((proj.id == 'Project' and proj.state == 'active development') or proj.id == 'Blog')]
            if len(projects) > 50:
                chcol = len(projects) // 2
            else:
                chcol = None # all projects in one column
            for i, project in enumerate(projects):
                self.w(u'%s<br/>' % project.view('incontext'))
                if i == chcol:
                    self.w(u'</td><td>')
            self.w(u'</td></tr></table>')
            self.w(u'<p><a href="%s">%s</a></p>' % (self.req.build_url('project'),
                                                    self.req._('view all active projects')))
            self.w(u'</div>')
            self.w(u'</div>')
        if not user.matching_groups(('managers', 'staff', 'users')):
            self.w(u'<div>')
            self.folders()
            self.w(u'</div>')
        self.w(u'</td><td style="width: 50%;">')
        # projects the user is subscribed to
        if user.is_in_group('users'):
            rql = 'Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE U interested_in P, U eid %(x)s, X concerns P, X creation_date CD'
            rset = self.req.execute(rql, {'x': user.eid})
            self.wview('table', rset, 'null',
                       headers=[_(u'Recent tickets in my projects'), _(u'Date'), _(u'Project')],
                       subvid='incontext', displayactions=False)


        # tickets
        if user.is_in_group('guests'):
            rql = 'Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE X concerns P, X creation_date CD'
            rset = self.req.execute(rql)
        else:
            rql = 'Any X, NOW - CD, P ORDERBY CD DESC LIMIT 5 WHERE X concerns P, X creation_date CD, NOT U interested_in P, U eid %(x)s'
            rset = self.req.execute(rql, {'x': user.eid})
        self.wview('table', rset, 'null',
                   headers=[_(u'Recent tickets'), _(u'Date'),_(u'Project')],
                   subvid='incontext', displayactions=False)
        # upcoming versions
        rql = 'Any X,D ORDERBY D DESC LIMIT 5 WHERE X is Version, X prevision_date D, NOT X prevision_date NULL, X in_state S, S name "dev"'
        rset = self.req.execute(rql)
        self.wview('table', rset, 'null',
                   headers=[_(u'Upcoming versions'), _(u'Planned on')],
                   subvid='outofcontext', displayactions=False)
        # latest releases
        rql = 'Any X,D ORDERBY D DESC LIMIT 5 WHERE X is Version, X publication_date D, NOT X publication_date NULL, X in_state S, S name "published"'
        rset = self.req.execute(rql)
        self.wview('table', rset, 'null',
                   headers=[_(u'Latest releases'), _(u'Published on')],
                   subvid='outofcontext', displayactions=False)
        # new projects
        rql = 'Any P,S ORDERBY CD DESC LIMIT 5 WHERE P is Project, P summary S, P creation_date CD'
        rset = self.req.execute(rql)
        self.wview('table', rset, 'null',
                   headers=[_(u'New projects'), _(u'Description')],
                   subvid='oneline', displayactions=False)
        self.w(u'</td>')
        self.w(u'</tr></table>\n')


schema.SchemaImageView.skip_rels += ('see_also',)


class ProjectStatsView(EntityStartupView):
    """Some statistics : how many bugs, sorted by status, indexed by projects
    """
    id = 'stats'
    __select__ = none_rset() | implements('Project')
    title = _('projects statistics')
    default_rql = 'Any P,PN WHERE P name PN, P in_state S, S name "active development"'

    def call(self, sort_col=None):
        req = self.req
        if self.rset is None:
            self.rset = req.execute(self.default_rql)
        table = _table.Table()
        statuslist = [row[0] for row in self.req.execute('DISTINCT Any N WHERE S name N, S state_of E, E name "Ticket"')]
        severities = ['minor', 'normal', 'important']
        table.create_columns(statuslist + severities + ['Total'])
        nb_cols = len(table.col_names)
        # create a stylesheet to compute sums over rows and cols
        stylesheet = _table.TableStyleSheet()
        # fill table
        i = -1
        for row in self.rset:
            i += 1
            eid = row[0]
            row = []
            total = 0
            for status in statuslist:
                rql = "Any COUNT(A) WHERE A is Ticket, A concerns P, A in_state S, S name %(s)s, P eid %(x)s"
                nbtickets = req.execute(rql, {'x': eid, 's': status}, 'x', build_descr=0)[0][0]
                total += nbtickets
                row.append(nbtickets)
            for severity in severities:
                rql = "Any COUNT(A) WHERE A is Ticket, A concerns P, A priority %(p)s, P eid %(x)s"
                nbtickets = req.execute(rql, {'x': eid, 'p': severity}, 'x', build_descr=0)[0][0]
                total += nbtickets
                row.append(nbtickets)
            row.append(total)
            table.append_row(row, html_escape(self.entity(i).name))
            assert len(row) == nb_cols
        # sort table according to sort_col if wanted
        sort_col = sort_col or self.req.form.get('sort_col', '')
        if sort_col:
            table.sort_by_column_id(sort_col, method='desc')
        else:
            table.sort_by_column_index(0)
        # append a row to compute sums over rows and add appropriate
        # stylesheet rules for that
        if len(self.rset) > 1:
            table.append_row([0] * nb_cols, 'Total')
            nb_rows = len(table.row_names)
            for i in range(nb_cols):
                stylesheet.add_colsum_rule((nb_rows-1, i), i, 0, nb_rows-2)
            table.apply_stylesheet(stylesheet)
        # render the table
        self.w(u'<table class="stats" cellpadding="5">')
        self.w(u'<tr>')
        col_template = ''
        for col in [''] + table.col_names:
            url = self.build_url(vid='stats', sort_col=col,
                                 __force_display=1,
                                 rql=self.rset.printable_rql())
            self.w(u'<th><a href="%s">%s</a></th>\n' % (html_escape(url), col))
        self.w(u'</tr>')
        for row_name, row, index in zip(table.row_names, table.data,
                                        xrange(len(table.data))):
            if index % 2 == 0:
                self.w(u'<tr class="alt0">')
            else:
                self.w(u'<tr class="alt1">')
            if index == len(table.data) - 1:
                self.w(u'<td>%s</td>' % row_name)
            else:
                url = self.build_url('project/%s' % self.req.url_quote(row_name))
                self.w(u'<td><a href="%s">%s</a></td>' % (html_escape(url), row_name))
            for cell_data in row:
                self.w(u'<td>%s</td>' % cell_data)
            self.w(u'</tr>')
        self.w(u'</table>')


class VersionsInfoView(StartupView):
    """display versions in state ready or development, or marked as prioritary.
    """
    id = 'versionsinfo'
    title = _('All current versions')

    def call(self, sort_col=None):
        rql = ('Any X,P,N,PN ORDERBY PN, version_sort_value(N) '
               'WHERE X num N, X version_of P, P name PN, '
               'EXISTS(X in_state S, S name IN ("dev", "ready")) '
               'OR EXISTS(T tags X, T name IN ("priority", "prioritaire"))')
        rset = self.req.execute(rql)
        self.wview('progress_table_view', rset, 'noresult')
        url = self.build_url(rql='Any P,X ORDERBY PN, version_sort_value(N) '
                             'WHERE X num N, X version_of P, P name PN')
        self.w(u'<a href="%s">%s</a>\n'
               % (html_escape(url), self.req._('view all versions')))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      butclasses=(IndexView,))
    vreg.register_and_replace(IndexView, startup.IndexView)
