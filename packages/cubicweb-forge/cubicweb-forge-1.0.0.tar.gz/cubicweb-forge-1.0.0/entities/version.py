"""forge project entity class

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from itertools import chain
from datetime import datetime, date, timedelta

from logilab.common.decorators import cached
from logilab.common.date import nb_open_days
from rql.utils import quote

from cubicweb.utils import todate
from cubicweb.interfaces import (IMileStone, IPrevNext, ITimetableViews,
                                 ICalendarViews, ICalendarable)
from cubicweb.common.mixins import ProgressMixIn
from cubicweb.entities import AnyEntity

from cubes.forge.entities import fixed_orderby_rql

def percent(value, total):
    try:
        return 100 * value / total
    except ZeroDivisionError :
        return 0

class Version(ProgressMixIn, AnyEntity):
    id = 'Version'
    fetch_attrs = ('num', 'description', 'description_format', 'in_state')
    __implements__ = AnyEntity.__implements__ + (ICalendarViews, IMileStone, IPrevNext,
                                                 ITimetableViews, ICalendarable)


    @classmethod
    def fetch_order(cls, attr, var):
        if attr == 'num':
            var = 'version_sort_value(%s)' % var
            return '%s DESC' % var
        return None
    fetch_unrelated_order = fetch_order

    def rest_path(self, use_ext_eid=False):
        return u'%s/%s' % (self.project.rest_path(), self.num)

    def add_related_schemas(self):
        return []

    @property
    def project(self):
        """ProjectItem interface"""
        return self.version_of[0]

    def unrelated_rql(self, rtype, targettype, role, ordermethod=None,
                      vocabconstraints=True):
        if rtype == 'depends_on' and role == 'subject':
            return ("DISTINCT Any V2 WITH V2 BEING ((Any V2 WHERE "
                    "V2 version_of P2, V version_of P, P uses P2, "
                    "V eid %(x)s) UNION (Any V2 WHERE V2 version_of P2, "
                    "V version_of P, P recommends P2, V eid %(x)s))")
        else:
            return super(Version, self).unrelated_rql(rtype, targettype, role,
                                                      ordermethod, vocabconstraints)

    # dublin core #############################################################

    def dc_title(self, format='text/plain'):
        return self.num

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.num)

    def dc_date(self, date_format=None):
        if self.publication_date:
            return self.format_date(self.publication_date, date_format=date_format)
        return self.format_date(self.modification_date, date_format=date_format)

    # version'specific logic ##################################################

    def velocity(self):
        """return computed velocity or None if some information is missing"""
        if self.finished():
            stop = self.stop_date()
        else:
            stop =  datetime.now()
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

    def depends_on_rset(self):
        """return a result set of versions on which this one depends or None"""
        rql = 'DISTINCT Version V WHERE MB done_in MV, MV eid %(x)s, '\
              'MB depends_on B, B done_in V, V version_of P, NOT P eid %(p)s'
        args = {'x': self.eid, 'p': self.project.eid}
        eids = set(str(r[0]) for r in self.req.execute(rql, args))
        for row in self.related('depends_on'):
            eids.add(str(row[0]))
        if not eids:
            return None
        return self.req.execute('Version V WHERE V eid in (%s)' % ','.join(eids))

    def next_version(self, states=('planned', 'dev')):
        """return the first version following this one which is in one of the
        given states
        """
        # XXX don't work since version_sort_value is not applied to VN before comparison
        #rql = ('Any V,VN,P ORDERBY version_sort_value(VN) LIMIT 1'
        #       'WHERE V version_of P, P eid %(p)s, V num VN, '
        #       'V num > version_sort_value(%(num)s)')
        #if states is not None:
        #    rql += 'V in_state S, S name IN %s' % ','.join(quote(s) for s in states)
        #rset = self.req.execute(rql, {'p': self.project.eid, 'num': self.num}, 'p')
        #if rset:
        #    return rset.get_entity(0, 0)
        #return None
        found = False
        for version in reversed(self.project.reverse_version_of):
            if found and (states is None or version.state in states):
                return version
            if version is self:
                found = True

    def open_tickets(self):
        return (ticket for ticket in self.reverse_done_in if ticket.is_open())

    def move_open_to_next_version(self):
        """move tickets which are still open into the next version

        XXX as some other methods, this rely in versions being correctly
        ordered, which may not be true on sqlite
        """
        nextversion = self.next_version()
        if nextversion is None:
            raise Exception(self.req._('no next version available'))
        eids = [str(ticket.eid) for ticket in self.open_tickets()]
        self.req.execute('SET X done_in V WHERE X eid IN(%s), V eid %s' %
                         (','.join(eids), nextversion.eid))

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

    def sortvalue(self, rtype=None):
        if rtype is None or rtype == 'num':
            # small hack to add the project name in the sorted values so that
            # out-of-context views get sorted according to project names and
            # in-context views according to version number
            if rtype is None:
                value = [self.project.name]
            else:
                value = []
            for part in self.num.split('.'):
                try:
                    value.append(int(part))
                except ValueError:
                    value.append(part)
            return value
        return super(Version, self).sortvalue(rtype)

    @cached
    def start_date(self):
        """return start date of version, when first transition is done (to
        'dev' state)
        """
        # first tr_info is necessarily the transition to dev
        try:
            tr_info = self.reverse_wf_info_for[1]
            return todate(tr_info.creation_date)
        except IndexError:
            # for versions without transitions passed
            return None

    @cached
    def stop_date(self):
        rql = 'Any MIN(D) WHERE E in_state S, WI wf_info_for E,'\
              'WI to_state S, S name IN ("ready", "published"),'\
              'WI creation_date D, E eid %(x)s'
        rset = self.req.execute(rql, {'x': self.eid}, 'x')
        if rset and rset[0][0]:
            return todate(rset[0][0])
        return None

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return self.project.rest_path(), {}

    # ICalendarViews interface ################################################

    def matching_dates(self, begin, end):
        """return prevision or publication date according to state"""
        if self.in_state[0].name == 'published':
            if self.publication_date:
                return [self.publication_date]
        elif self.prevision_date:
            return [self.prevision_date]
        return []

    # ITimetableViews ################

    @property
    def start(self):
        return self.start_date() or self.starting_date or date.today()

    @property
    def stop(self):
        return self.stop_date() or self.prevision_date or date.today()

    # IMileStone interface ####################################################
    parent_type = 'Project'

    @cached
    def progress_info(self):
        """returns a dictionary describing load and progress of the version"""
        pinfo = { 'notestimated': 0,
                  'estimated': 0,
                  'done': 0,
                  'todo': 0 }
        for entity in self.reverse_done_in:
            estimated = entity.load
            if estimated is None:
                pinfo['notestimated'] += 1
                estimated = entity.noload_cost
            pinfo['estimated'] += estimated
            if entity.load_left is not None:
                pinfo['done'] += estimated - entity.load_left
                pinfo['todo'] += entity.load_left
            else:
                pinfo['todo'] += estimated
        pinfo['todo'] = pinfo['estimated'] - pinfo['done']
        return pinfo

    def finished(self):
        return self.state in (u'ready', u'published')

    def in_progress(self):
        return self.state == u'dev'

    def get_main_task(self):
        return self.project

    def initial_prevision_date(self):
        return self.prevision_date

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

    def completion_date(self):
        return self.publication_date or self.prevision_date

    def contractors(self):
        return [euser for euser in self.todo_by]

    # IPrevNext interface #####################################################

    def previous_entity(self):
        found = False
        for version in self.project.reverse_version_of:
            if found:
                return version
            if version is self:
                found = True

    def next_entity(self):
        return self.next_version(states=None)

    def parent(self):
        return self.project
