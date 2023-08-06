"""views for Ticket entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.selectors import objectify_selector, implements, two_lines_rset
from cubicweb.common import tags, uilib
from cubicweb.web import component, action
from cubicweb.web.views import primary, baseviews

# primary view and tabs ########################################################

class TicketPrimaryView(primary.PrimaryView):
    """common primary view for bug and story, relying on a mixin class
    to be usable
    """
    __select__ = implements('Ticket')

    def render_entity_title(self, entity):
        self.w(u'<div class="titleGroup">')
        title = xml_escape(entity.dc_title())
        self.w(u'<h2><span class="%s %s">%s</span><span class="state"> [%s]</span></h2>\n'
               % (entity.priority, entity.type, title,
                  xml_escape(self.req._(entity.state))))
        self.w(u'</div>')

    ticket_attributes = ('type', 'priority', 'description' )

    def render_entity_attributes(self, entity):
        w = self.w
        w(u'<table>')
        for attr in self.ticket_attributes:
            w(u'<tr class="row">')
            w(u'<td class="label">%s</td><td>' % display_name(self.req, attr))
            entity.view('reledit', rtype=attr, w=self.w)
            w(u'</td></tr>\n')
        w(u'</table>')
        # Solved in
        if entity.done_in:
            w(u'<div class="label">%s %s</div>' % (self.req._('planned for'),
                                                   entity.in_version().view('oneline')))
        else:
            w(self.req._('not planned'))


# pluggable sections ###########################################################

class TicketIdenticalToVComponent(component.RelatedObjectsVComponent):
    """display identical tickets"""
    id = 'tickectidentical'
    __select__ = component.RelatedObjectsVComponent.__select__ & implements('Ticket')

    rtype = 'identical_to'
    target = 'object'

    title = _('Identical tickets')
    context = 'navcontentbottom'
    order = 20


# secondary views ##############################################################

class TicketOneLineView(baseviews.OneLineView):
    """one representation of a story / bug:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    __select__ = implements('Ticket')

    def cell_call(self, row, col):
        self.wview('incontext', self.rset, row=row)
        entity = self.entity(row, col)
        if entity.in_state:
            self.w(u'&nbsp;[%s]' % xml_escape(self.req._(entity.state)))


class TicketInContextView(baseviews.OneLineView):
    """one representation of a story / bug:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    id = 'incontext'
    __select__ = implements('Ticket')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.dc_title(), href=entity.absolute_url(),
                      title=uilib.cut(entity.dc_description(), 80),
                      klass=entity.priority))


# actions ######################################################################

@objectify_selector
def ticket_has_next_version(cls, req, rset, row=None, col=0, **kwargs):
    rschema = req.vreg.schema.rschema('done_in')
    if row is None:
        # action is applyable if all entities are ticket from the same project,
        # in an open state, share some versions to which they may be moved
        project, versions = None, set()
        for entity in rset.entities():
            if entity.e_schema != 'Ticket':
                return 0
            if not entity.is_open():
                return 0
            if project is None:
                project = entity.project
            elif project.eid != entity.project.eid:
                return 0
            if entity.in_version():
                versions.add(entity.in_version().eid)
        if project is None:
            return 0
        maymoveto = []
        for version in project.versions_in_state(('planned', 'dev')).entities():
            if version.eid in versions:
                continue
            for entity in rset.entities():
                if not rschema.has_perm(req, 'add', fromeid=entity.eid,
                                        toeid=version.eid):
                    break
            else:
                maymoveto.append(version)
        if maymoveto:
            rset.maymovetoversions = maymoveto # cache for use in action
            return 1
        return 0
    entity = rset.get_entity(row, 0)
    versionsrset = entity.project.versions_in_state(('planned', 'dev'))
    if not versionsrset:
        return 0
    ticketversion = entity.in_version() and entity.in_version().eid
    maymoveto = [version for version in versionsrset.entities()
                 if not version.eid == ticketversion and
                 rschema.has_perm(req, 'add', fromeid=entity.eid,
                                  toeid=version.eid)]
    if maymoveto:
        rset.maymovetoversions = maymoveto # cache for use in action
        return 1
    return 0


class TicketAction(action.Action):
    __select__ = action.Action.__select__ & implements('Ticket')
    # use "mainactions" category to appears in table filter's actions menu
    category = 'mainactions'


class TicketMoveToNextVersionActions(TicketAction):
    id = 'movetonext'
    __select__ = TicketAction.__select__ & ticket_has_next_version()

    submenu = _('move to version')

    def fill_menu(self, box, menu):
        # when there is only one item in the sub-menu, replace the sub-menu by
        # item's title prefixed by 'move to version'
        menu.label_prefix = self.req._(self.submenu)
        super(TicketMoveToNextVersionActions, self).fill_menu(box, menu)

    def actual_actions(self):
        for version in self.rset.maymovetoversions:
            yield self.build_action(version.num, self.url(version))

    def url(self, version):
        if self.row is None:
            eids = [str(row[self.col or 0]) for row in self.rset]
        else:
            eids = [str(self.rset[self.row][self.col or 0])]
        rql = 'SET X done_in V WHERE X eid IN(%s), V eid %%(v)s' % ','.join(eids)
        msg = self.req._('tickets moved to version %s') % version.num
        return self.user_rql_callback((rql, {'v': version.eid}, 'v'), msg)


class TicketCSVExportAction(TicketAction):
    id = 'ticketcsvexport'
    __select__ = two_lines_rset() & TicketAction.__select__

    title = _('csv export')

    def url(self):
        return self.build_url('view', rql=self.rset.printable_rql(),
                              vid='csvexport')
