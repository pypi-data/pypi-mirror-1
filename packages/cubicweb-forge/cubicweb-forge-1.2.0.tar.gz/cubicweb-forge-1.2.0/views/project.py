"""views for Project entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import one_line_rset, score_entity, implements
from cubicweb.view import EntityView
from cubicweb.common import tags, uilib
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, tabs, baseviews

from cubes.tracker.views import project as tracker

tracker.ProjectStatsView.default_rql = (
    'Any P, PN WHERE P is Project, P name PN, '
    'P in_state S, S name "active development"')

# primary view and tabs ########################################################

class ExtProjectPrimaryView(primary.PrimaryView):
    __select__ = implements('ExtProject')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (xml_escape(entity.homepage),
                                          xml_escape(entity.name))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class ProjectPrimaryView(tracker.ProjectPrimaryView):
    tabs = tracker.ProjectPrimaryView.tabs + [
        _('documentation_tab'), _('screenshots_tab'),
        _('testcards_tab'), _('codebrowser_tab')]

    def render_entity_title(self, entity):
        self.w(u'<div class="projectTitleGroup">%s %s <span class="state">(%s)</span></div>' % (
            entity.dc_type().capitalize(),
            entity.view('reledit', rtype='name', role='subject'),
            xml_escape(self.req._(entity.state))))
        nc = self.vreg['components'].select_object('notification', self.req,
                                                   rset=self.rset)
        if nc:
            nc.render(w=self.w)
        self.w(u'<br/>')


tracker.ProjectInfoTab.attribute_relations = [('summary', 'subject'),
                                              ('description', 'subject'),
                                              ('mailinglist_of', 'object'),
                                              ('license_of', 'object'),
                                              ('uses', 'subject'), ('recommends', 'subject'),
                                              ('uses', 'object'), ('recommends', 'object')]

# XXX cleanup or explain View/Tab duality

class ProjectDocumentationView(tabs.EntityRelationView):
    """display project's documentation"""
    id = title = _('projectdocumentation')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'documented_by'
    target = 'object'

class ProjectDocumentationTab(ProjectDocumentationView):
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

class ProjectScreenshotsTab(ProjectScreenshotsView):
    id = 'screenshots_tab'
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    title = None # should not appears in possible views


class ProjectTestCardsView(tabs.EntityRelationView):
    """display project's test cards"""
    id = title = _('projecttests')
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    rtype = 'test_case_of'
    target = 'subject'

class ProjectTestCardsTab(ProjectTestCardsView):
    id = 'testcards_tab'
    __select__ = tabs.EntityRelationView.__select__ & implements('Project')
    title = None # should not appears in possible views


class ProjectBrowseTab(EntityView):
    id = 'codebrowser_tab'
    __select__ = implements('Project') & score_entity(lambda x: x.vcsurl)
    title = None # should not appears in possible views

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        # XXX browse sub-tab
        # XXX may not be an hg repo
        w = self.w
        _ = self.req._
        w(u'<h4>%s</h4>' % _('Browse source'))
        rql = uilib.rql_for_eid(entity.eid)
        url = self.build_url('embed', rql=rql,  url=entity.vcsurl)
        w(u'<p>%s</p>' % _('You can browse the source code by following <a href="%s">this link</a>.')
          % xml_escape(url))
        w(u'<h4>%s</h4>' % _('Command-Line Access'))
        w(u'<p>%s</p>' % _('Use this command to check out the latest project source code:'))
        w(u'<br/><pre>')
        w(u'# %s' % _('Non-members may check out a read-only working copy anonymously over HTTP.'))
        w(u'<br/>')
        w(u'hg clone %s' % xml_escape(entity.vcsurl))
        w(u'</pre>')


# secondary views ##############################################################

class ExtProjectOutOfContextView(baseviews.OutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = implements('ExtProject')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        self.w(u'&nbsp;')
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))


class ProjectTextView(baseviews.TextView):
    __select__ = implements('Project')

    def cell_call(self, row, col):
        """ text_view representation of a project """
        entity = self.entity(row, col)
        self.w(entity.name)
        if entity.state != 'active development':
            self.w(u' [%s]' % self.req._(entity.state))


class ProjectOutOfContextView(tracker.ProjectOutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = implements('Project')

    def cell_call(self, row, col):
        entity = self.rset.get_entity(row, col)
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))
        # no summary on ext project
        if getattr(entity, 'summary', None):
            self.w(u'&nbsp;')
            self.w(xml_escape(entity.summary))


# Project actions #############################################################

class ProjectTestReportsAction(action.Action):
    id = 'testreports'
    __select__ = implements('Project') & score_entity(lambda x: x.reporturl)

    title = _('test reports')
    order = 220
    def url(self):
        entity = self.rset.get_entity(0, 0)
        rql = uilib.rql_for_eid(entity.eid)
        return self.build_url('embed', rql=rql, url=entity.reporturl,
                              vtitle=self.req._(self.title))

class ProjectAddRelatedAction(action.LinkToEntityAction):
    __select__ = (action.LinkToEntityAction.__select__ & implements('Project')
                  & score_entity(lambda x: x.state != 'moved'))

class ProjectAddDocumentationCard(ProjectAddRelatedAction):
    id = 'adddocumentationcard'
    etype = 'Card'
    rtype = 'documented_by'
    target = 'object'
    title = _('add Project documented_by Card subject')
    order = 120

class ProjectAddDocumentationFile(ProjectAddRelatedAction):
    id = 'adddocumentationfile'
    etype = 'File'
    rtype = 'documented_by'
    target = 'object'
    title = _('add Project documented_by File subject')
    order = 121

class ProjectAddScreenshot(ProjectAddRelatedAction):
    id = 'addscreenshot'
    etype = 'Image'
    rtype = 'screenshot'
    target = 'object'
    title = _('add Project screenshot Image subject')
    order = 122

class ProjectAddTestCard(ProjectAddRelatedAction):
    id = 'addtestcard'
    etype = 'Card'
    rtype = 'test_case_of'
    target = 'subject'
    title = _('add Card test_case_of Project object')
    order = 123

class ProjectAddTicket(ProjectAddRelatedAction):
    id = 'addticket'
    etype = 'Ticket'
    rtype = 'concerns'
    target = 'subject'
    title = _('add Ticket concerns Project object')
    order = 110

class ProjectAddVersion(ProjectAddRelatedAction):
    id = 'addversion'
    etype = 'Version'
    rtype = 'version_of'
    target = 'subject'
    title = _('add Version concerns Project object')
    order = 112

_abaa = uicfg.actionbox_appearsin_addmenu
for cls in ProjectAddRelatedAction.__subclasses__():
    if cls.target == 'subject':
        _abaa.tag_object_of(('*', cls.rtype, 'Project'), False)
    else:
        _abaa.tag_subject_of(('Project', cls.rtype, '*'), False)
# del cls local identifier else ProjectAddVersion is referenced twice and it
# triggers a registration error
del cls

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (ProjectPrimaryView, ProjectOutOfContextView))
    vreg.register_and_replace(ProjectPrimaryView, tracker.ProjectPrimaryView)
    vreg.register_and_replace(ProjectOutOfContextView, tracker.ProjectOutOfContextView)
