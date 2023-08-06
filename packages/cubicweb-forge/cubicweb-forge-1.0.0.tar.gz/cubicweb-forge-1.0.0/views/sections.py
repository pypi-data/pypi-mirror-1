"""forge components sections

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import html_escape

from cubicweb import role
from cubicweb.selectors import (one_line_rset, rql_condition, implements,
                                has_related_entities)
from cubicweb.view import EntityView
from cubicweb.common.uilib import rql_for_eid
from cubicweb.web.component import (Component, EntityVComponent,
                                    RelatedObjectsVComponent)
from cubicweb.web.views import primary, tabs


# project related sections and views ##########################################

class ProjectDocumentationView(tabs.EntityRelationView):
    """display project's documentation"""
    id = title = _('projectdocumentation')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'documented_by'
    target = 'object'

class DocumentationScreenshotTab(ProjectDocumentationView):
    id = 'documentation_tab'
    title = None # should not appears in possible views
    __select__ = ProjectDocumentationView.__select__ & one_line_rset()

class ProjectScreenshotsView(tabs.EntityRelationView):
    """display project's screenshots"""
    id = title = _('projectscreenshots')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'screenshot'
    target = 'object'
    vid = 'gallery'

class ProjectScreenshotTab(ProjectScreenshotsView):
    id = 'screenshots_tab'
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    title = None # should not appears in possible views

class ProjectTestCardsView(tabs.EntityRelationView):
    """display project's test cards"""
    id = title = _('projecttests')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'test_case_of'
    target = 'subject'

class TestcardsTab(ProjectTestCardsView):
    id = 'testcards_tab'
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    title = None # should not appears in possible views


class ProjectMainTab(primary.PrimaryView):
    __select__ = one_line_rset() & implements('Project')
    id = 'projectinfo'
    title = None # should not appears in possible views
    attribute_relations = [('mailinglist_of', 'object'),
                           ('license_of', 'object'),
                           ('uses', 'subject'), ('recommends', 'subject'),
                           ('uses', 'object'), ('recommends', 'object')]

    def is_primary(self):
        return True

    def render_entity_title(self, entity):
        pass

    def render_entity_attributes(self, entity):
        self.w(u'<div class="entityDescr">')
        if entity.description:
            entity.view('reledit', rtype='description', w=self.w)
            self.w(u'<br/>')
        #limit = self.req.property_value('navigation.related-limit') + 1
        for rtype, role in self.attribute_relations:
            rset = entity.related(rtype, role)
            if rset:
                value = self.view('csv', rset)
                self.field(display_name(self.req, rtype, role), value,
                           show_label=True, w=self.w, tr=False)
        self.w(u'</div>')

    def render_entity_relations(self, entity):
        pass

class ProjectRoadmapVComponent(EntityVComponent):
    """display the latest published version and in preparation version"""
    id = 'roadmap'
    __select__ = (EntityVComponent.__select__ & implements('Project')
                  & has_related_entities('version_of', 'object'))
    context = 'navcontenttop'
    title = _('Version_plural')
    order = 10

    def cell_call(self, row, col, view=None):
        self.w(u'<div class="section">')
        self.w(u'<h3>%s</h3>\n' % self.req._(self.title).capitalize())
        entity = self.rset.get_entity(row, col)
        currentversion = entity.latest_version()
        if currentversion:
            self.w(self.req._('latest published version:'))
            self.w(u'&nbsp;')
            currentversion.view('incontext', w=self.w)
            self.w(u'<br/>')
        rql = ('Any V,DATE ORDERBY version_sort_value(N) '
               'WHERE V num N, V prevision_date DATE, V version_of X, '
               'V in_state S, S name IN ("planned", "dev", "ready"), '
               'X eid %(x)s')
        rset = self.req.execute(rql, {'x': entity.eid}, 'x')
        if rset:
            self.wview('ic_progress_table_view', rset)
        allversionsrql = entity.related_rql('version_of', 'object') % {'x': entity.eid}
        self.w('<a href="%s">%s</a>'
               % (html_escape(self.build_url(vid='list', rql=allversionsrql)),
                  self.req._('view all versions')))
        self.w(u'</div>')


class ProjectBrowseTab(EntityView):
    id = 'codebrowser'
    __select__ = implements('Project') & rql_condition('NOT X vcsurl NULL')
    title = _('source')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        # XXX browse sub-tab
        # XXX may not be an hg repo
        w = self.w
        _ = self.req._
        w(u'<h4>%s</h4>' % _('Browse source'))
        rql = rql_for_eid(entity.eid)
        url = self.build_url('embed', rql=rql,  url=entity.vcsurl)
        w(u'<p>%s</p>' % _('You can browse the source code by following <a href="%s">this link</a>.')
          % html_escape(url))
        w(u'<h4>%s</h4>' % _('Command-Line Access'))
        w(u'<p>%s</p>' % _('Use this command to check out the latest project source code:'))
        w(u'<br/><pre>')
        w(u'# %s' % _('Non-members may check out a read-only working copy anonymously over HTTP.'))
        w(u'<br/>')
        w(u'hg clone %s' % html_escape(entity.vcsurl))
        w(u'</pre>')



