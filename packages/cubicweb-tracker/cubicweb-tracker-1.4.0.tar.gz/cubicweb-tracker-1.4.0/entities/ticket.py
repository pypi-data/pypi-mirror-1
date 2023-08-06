"""tracker specific entities class for Ticket

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.interfaces import IPrevNext
from cubicweb.entities import AnyEntity


class Ticket(AnyEntity):
    __regid__ = 'Ticket'
    __permissions__ = ('developer', 'client')
    __implements__ = AnyEntity.__implements__ + (IPrevNext,)
    fetch_attrs = ('title', 'type', 'priority', 'in_state')

    OPEN_STATES = frozenset(('in-progress',))

    @classmethod
    def fetch_order(cls, attr, var):
        if attr == 'priority':
            return 'priority_sort_value(%s)' % var
        if attr in ('title', 'type'):
            return var
        return None

    @property
    def project(self):
        """project item interface"""
        return self.concerns[0]

    # hierarchy #############################################################

    def parent(self):
        parents = self.done_in or self.concerns
        if parents:
            return parents[0]

    # dublin core #############################################################

    def dc_title(self):
        return u'#%s: %s' % (self.eid, self.title)

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.dc_title())

    # ticket'specific logic ###################################################


    def is_open(self):
        return self.state in self.OPEN_STATES

    def state_history(self):
        """returns a list of dates where the state changed from "open" to "not-open"
        :returns: a list couples of (date, is_open)
        """
        dates = [(self.creation_date, True)]
        for tr_info in self.reverse_wf_info_for:
            prevstate = tr_info.previous_state.name
            nextstate = tr_info.new_state.name
            if prevstate in self.OPEN_STATES and nextstate not in self.OPEN_STATES:
                dates.append( (tr_info.creation_date, False) )
            elif prevstate not in self.OPEN_STATES and nextstate in self.OPEN_STATES:
                dates.append( (tr_info.creation_date, True) )
        return sorted(dates)

    def in_version(self):
        versions = self.done_in
        if versions:
            return versions[0]

    def next_version(self):
        version = self.in_version()
        if version:
            return version.next_version()
        return self.project.versions_in_state(('planned', 'dev'), True)

    def sortvalue(self, rtype=None):
        if rtype == 'priority':
            return ['minor', 'normal', 'important'].index(self.priority)
        return super(Ticket, self).sortvalue(rtype)

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        if self.done_in:
            return self.done_in[0].rest_path(), {}
        return self.project.rest_path(), {}

    # IPrevNext interface #######################################

    def previous_entity(self):
        rql = ('Any X,T ORDERBY X DESC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid < %(x)s')
        rset = self._cw.execute(rql, {'p': self.project.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        rql = ('Any X,T ORDERBY X ASC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid > %(x)s')
        rset = self._cw.execute(rql, {'p': self.project.eid, 'x': self.eid})
        if rset:
            return rset.get_entity(0, 0)
