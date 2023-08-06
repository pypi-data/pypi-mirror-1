"""forge specific ui actions

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import html_escape

from cubicweb.common.uilib import rql_for_eid
from cubicweb.selectors import (objectify_selector, match_search_state,
                                one_line_rset, two_lines_rset, implements,
                                rql_condition)
from cubicweb.web.action import LinkToEntityAction, Action


class ProjectVersionExportAction(Action):
    id = 'pvrestexport'
    __select__ = (match_search_state('normal') & one_line_rset() &
                  implements('Project', 'Version'))

    title = _('ReST export')
    order = 410

    def url(self):
        entity = self.rset.get_entity(0, 0)
        return entity.absolute_url(vid='document')

# Project actions #############################################################

class ProjectTestReportsAction(Action):
    id = 'testreports'
    __select__ = implements('Project') & rql_condition('NOT X reporturl NULL')

    title = _('test reports')
    order = 220
    def url(self):
        entity = self.rset.get_entity(0, 0)
        rql = rql_for_eid(entity.eid)
        return self.build_url('embed', rql=rql, url=entity.reporturl,
                              vtitle=self.req._(self.title))

# add related box actions

class ProjectAddRelatedAction(LinkToEntityAction):
    __select__ = (LinkToEntityAction.__select__ & implements('Project')
                  & rql_condition('X in_state S, NOT S name "moved"'))


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


# Version actions #############################################################

class DownloadVersionAction(Action):
    id = 'download'
    __select__ = (implements('Version')
                  & rql_condition('X version_of P, NOT P downloadurl NULL, '
                                  'X in_state S, S name "published"'))
    category = 'mainactions'
    title = _('download')
    order = 100

    def url(self):
        return self.rset.get_entity(0, 0).download_url()

@objectify_selector
def version_has_next_version(cls, req, rset, row=None, col=0, **kwargs):
    if rset.description[row or 0][col or 0] != 'Version':
        return 0
    version = rset.get_entity(row or 0, col or 0)
    if not cls.schema.rschema('done_in').has_perm(req, 'add', toeid=version.eid):
        return 0
    try:
        version.open_tickets().next()
    except StopIteration:
        return 0
    return bool(version.next_version())


class MoveToNextVersionAction(Action):
    id = 'movetonext'
    __select__ = (one_line_rset() & match_search_state('normal')
                  & implements('Version') & version_has_next_version)
    _title = _('move open tickets to %s')
    order = 101

    @property
    def title(self):
        version = self.rset.get_entity(0, 0).next_version()
        return self.req._(self._title) % version.num

    def url(self):
        return self.rset.get_entity(0, 0).absolute_url(__method='move_open_to_next_version')

# add related actions

class VersionAddTicketAction(LinkToEntityAction):
    id = 'addticket'
    __select__ = (LinkToEntityAction.__select__ & implements('Version')
                  & rql_condition('X in_state S, S name IN ("planned", "dev")'))
    title = _('add Ticket done_in Version object')
    etype = 'Ticket'
    rtype = 'done_in'
    target = 'subject'

    def url(self):
        baseurl = super(VersionAddTicketAction, self).url()
        entity = self.rset.get_entity(0, 0)
        linkto = 'concerns:%s:%s' % (entity.version_of[0].eid, self.target)
        return '%s&__linkto=%s' % (baseurl, self.req.url_quote(linkto))

class VersionSubmitBugAction(VersionAddTicketAction):
    id = 'submitbug'
    __select__ = (LinkToEntityAction.__select__ & implements('Version')
                  & rql_condition('X in_state S, S name "published"'))
    title = _('add Ticket appeared_in Version object')
    rtype = 'appeared_in'
    category = 'mainactions'


# Ticket actions ##############################################################

class TicketAction(Action):
    __select__ = match_search_state('normal') & implements('Ticket')
    category = 'mainactions'

@objectify_selector
def ticket_has_next_version(cls, req, rset, row=None, col=0, **kwargs):
    rschema = cls.schema.rschema('done_in')
    if row is None:
        # action is applyable if all entities are from the same project,
        # in an open state and share all the same "next version"
        project, version = None, None
        for entity in rset.entities():
            if entity.e_schema != 'Ticket':
                return 0
            if not entity.is_open():
                return 0
            if project is None:
                project = entity.project
            elif project.eid != entity.project.eid:
                return 0
            if version is None:
                version = entity.next_version()
                if version is None:
                    return 0
            elif version.eid != getattr(entity.next_version(), 'eid', None):
                return 0
            if not rschema.has_perm(req, 'add', toeid=version.eid):
                return 0
        return 1
    entity = rset.get_entity(row, 0)
    version = entity.next_version()
    if version is None:
        return 0
    elif not rschema.has_perm(req, 'add', fromeid=entity.eid, toeid=version.eid):
        return 0
    return 1


class TicketMoveToNextVersionAction(TicketAction):
    id = 'movetonext'
    _title = _('move to version %s')
    __select__ = TicketAction.__select__ & ticket_has_next_version

    @property
    def title(self):
        entity = self.rset.get_entity(self.row or 0, self.col or 0)
        version = entity.next_version()
        return self.req._(self._title) % html_escape(version.num)

    def url(self):
        if self.row is None:
            entity = self.rset.get_entity(0, 0) # sample entity
            eids = [str(row[0]) for row in self.rset]
        else:
            entity = self.rset.get_entity(self.row, self.col or 0)
            eids = [str(entity.eid)]
        nextversion = entity.next_version()
        rql = 'SET X done_in V WHERE X eid IN(%s), V eid %%(v)s' % ','.join(eids)
        msg = self.req._('tickets moved to version %s') % nextversion.num
        return self.user_rql_callback((rql, {'v': nextversion.eid}, 'v'), msg)


class TicketCSVExportAction(TicketAction):
    id = 'ticketcsvexport'
    __select__ = two_lines_rset() & TicketAction.__select__
    title = _('csv export')

    def url(self):
        return self.build_url('view', rql=self.rset.printable_rql(),
                              vid='csvexport')

class TicketRESTExportAction(TicketAction):
    id = 'ticketrestexport'
    __select__ = two_lines_rset() & TicketAction.__select__
    title = _('ReST export')

    def url(self):
        return self.build_url('view', rql=self.rset.printable_rql(),
                              vid='document')


# TestInstance actions ########################################################

class TestInstanceGenerateBugAction(LinkToEntityAction):
    id = 'submitbug'
    __select__ = match_search_state('normal') & implements('TestInstance')
    title = _('add TestInstance generate_bug Ticket subject')
    etype = 'Ticket'
    rtype = 'generate_bug'
    target = 'object'
    def url(self):
        entity = self.rset.get_entity(0, 0)
        linkto = '__linkto=concerns:%s:%s' % (entity.instance_of[0].test_case_of[0].eid, self.target)
        linkto += '&__linkto=generate_bug:%s:subject' % entity.eid
        linkto += '&__linkto=appeared_in:%s:%s' % (entity.for_version[0].eid, self.target)
        return '%s&%s' % (LinkToEntityAction.url(self), linkto)

# XXX bw compat
from logilab.common.deprecation import class_moved
class ProjectAction(Action):
    __select__ = implements('Project')
ProjectAction = class_moved(ProjectAction, message='use Action and appropriate selector')
