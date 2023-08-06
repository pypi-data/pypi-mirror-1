"""tracker specific hooks

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from itertools import chain

from logilab.common.decorators import classproperty

from cubicweb import ValidationError
from cubicweb.schema import META_RTYPES
from cubicweb.server import pool, hooksmanager, hookhelper
from cubicweb.sobjects import notification

# automatization hooks #########################################################

class VersionStatusChangeHook(hooksmanager.Hook):
    """when a ticket is done, automatically set its version'state to 'dev' if
      necessary
    """
    events = ('after_add_relation',)
    accepts = ('in_state',)
    ticket_states_start_version = set(('in-progress',))

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity_from_eid(fromeid)
        if entity.e_schema != 'Ticket':
            return
        if entity.state in self.ticket_states_start_version \
               and entity.in_version():
            version = entity.in_version()
            if any(tr for tr in version.possible_transitions()
                   if tr.name == 'start development'):
                version.fire_transition('start development')


class TicketDoneInChangeHook(hooksmanager.Hook):
    """when a ticket is attached to a version and it's identical to another one,
    attach the other one as well
    """
    events = ('after_add_relation',)
    accepts = ('done_in',)

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity_from_eid(fromeid)
        execute = entity.req.execute
        for identic in entity.identical_to:
            iversion = identic.in_version()
            iveid = iversion and iversion.eid
            if iveid != toeid:
                try:
                    execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                            {'x': identic.eid, 'v': toeid}, 'x')
                except:
                    self.exception("can't synchronize version")


class TicketStatusChangeHook(hooksmanager.Hook):
    """when a ticket status change and it's identical to another one, change the
    state of the other one as well
    """
    events = ('after_add_entity',)
    accepts = ('TrInfo',)

    def call(self, session, entity):
        forentity = entity.for_entity
        if forentity.e_schema != 'Ticket' or not forentity.identical_to:
            return
        pstate = entity.previous_state
        tr = entity.transition
        execute = entity.req.execute
        for identic in forentity.identical_to:
            if identic.current_state and identic.current_state.eid == pstate.eid:
                try:
                    identic.fire_transition(tr.name,
                                            entity.comment, entity.comment_format)
                except:
                    self.exception("can't synchronize identical ticket's state")


# verification hooks ###########################################################

# XXX postpone to an operation, else we may cheat to by-pass this check (prove
# it in a test first!)
class CheckVersionNameOfAProject(hooksmanager.Hook):
    """check that the a version of the same project with the same num doesn't
    already exist
    """
    events = ('before_add_relation',)
    accepts = ('version_of',)

    def call(self, session, fromeid, rtype, toeid):
        entity = session.entity_from_eid(fromeid)
        project = session.entity_from_eid(toeid)
        rset = session.execute(
            'Any X WHERE X num %(num)s, X version_of P, P eid %(p)s',
            {'num': entity.num, 'p': project.eid})
        if rset and (len(rset)>1 or rset[0][0] != entity.eid):
            msg = session._(u'%(vnum)s release number already exists for the project %(prj)s') % {
                'vnum': entity.num, 'prj': project.name}
            raise ValidationError(entity.eid, {"num": msg})


# notification hooks ###########################################################

class TicketChangedNotificationOp(pool.SingleLastOperation):

    def precommit_event(self):
        session = self.session
        for eid in session.transaction_data['changes']:
            view = session.vreg['views'].select('notif_ticket_changed', session,
                                                rset=session.eid_rset(eid, 'Ticket'),
                                                row=0)
            notification.RenderAndSendNotificationView(session, view=view)

    def commit_event(self):
        pass


class BeforeUpdateTicket(hooksmanager.Hook):
    events = ('before_update_entity',)
    accepts = ('Ticket',)
    skip_attrs = META_RTYPES | set(('done_in', 'concerns', 'description_format'))

    def call(self, session, entity):
        if entity.eid in session.transaction_data.get('neweids', ()):
            return # entity is being created
        if session.is_super_session:
            return # ignore changes triggered by hooks
        # then compute changes
        changes = session.transaction_data.setdefault('changes', {})
        thisentitychanges = changes.setdefault(entity.eid, set())
        attrs = [k for k in entity.edited_attributes if not k in self.skip_attrs]
        if not attrs:
            return
        rqlsel, rqlrestr = [], ['X eid %(x)s']
        for i, attr in enumerate(attrs):
            var = chr(65+i)
            rqlsel.append(var)
            rqlrestr.append('X %s %s' % (attr, var))
        rql = 'Any %s WHERE %s' % (','.join(rqlsel), ','.join(rqlrestr))
        rset = session.execute(rql, {'x': entity.eid}, 'x')
        for i, attr in enumerate(attrs):
            oldvalue = rset[0][i]
            newvalue = entity[attr]
            if oldvalue != newvalue:
                thisentitychanges.add((attr, oldvalue, newvalue))
        if thisentitychanges:
            TicketChangedNotificationOp(session)


class BeforeInVersionChangeHook(hooksmanager.Hook):
    events = ('before_add_relation',)
    accepts = ('done_in',)

    def call(self, session, fromeid, rtype, toeid):
        if fromeid in session.transaction_data.get('neweids', ()):
            return # entity is being created
        changes = session.transaction_data.setdefault('changes', {})
        thisentitychanges = changes.setdefault(fromeid, set())
        oldrset = session.execute("Any VN WHERE V num VN, T done_in V, T eid %(eid)s",
                                  {'eid': fromeid})
        oldversion = oldrset and oldrset[0][0] or None
        newrset = session.execute("Any VN WHERE V num VN, V eid %(eid)s",
                                  {'eid': toeid})
        newversion = newrset[0][0]
        if oldversion != newversion:
            thisentitychanges.add(('done_in', oldversion, newversion))
            TicketChangedNotificationOp(session)


# require_permission propagation hooks #########################################

# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set(('concerns', 'version_of'))
# not necessary on:
#
# * "secondary" relations: todo_by, done_in, appeared_in, depends_on, uses
# * no propagation needed: wf_info_for
#
# XXX: see_also


class AddEntitySecurityPropagationHook(hooksmanager.PropagateSubjectRelationHook):
    """propagate permissions when new entity are added"""
    rtype = 'require_permission'
    subject_relations = S_RELS
    object_relations = O_RELS

    @classproperty
    def accepts(cls):
        return chain(cls.subject_relations, cls.object_relations)

class AddPermissionSecurityPropagationHook(hooksmanager.PropagateSubjectRelationAddHook):
    """propagate permissions when new entity are added"""
    rtype = 'require_permission'
    subject_relations = S_RELS
    object_relations = O_RELS
    accepts = ('require_permission',)

class DelPermissionSecurityPropagationHook(hooksmanager.PropagateSubjectRelationDelHook):
    rtype = 'require_permission'
    subject_relations = S_RELS
    object_relations = O_RELS
    accepts = ('require_permission',)


# has_group_permission propagation hooks #######################################

class AddGroupPermissionSecurityPropagationHook(hooksmanager.Hook):
    """propagate on group users when a permission is granted to a group"""
    events = ('after_add_relation',)
    accepts = ('require_group',)
    rql = ('SET U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT U has_group_permission P')

    def call(self, session, fromeid, rtype, toeid):
        if session.describe(fromeid)[0] != 'CWPermission':
            return
        session.unsafe_execute(self.rql, {'p': fromeid, 'g': toeid},)


class DelGroupPermissionSecurityPropagationHook(AddGroupPermissionSecurityPropagationHook):
    """propagate on group users when a permission is removed to a group"""
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT EXISTS(U in_group G2, P require_group G2)')


class AddInGroupSecurityPropagationHook(hooksmanager.Hook):
    """propagate group permission to users when a permission is granted to a group"""
    events = ('after_add_relation',)
    accepts = ('in_group',)
    rql = ('SET U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT U has_group_permission P')

    def call(self, session, fromeid, rtype, toeid):
        session.unsafe_execute(self.rql, {'u': fromeid, 'g': toeid})


class DelInGroupSecurityPropagationHook(AddInGroupSecurityPropagationHook):
    """propagate on existing entities when a permission is deleted"""
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT EXISTS(U in_group G2, P require_group G2)')
