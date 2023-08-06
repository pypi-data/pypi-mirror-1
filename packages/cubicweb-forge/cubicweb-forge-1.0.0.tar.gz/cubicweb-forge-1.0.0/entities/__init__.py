"""forge specific entities class for imported entities

:organization: Logilab
:copyright: 2006-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.interfaces import IPrevNext
from cubicweb.entities import AnyEntity

from cubes.card.entities import Card as BaseCard
from cubes.file.entities import File as BaseFile
from cubes.file.entities import Image as BaseImage
from cubes.comment.entities import Comment as BaseComment
from cubes.folder.entities import Folder as BaseFolder
from cubes.email.entities import Email as BaseEmail

def fixed_orderby_rql(sortsdef, asc=True):
    orderby = []
    for rtype, varname in sortsdef:
        if rtype == 'priority':
            orderby.append('priority_sort_value(%s)' % varname)
        elif rtype == 'num':
            orderby.append('version_sort_value(%s)' % varname)
        else:
            orderby.append(varname)
    if asc:
        return 'ORDERBY %s' % ', '.join(orderby)
    return 'ORDERBY %s DESC' % ', '.join(orderby)


class License(AnyEntity):
    id = 'License'
    fetch_attrs = ('name', 'url')


class TestInstance(AnyEntity):
    id = 'TestInstance'
    fetch_attrs = ('name',)
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)

    @property
    def version(self):
        """project item interface"""
        return self.for_version[0]

    @property
    def project(self):
        """project item interface"""
        return self.version.project

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return self.version.rest_path(), {}

    # IPrevNext/IBreadCrumbs interfaces #######################################

    def previous_entity(self):
        rql = ('TestInstance X ORDERBY X DESC LIMIT 1 '
               'WHERE X for_version V, V eid %(v)s, X eid < %(x)s')
        rset = self.req.execute(rql, {'v': self.version.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0)

    def next_entity(self):
        rql = ('TestInstance X ORDERBY X ASC LIMIT 1 '
               'WHERE X for_version V, V eid %(v)s, X eid > %(x)s')
        rset = self.req.execute(rql, {'v': self.version.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0)

    def breadcrumbs(self, view=None, recurs=False):
        breadcrumbs = self.version.breadcrumbs(view, True)
        url = '%s/%s' % (self.version.absolute_url(), 'tests')
        breadcrumbs += [(url, self.req._('tests')), self]
        return breadcrumbs

# library overrides ###########################################################

class Card(BaseCard):
    fetch_attrs = ('title', 'wikiid')

    @property
    def project(self):
        """project item interface"""
        if self.reverse_documented_by:
            return self.reverse_documented_by[0]
        if self.test_case_of:
            return self.test_case_of[0]
        if self.test_case_for:
            return self.test_case_for[0].project

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.project:
            return self.project.rest_path(), {}
        return 'view', {}

    def breadcrumbs(self, view=None, recurs=False):
        if self.project:
            path = self.project.breadcrumbs(view, True)
            if self.reverse_documented_by:
                url = '%s/%s' % (self.project.absolute_url(), 'documentation')
                path.append( (url, self.req._('documentation')) )
            elif self.test_case_for:
                path = self.test_case_for[0].breadcrumbs(view, True)
            else:
                url = '%s/%s' % (self.project.absolute_url(), 'testcases')
                path.append( (url, self.req._('test cases')) )
            path.append(self)
            return path
        return super(Card, self).breadcrumbs(view, recurs)


class Comment(BaseComment):

    @property
    def project(self):
        """project item interface"""
        return self.root().project

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return self.root().rest_path(), {}


class File(BaseFile):

    @property
    def project(self):
        """project item interface"""
        if self.reverse_documented_by:
            return self.reverse_documented_by[0]
        if self.reverse_attachment:
            try:
                return self.reverse_attachment[0].project
            except AttributeError:
                # XXX
                assert self.reverse_attachment[0].e_schema == 'Email'

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.project:
            return self.project.rest_path(), {}
        return 'view', {}

    def breadcrumbs(self, view=None, recurs=False):
        if self.reverse_attachment:
            try:
                path = self.reverse_attachment[0].breadcrumbs(view, True)
            except AttributeError:
                # XXX
                assert self.reverse_attachment[0].e_schema == 'Email'
            else:
                path.append(self.reverse_attachment[0])
                return path
        if self.project:
            path = [self.project]
            if self.reverse_documented_by:
                url = '%s/%s' % (self.project.absolute_url(), 'documentation')
                label = self.req._('documentation')
                path.append( (url, label) )
            return path
        return super(File, self).breadcrumbs(view, recurs)


class Image(BaseImage):

    @property
    def project(self):
        """project item interface"""
        if self.reverse_attachment:
            return self.reverse_attachment[0].project
        if self.reverse_screenshot:
            return self.reverse_screenshot[0].project

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.project:
            return self.project.rest_path(), {}
        return 'view', {}

    def parent(self):
        return self.project


class ProjectItemMixIn(object):
    """default mixin class for commentable objects to make them implement
    the project item interface. Defined as a mixin for use by custom forge
    templates.
    """
    @property
    def project(self):
        # XXX should we try to pick up one of the see_also projects ?
        # rset = self.req.execute('Any P WHERE P is Project, X see_also P, X eid %(x)s LIMIT 1',
        #                         {'x': self.eid})
        return None

class Email(ProjectItemMixIn, BaseEmail):
    pass
