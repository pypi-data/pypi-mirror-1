"""tracker version entity class

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import date

from logilab.common.decorators import cached
from logilab.common.date import todate

from cubicweb.interfaces import (IMileStone, IPrevNext, ITimetableViews,
                                 ICalendarViews, ICalendarable)
from cubicweb.mixins import ProgressMixIn
from cubicweb.entities import AnyEntity

from cubes.tracker.entities import fixed_orderby_rql


class Version(ProgressMixIn, AnyEntity):
    __regid__ = 'Version'
    __implements__ = AnyEntity.__implements__ + (ICalendarViews, IMileStone, IPrevNext,
                                                 ITimetableViews, ICalendarable)
    fetch_attrs = ('num', 'description', 'in_state')

    FINISHED_STATES = (u'ready', u'published')
    PROGRESSING_STATES =  (u'dev',)
    PUBLISHED_STATES = (u'published')

    @classmethod
    def fetch_order(cls, attr, var):
        if attr == 'num':
            var = 'version_sort_value(%s)' % var
            return '%s DESC' % var
        return None
    fetch_unrelated_order = fetch_order

    def rest_path(self, use_ext_eid=False):
        return u'%s/%s' % (self.project.rest_path(), self.num)

    @property
    def project(self):
        """ProjectItem interface"""
        return self.version_of[0]

    # dublin core ##############################################################

    def dc_title(self, format='text/plain'):
        return self.num

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.num)

    def dc_date(self, date_format=None):
        if self.publication_date:
            date = self.publication_date
        else:
            date = self.modification_date
        return self._cw.format_date(date, date_format=date_format)

    # version'specific logic ###################################################

    def depends_on_rset(self):
        """return a result set of versions on which this one depends or None"""
        rql = 'DISTINCT Version V WHERE MB done_in MV, MV eid %(x)s, '\
              'MB depends_on B, B done_in V, V version_of P, NOT P eid %(p)s'
        args = {'x': self.eid, 'p': self.project.eid}
        eids = set(str(r[0]) for r in self._cw.execute(rql, args))
        for row in self.related('depends_on'):
            eids.add(str(row[0]))
        if not eids:
            return None
        return self._cw.execute('Version V WHERE V eid in (%s)' % ','.join(eids))

    def next_version(self, states=('planned', 'dev')):
        """return the first version following this one which is in one of the
        given states
        """
        found = False
        for version in reversed(self.project.reverse_version_of):
            if found and (states is None or version.state in states):
                return version
            if version is self:
                found = True

    def open_tickets(self):
        return (ticket for ticket in self.reverse_done_in if ticket.is_open())

    # iprogress interface ############################################################
    def contractors(self):
        return [euser for euser in self.todo_by]

    def progress_info(self):
        """returns a dictionary describing load and progress of the version"""
        return {'notestimated': 0,
                'estimated': 0,
                'done': 0,
                'todo': 0 }

    # number of columns to display
    tickets_rql_nb_displayed_cols = 8
    defects_rql_nb_displayed_cols = 5
    sort_defs = (('in_state', 'S'), ('priority', 'PR'))

    def tickets_rql(self):
        return ('Any B,PR,S,U,TI,D,V '
                'GROUPBY B,PR,S,U,TI,D,V %s '
                'WHERE B priority PR, '
                'B in_state S, B created_by U?,'
                'B done_in V, V eid %s, '
                'B title TI, B description D'
                % (fixed_orderby_rql(self.sort_defs), self.eid))

    def defects_rql(self):
        return ('Any B,PR,S,U,TI,D,V '
                'GROUPBY B,PR,S,U,TI,D,V %s '
                'WHERE B priority PR, '
                'B in_state S, B created_by U?,'
                'B appeared_in V, V eid %s, '
                'B title TI, B description D'
                % (fixed_orderby_rql(self.sort_defs), self.eid))

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
        rset = self._cw.execute(rql, {'x': self.eid}, 'x')
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

    def finished(self):
        return self.state in self.FINISHED_STATES

    def in_progress(self):
        return self.state in self.PROGRESSING_STATES

    def initial_prevision_date(self):
        return self.prevision_date

    def completion_date(self):
        return self.publication_date or self.prevision_date

    def get_main_task(self):
        return self.project


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
