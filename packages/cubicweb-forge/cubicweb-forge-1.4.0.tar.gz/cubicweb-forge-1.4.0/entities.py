"""forge specific entities class for imported entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime, date, timedelta

from logilab.common.date import nb_open_days

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import IPrevNext, ICalendarViews

from cubes.card.entities import Card as BaseCard
from cubes.file.entities import File as BaseFile, Image as BaseImage
from cubes.comment.entities import Comment as BaseComment
from cubes.email.entities import Email as BaseEmail
from cubes.nosylist.interfaces import INosyList
from cubes.tracker.entities import project, version, ticket
from cubes.tracker.entities import ProjectItemMixIn, fixed_orderby_rql


# project / extproject #########################################################


class ExtProject(AnyEntity):
    __regid__ = 'ExtProject'
    __permissions__ = ('developer', 'client')

    fetch_attrs, fetch_order = fetch_config(['name', 'description', 'description_format'])

    def dc_title(self, format='text/plain'):
        return self.name


class Project(project.Project):

    __implements__ = project.Project.__implements__ + (INosyList,)
    __permissions__ = ('developer', 'client')
    fetch_attrs = project.Project.fetch_attrs + ('homepage', 'summary')

    TICKET_DEFAULT_STATE_RESTR = 'S name IN ("open","done","waiting feedback","in-progress","validation pending")'

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


# version ######################################################################

class Version(version.Version):

    fetch_attrs = ('num', 'description', 'description_format', 'in_state')

    # version'specific logic ##################################################

    def velocity(self):
        """return computed velocity or None if some information is missing"""
        if self.finished():
            stop = self.stop_date()
        else:
            stop =  date.today()
        start = self.start_date()
        if stop is None or start is None or start > stop:
            return None
        nb_days = nb_open_days(start, stop)
        if nb_days:
            return self.progress_info()['done'] / float(nb_days)
        return None

    def tarball_name(self):
        return '%s-%s.tar.gz' % (self.project.name, self.num)

    def download_url(self):
        downloadurl = self.project.downloadurl
        if not downloadurl:
            return
        if not downloadurl[-1] == '/':
            downloadurl +=  '/'
        return '%s%s' % (downloadurl, self.tarball_name())

    def estimated_load(self):
        """return the actually estimated load of the version:
        even if some tasks are marked as done, consider their estimated load and
        not there effective load

        notice that actually 2 values are returned :
        * the estimated load
        * the number of tasks which have no estimated time
        """
        missing = 0
        total = 0
        for entity in self.reverse_done_in:
            estimated_load = entity.load or 0
            if estimated_load is None:
                missing += 1
            else:
                total += estimated_load
        return (total, missing)

    # ui utilities ############################################################

    # number of columns to display
    tickets_rql_nb_displayed_cols = 8
    sort_defs = (('in_state', 'S'), ('type', 'TT'), ('priority', 'PR'))
    def tickets_rql(self):
        """rql for tickets done / todo in this version"""
        return ('Any B,TT,PR,S,C,AC,U,group_concat(TN), TI,D,DF,V '
                'GROUPBY B,TT,PR,S,C,AC,U,TI,D,DF,V %s '
                'WHERE B type TT, B priority PR, B load_left AC, B load C, '
                'B in_state S, T? tags B, T name TN, B created_by U?,'
                'B done_in V, V eid %s, '
                'B title TI, B description D, B description_format DF'
                % (fixed_orderby_rql(self.sort_defs), self.eid))

    defects_rql_nb_displayed_cols = 5
    def defects_rql(self):
        """rql for defects appeared in this version"""
        return ('Any B,S,V,U,group_concat(TN), BT,BD,BDF '
                'GROUPBY B,S,V,U,BT,BD,BDF ORDERBY S '
                'WHERE B in_state S, T? tags B, T name TN, B created_by U?,'
                'B done_in V?, B appeared_in X, X eid %s, '
                'B title BT, B description BD, B description_format BDF'
                % self.eid)

    def progress_class(self):
        """return a class name according to % progress of a version"""
        progress = self.progress()
        if progress == 100:
            return 'complete'
        elif progress == 0:
            return 'none'
        elif progress > 50:
            return 'over50'
        return 'below50'

    # IMileStone interface ####################################################

    parent_type = 'Project'

    def progress_info(self):
        """returns a dictionary describing load and progress of the version"""
        pinfo = {'estimated': self.progress_target,
                 'done': self.progress_done,
                 'todo': self.progress_todo,
                 'notestimated': len([entity for entity in self.reverse_done_in
                                      if entity.load is None]),
                 }
        return pinfo

    def eta_date(self):
        """return expected date based on remaining tasks and velocity"""
        if self.state != 'dev':
            return None
        velocity = self.velocity()
        if velocity is None:
            return None
        # XXX if velocity == 0, use a hidden attribute which is computed from
        #     precedent version's velocity
        velocity = velocity or 1
        return datetime.now() + timedelta(self.todo / velocity)

    def contractors(self):
        return self.todo_by

    def update_progress(self):
        if not 'progress_target' in self.e_schema.subject_relations():
            return # XXX necessary for 1.1.0 migration
        self.progress_target = 0
        self.progress_todo = 0
        self.progress_done = 0
        for ticket in self.reverse_done_in:
            self.progress_target += ticket.corrected_load()
            self.progress_todo += ticket.corrected_load_left()
        self.progress_done = max(0, self.progress_target - self.progress_todo)
        self.set_attributes(progress_target=self.progress_target,
                            progress_todo=self.progress_todo,
                            progress_done=self.progress_done, _cw_unsafe=True)


# ticket #######################################################################

class Ticket(ticket.Ticket):

    __implements__ = ticket.Ticket.__implements__ + (INosyList,)
    fetch_attrs = ('title', 'type', 'priority', 'load', 'load_left', 'in_state')
    noload_cost = 10

    # ticket'specific logic ###################################################

    OPEN_STATES = frozenset(('open', 'waiting feedback', 'in-progress'))

    def corrected_load(self):
        if self.load is not None:
            return self.load
        return self.noload_cost

    def corrected_load_left(self):
        if self.load_left is not None:
            return self.load_left
        return self.corrected_load()


# forge specific entities and library overrides ################################

class License(AnyEntity):
    __regid__ = 'License'
    fetch_attrs = ('name', 'url')


# XXX should be independant of testcard cube'schema
class Card(ProjectItemMixIn, BaseCard):
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


class File(ProjectItemMixIn, BaseFile):

    @property
    def project(self):
        """project item interface"""
        if self.reverse_documented_by:
            return self.reverse_documented_by[0]
        if self.reverse_attachment:
            return self.reverse_attachment[0].project

    def breadcrumbs(self, view=None, recurs=False):
        if self.reverse_attachment:
            if self.reverse_attachment[0].e_schema != 'Email':
                path = self.reverse_attachment[0].breadcrumbs(view, True)
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


class Image(ProjectItemMixIn, BaseImage):

    @property
    def project(self):
        """project item interface"""
        # check reverse_screenshot first, we may be attached to an email
        if self.reverse_screenshot:
            return self.reverse_screenshot[0].project
        if self.reverse_attachment:
            return self.reverse_attachment[0].project

    def parent(self):
        return self.project



class Email(ProjectItemMixIn, BaseEmail):
    pass
