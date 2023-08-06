"""forge web user interface

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.web import uicfg
from cubicweb.web.views.urlrewrite import (
    SimpleReqRewriter, SchemaBasedRewriter, rgx, build_rset)

class ForgeSimpleReqRewriter(SimpleReqRewriter):
    """handle path with the form::

    versions -> view versions in state ready or development, or marked as
                prioritary.

    foaf.rdf -> view the foaf file for all users
    """
    rules = [
        (rgx('/versions'), dict(vid='versionsinfo')),
        ('/foaf.rdf', dict(vid='foaf', rql='Any X WHERE X is CWUser'))
        ]

class ForgeURLRewriter(SchemaBasedRewriter):
    """handle path with the form::

        project/<name>/testcases         -> view project's test cases
        project/<name>/documentation     -> view project's documentation
        project/<name>/screenshots       -> view project's screenshots
        project/<name>/tickets           -> view project's tickets
        project/<name>/versions          -> view project's versions in state ready
                                            or development, or marked as
                                            prioritary.
        project/<name>/[version]         -> view version
        project/<name>/[version]/tests   -> test for this version
        project/<name>/[version]/tickets -> tickets for this version
    """
    rules = [
        (rgx('/project/([^/]+)/testcases'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projecttests')),
        (rgx('/project/([^/]+)/documentation'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectdocumentation')),
        (rgx('/project/([^/]+)/screenshots'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1)], vid='projectscreenshots')),
        (rgx('/project/([^/]+)/([^/]+)/tests'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)], vid='versiontests')),
        (rgx('/project/([^/]+)/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T done_in V, V version_of P, P name %(project)s, V num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)],
                    vtitle=_('tickets for %(project)s - %(num)s'))),
        (rgx('/project/([^/]+)/versions'),
         build_rset(rql='Any X,N ORDERBY version_sort_value(N) '
                    'WHERE X num N, X version_of P, P name %(project)s, '
                    'EXISTS(X in_state S, S name IN ("dev", "ready")) '
                    'OR EXISTS(T tags X, T name IN ("priority", "prioritaire"))',
                    rgxgroups=[('project', 1)], vid='ic_progress_table_view',
                    vtitle=_('upcoming versions for %(project)s'))),
        (rgx('/project/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T concerns P, P name %(project)s',
                    rgxgroups=[('project', 1)], vid='table',
                    vtitle=_('tickets for %(project)s'))),
        (rgx('/project/([^/]+)/([^/]+)'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)])),
        (rgx('/project/([^/]+)/([^/]+)'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)])),
         ]


_afs = uicfg.autoform_section
_afs.tag_attribute(('Version', 'publication_date'), 'generated')
_afs.tag_attribute(('Version', 'starting_date'), 'primary')
_afs.tag_attribute(('Version', 'prevision_date'), 'primary')
_afs.tag_subject_of(('Version', 'version_of', '*'), 'secondary')
_afs.tag_object_of(('TestInstance', 'for_version', 'Version'), 'generated')
_afs.tag_attribute(('Ticket', 'load'), 'primary')
_afs.tag_attribute(('Ticket', 'load_left'), 'primary')
_afs.tag_subject_of(('Ticket', 'concerns', '*'), 'secondary')
_afs.tag_subject_of(('Ticket', 'done_in', '*'), 'primary')

_affk = uicfg.autoform_field_kwargs
_affk.tag_subject_of(('Ticket', 'concerns', '*'), {'sort': True})


_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('*', 'interested_in', '*'), 'hidden')

_pvs.tag_subject_of(('Project', 'uses', '*'), 'hidden')
_pvs.tag_object_of(('*', 'uses', 'Project'), 'hidden')
_pvs.tag_subject_of(('Project', 'recommends', '*'), 'hidden')
_pvs.tag_object_of(('*', 'recommends', 'Project'), 'hidden')
_pvs.tag_subject_of(('Project', 'documented_by', '*'), 'hidden')
_pvs.tag_object_of(('*', 'test_case_of', 'Project'), 'hidden')

_pvs.tag_object_of(('MailingList', 'mailinglist_of', 'Project'), 'hidden')
_pvs.tag_object_of(('License', 'license_of', 'Project'), 'hidden')

_pvs.tag_subject_of(('Ticket', 'concerns', 'Project'), 'hidden')
_pvs.tag_object_of(('Ticket', 'concerns', 'Project'), 'hidden')
_pvs.tag_subject_of(('Ticket', 'done_in', 'Version'), 'hidden')
_pvs.tag_object_of(('Ticket', 'done_in', 'Version'), 'hidden')

_pvs.tag_subject_of(('Version', 'version_of', 'Project'), 'hidden')
_pvs.tag_object_of(('Version', 'version_of', 'Project'), 'hidden')
_pvs.tag_subject_of(('Version', 'depends_on', 'Version'), 'hidden')
_pvs.tag_object_of(('Version', 'depends_on', 'Version'), 'hidden')

_pvs.tag_object_of(('*', 'documented_by', '*'), 'hidden')

_pvs.tag_subject_of(('Ticket', 'depends_on', '*'), 'sideboxes')
_pvs.tag_object_of(('*', 'depends_on', 'Ticket'), 'sideboxes')
_pvs.tag_subject_of(('Ticket', 'attachment', '*'), 'sideboxes')
_pvs.tag_subject_of(('Ticket', 'appeared_in', '*'), 'sideboxes')
_pvs.tag_object_of(('Ticket', 'appeared_in', '*'), 'hidden')
_pvs.tag_object_of(('*', 'generate_bug', 'Ticket'), 'sideboxes')

_pvs.tag_object_of(('*', 'todo_by', 'CWUser'), 'relations')

_pvs.tag_attribute(('ExtProject', 'name'), 'hidden')

_pvs.tag_attribute(('License', 'name'), 'hidden')
_pvs.tag_attribute(('License', 'url'), 'hidden')

_pvs.tag_object_of(('TestInstance', 'instance_of', '*'), 'hidden')


uicfg.primaryview_display_ctrl.tag_object_of(
    ('*', 'todo_by', 'CWUser'),
    {'vid': 'list', 'label': _('working on release(s):'), 'limit': False,
     'filter': lambda rset: rset.filtered_rset(lambda x: x.state == u'dev'),
     })

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('TestInstance', 'generate_bug', 'Ticket'), True)
_abaa.tag_subject_of(('CWUser', 'todo_by', '*'), False)
_abaa.tag_subject_of(('*', 'instance_of', '*'), False)
_abaa.tag_object_of(('*', 'instance_of', '*'), False)
_abaa.tag_subject_of(('*', 'documented_by', '*'), True)
_abaa.tag_object_of(('*', 'concerns', 'Project'), True)
_abaa.tag_object_of(('*', 'test_case_of', 'Project'), True)
_abaa.tag_object_of(('*', 'done_in', 'Version'), True)
_abaa.tag_object_of(('*', 'appeared_in', 'Version'), True)

_abaa.tag_object_of(('TestInstance', 'for_version', 'Version'), False)
_abaa.tag_object_of(('*', 'test_case_for', 'Ticket'), True)
# File will be autocasted to Image when necessary, so only provide one link to
# add an attachment
_abaa.tag_subject_of(('Ticket', 'attachment', 'File'), True)
_abaa.tag_subject_of(('Ticket', 'attachment', 'Image'), False)
for et in ('Ticket', 'Version', 'TestInstance'):
    _abaa.tag_object_of((et, 'filed_under', 'Folder'), False)
