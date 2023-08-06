"""forge specific primary views

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import html_escape

from cubicweb.selectors import implements
from cubicweb.web.views import baseviews, tabs
from cubicweb.web.views.primary import PrimaryView

from cubes.forge.entities.ticket import Ticket


class ProjectPrimaryView(tabs.TabsMixin, baseviews.PrimaryView):
    __select__ = implements('Project')
    tabs = [_('projectinfo'), _('projecttickets'),
            _('documentation_tab'), _('screenshots_tab'),
            _('testcards_tab'), _('codebrowser')]
    default_tab = 'projectinfo'

    def render_entity_title(self, entity):
        self.w(u'<h1>%s %s <span class="state">(%s)</span></h1>' % (
            entity.dc_type().capitalize(), html_escape(entity.name),
            html_escape(self.req._(entity.state))))
        nc = self.vreg.select_component('notification', self.req, self.rset)
        if nc:
             nc.render(w=self.w)
        self.w(u'<div class="summary">%s</div>' % entity.view('reledit', rtype='summary'))
        self.w(u'<br/>')

    def render_entity(self, entity):
        # we have to include formfilter here since tickets table will be
        # included by ajax
        self.req.add_js( ('cubicweb.ajax.js', 'cubicweb.formfilter.js',
                          'cubes.file.js', 'jquery.tablesorter.js') )
        self.req.add_css(('cubicweb.iprogress.css','cubicweb.tablesorter.css', 'cubicweb.tableview.css', 'cubicweb.facets.css'))
        self.render_entity_title(entity)
        self.render_tabs(self.tabs, self.default_tab, entity)


class VersionPrimaryView(baseviews.PrimaryView):
    __select__ = implements('Version')

    def render_entity_title(self, entity):
        self.w(u'<div class="titleGroup">')
        self.w(u'<h2 class="%s">' % entity.progress_class())
        if entity.version_of:
            project_name = entity.version_of[0].name
        else:
            project_name = ''
        self.wdata('%s %s %s %s' % (entity.dc_type().capitalize(),
                                    project_name, entity.num,
                                    self.req._(entity.state)))
        self.w(u'</h2>\n')
        self.w(u'</div>')

    def render_entity_metadata(self, entity):
        entity.view('metadata', w=self.w)
        if entity.project.summary:
            self.w(u'<div class="entityDescr">%s</div>'
                   % entity.project.printable_value('summary'))

    def render_entity_attributes(self, entity):
        if entity.description:
            self.w(u'<div class="entityDescr"><b>%s</b> %s</div>' % (
                self.req._('focus for this release'),
                entity.view('reledit', rtype='description')))

    def render_entity_relations(self, entity):
        """ Main Block in primary view """
        req = self.req
        _ = req._
        req.add_js( ('cubicweb.ajax.js', 'jquery.tablesorter.js', 'cubicweb.formfilter.js') )
        pinfo = entity.progress_info()
        if pinfo['notestimated']:
            self.w(u'<div class="entityDescr">')
            msg = _('load of unestimated tickets is arbitrary set to %s m/d')
            self.w(u'<p>%s</p>' % (msg % Ticket.noload_cost))
            self.w(u'</div>')
        if entity.conflicts:
            self.w(u"<div class='entityDescr'><b>%s</b>:<ul>" % _('conflicting with'))
            vid = len(entity.conflicts) > 1 and 'list' or 'outofcontext'
            self.w(vid, entity.conflicts)
            self.w(u'</ul></div>')
        # Tickets in version
        params = req.build_url_params(displaycols=range(entity.tickets_rql_nb_displayed_cols),
                                      displayfilter=1, displayactions=1,
                                      divid='bugs', subvid='incontext',
                                      title=_('Ticket_plural'))
        hackedvid = html_escape('table&' + params)
        req.html_headers.define_var('LOADING_MSG', _('Loading'))
        self.w(u'<div class="dynamicFragment" id="buglist" cubicweb:vid="%s" cubicweb:fallbackvid="null" cubicweb:rql="%s"></div>'
               % (hackedvid, req.url_quote(entity.tickets_rql())))
        # Defects appeared in version
        params = req.build_url_params(displaycols=range(entity.defects_rql_nb_displayed_cols),
                                      displayfilter=1, displayactions=1,
                                      divid='defects', subvid='incontext',
                                      title=_('Defects_plural'))
        hackedvid = html_escape('table&' + params)
        self.w(u'<div class="dynamicFragment" id="defectslist" cubicweb:vid="%s" cubicweb:fallbackvid="null" cubicweb:rql="%s"></div>'
               % (hackedvid, req.url_quote(entity.defects_rql())))


class TicketPrimaryView(PrimaryView):
    """common primary view for bug and story, relying on a mixin class
    to be usable
    """
    __select__ = implements('Ticket')

    def render_entity_title(self, entity):
        self.w(u'<div class="titleGroup">')
        title = html_escape(entity.dc_title())
        self.w(u'<h2><span class="%s %s">%s</span><span class="state"> [%s]</span></h2>\n'
               % (entity.priority, entity.type, title,
                  html_escape(self.req._(entity.state))))
        self.w(u'</div>')

    ticket_attributes = ('priority', 'type', 'load', 'load_left')

    def render_entity_metadata(self, entity):
        entity.view('metadata', w=self.w)
        self.w(u'<table>')
        for attr in self.ticket_attributes:
            self.w(u'<tr class="row">')
            self.w(u'<td class="label">%s</td><td>' % display_name(self.req, attr))
            entity.view('reledit', rtype=attr, w=self.w)
            self.w(u'</td></tr>\n')
        self.w(u'</table>')

    def render_entity_attributes(self, entity):
        # Solved in
        if entity.in_version():
            entity.in_version().view('oneline', w=self.w)
        else:
            self.w(self.req._('not planned'))

    def render_entity_relations(self, entity):
        # description
        description = entity.view('reledit', rtype='description')
        if description:
            if not description.startswith('<p'):
                description = u'<div>%s</div>' % description
            self.w(description)


class ExtProjectPrimaryView(baseviews.PrimaryView):
    __select__ = implements('ExtProject')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (html_escape(entity.homepage),
                                          html_escape(entity.name))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class LicensePrimaryView(baseviews.PrimaryView):
    __select__ = implements('License')

    def render_entity_title(self, entity):
        if entity.url:
            title = u'<a href="%s">%s</a>' % (html_escape(entity.url),
                                              html_escape(entity.name))
        else:
            title = entity.name
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class TestInstancePrimaryView(baseviews.PrimaryView):
    __select__ = implements('TestInstance')

    def render_entity_title(self, entity):
        title = html_escape('%s [%s]' % (entity.name, self.req._(entity.state)))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_metadata(self, entity):
        pass

    def render_entity_attributes(self, entity):
        self.w(entity.instance_of[0].view('inlined'))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