class NotificationVComponent(Component):
    """section to control email notification for a project"""
    __registry__ = 'components'
    id = 'notification'
    __select__ = Component.__select__ & implements('Project')
    context = 'header'
    htmlclass = 'mainRelated'

    def call(self):
        user = self.req.user
        # skip this for anonymous user
        if self.vreg.config['anonymous-user'] == user.login:
            return
        _ = self.req._
        eid = self.rset[0][0]
        rset = self.req.execute('Any X WHERE U interested_in X, U eid %(u)s, X eid %(x)s',
                                {'u': user.eid, 'x': eid}, 'x')
        self.w(u'<div class="%s" id="%s">' % (self.id, self.div_id()))
        if not rset.rowcount:
            # user isn't registered
            rql = 'SET U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = _('click here to be notified about changes for this project')
            imgurl = self.req.external_resource('NOMAIL_ICON')
            msg = _('you are now registered for this project')
        else:
            # user is registered
            rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = _('click here if you don\'t want to be notified anymore for this project')
            imgurl = self.req.external_resource('MAIL_ICON')
            msg = _('you are not anymore registered for this project')
        url = self.user_rql_callback((rql, {'u': self.req.user.eid, 'x': eid}, 'x'),
                                     msg=msg)
        self.w(u'<a href="%s" title="%s"><img src="%s" alt="%s"/></a>' % (
            url, title, imgurl, title))
        self.w(u'</div>')
        self.w(u'<div class="clear"></div>')


# version sections ############################################################

class VersionBurndownChartVComponent(EntityVComponent):
    id = 'versionburndown'
    __select__ = EntityVComponent.__select__ & implements('Version')

    def version_tickets_rql(self, versioneid):
        # put in a method to ease overriding by jplextra
        rql = 'Any X,CD,L,LL where X load L, X load_left LL, X creation_date CD, X done_in V, V eid %s'
        return rql % versioneid

    def cell_call(self, row, col, view=None):
        version = self.rset.entities().next()
#         if version.finished() or version.in_progress():
#             end_date = version.stop_date()
#             if end_date:
#                 params["end"] = end_date.strftime('%Y%m%d')
#             start_date = version.start_date()
#             if start_date:
#                 params['start'] = start_date.strftime('%Y%m%d')
#         url = self.build_url(**params)
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
        tickets_rset = self.req.execute(self.version_tickets_rql(self.rset[row][col]))
        if tickets_rset:
            self.wview('burndown_chart', tickets_rset, width=800, height=500)


class VersionInfoVComponent(EntityVComponent):
    """display version information table in the context of the project"""
    id = 'versioninfo'
    __select__ = EntityVComponent.__select__ & implements('Version')
    context = 'navcontenttop'
    order = 10

    def cell_call(self, row, col, view=None):
        self.w(u'<div class="section">')
        version = self.entity(row, col)
        view = self.vreg.select_view('progress_table_view', self.req, version.as_rset())
        columns = list(view.columns)
        for col in ('project', 'milestone'):
            try:
                columns.remove(col)
            except ValueError:
                self.warning('could not remove %s from columns' % col)
        view.render(w=self.w, columns=columns)
        self.w(u'</div>')


class VersionTestCardBarVComponent(RelatedObjectsVComponent):
    """display version's test instances of test card"""
    id = 'versiontests'
    __select__ = RelatedObjectsVComponent.__select__ & implements('Version')

    rtype = 'for_version'
    target = 'subject'

    title = _('Test case instances')
    context = 'navcontentbottom'
    vid = 'table'

    def rql(self):
        return 'Any X,S WHERE X for_version E, E eid %(x)s, X in_state S'


# ticket sections #############################################################

class TicketIdenticalToVComponent(RelatedObjectsVComponent):
    """display identical tickets"""
    id = 'tickectidentical'
    __select__ = RelatedObjectsVComponent.__select__ & implements('Ticket')

    rtype = 'identical_to'
    target = 'object'

    title = _('Identical tickets')
    context = 'navcontentbottom'
    order = 20


class TicketTestCardVComponent(RelatedObjectsVComponent):
    """display project's test cards"""
    id = 'tickettests'
    __select__ = RelatedObjectsVComponent.__select__ & implements('Ticket')

    rtype = 'test_case_for'
    target = 'subject'

    title = _('Test cards')
    context = 'navcontentbottom'
    order = 30


class TicketScreenshotsView(tabs.EntityRelationView):
    """display ticket's screenshots """
    id = 'ticketscreenshots'
    __select__ = one_line_rset() & tabs.EntityRelationView.__select__ & implements('Ticket')

    rtype = 'attachment'
    target = 'object'

    title = _('Attached Documents')
    vid = 'gallery'

