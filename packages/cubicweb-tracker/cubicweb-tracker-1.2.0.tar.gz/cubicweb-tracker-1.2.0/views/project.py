"""views for Project entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape
from logilab.common import table as _table

from cubicweb.schema import display_name
from cubicweb.view import EntityView, EntityStartupView
from cubicweb.selectors import (implements, has_related_entities, rql_condition,
                                none_rset, anonymous_user, authenticated_user)
from cubicweb.common import tags
from cubicweb.web import action, component
from cubicweb.web.views import primary, tabs, baseviews

# primary view and tabs ########################################################

class ProjectPrimaryView(tabs.TabsMixin, primary.PrimaryView):
    __select__ = implements('Project')

    tabs = [_('projectinfo_tab'), _('projectroadmap_tab'), _('projecttickets_tab')]
    default_tab = 'projectinfo_tab'

    def render_entity_title(self, entity):
        self.w(u'<div class="projectTitleGroup">%s %s</div>' % (
            entity.dc_type().capitalize(),
            entity.view('reledit', rtype='name',
                        role='subject', reload=True)))
        self.w(u'<br/>')

    def cell_call(self, row, col):
        entity = self.complete_entity(row, col)
        self.render_entity_title(entity)
        self.render_tabs(self.tabs, self.default_tab, entity)


class ProjectInfoTab(primary.PrimaryView):
    id = 'projectinfo_tab'
    __select__ = implements('Project')

    title = None # should not appear in possible views
    attribute_relations = [('summary', 'subject'),
                           ('description', 'subject'),
                           ('uses', 'subject'),
                           ('uses', 'object')]

    def is_primary(self):
        return True

    def render_entity_title(self, entity):
        pass

    def render_entity_attributes(self, entity):
        w = self.w
        w(u'<div class="entityDescr">')
        for rtype, role in self.attribute_relations:
            value = entity.view('reledit', rtype=rtype, role=role)
            if value:
                self.field(display_name(self.req, rtype, role), value,
                           show_label=True, w=self.w, tr=False)
        w(u'</div>')

    def render_entity_relations(self, entity):
        pass


class ProjectRoadmapTab(EntityView):
    """display the latest published version and in preparation version"""
    id = 'projectroadmap_tab'
    __select__ = (anonymous_user() & implements('Project') &
                  has_related_entities('version_of', 'object'))

    title = None # should not appear in possible views

    def cell_call(self, row, col):
        self.rset.get_entity(row, col).view('roadmap', w=self.w)


class ProjectTicketsTab(EntityView):
    id = 'projecttickets_tab'
    __select__ = implements('Project')

    title = None # should not appear in possible views

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        # optimization: prefetch project's to fill entity / relations cache
        entity.reverse_version_of
        rset = self.req.execute(entity.tickets_rql(limit=1))
        self.req.form['actualrql'] = entity.active_tickets_rql()
        self.wview('editable-initialtable', rset, 'null',
                   subvid='incontext', displayactions=1,
                   divid='tickets%s' % entity.eid,
                   displaycols=range(entity.tickets_rql_nb_displayed_cols))


# contextual components ########################################################

class ProjectRoadmapVComponent(component.EntityVComponent):
    """display the latest published version and in preparation version"""
    id = 'roadmap'
    __select__ = (component.EntityVComponent.__select__ &
                  authenticated_user() & implements('Project') &
                  has_related_entities('version_of', 'object'))
    context = 'navcontenttop'
    title = _('Version_plural')
    order = 10

    def cell_call(self, row, col, view=None):
        self.rset.get_entity(row, col).view('roadmap', w=self.w)


# secondary views ##############################################################

class ProjectRoadmapView(EntityView):
    """display the latest published version and in preparation version"""
    id = 'roadmap'
    __select__ = (implements('Project') &
                  has_related_entities('version_of', 'object'))
    title = None # should not appear in possible views
    rql = ('Any V,DATE ORDERBY version_sort_value(N) '
           'WHERE V num N, V prevision_date DATE, V version_of X, '
           'V in_state S, S name IN ("planned", "dev", "ready"), '
           'X eid %(x)s')

    def cell_call(self, row, col):
        self.w(u'<div class="section">')
        entity = self.rset.get_entity(row, col)
        currentversion = entity.latest_version()
        if currentversion:
            self.w(self.req._('latest published version:'))
            self.w(u'&nbsp;')
            currentversion.view('incontext', w=self.w)
            self.w(u'<br/>')
        rset = self.req.execute(self.rql, {'x': entity.eid}, 'x')
        if rset:
            self.wview('ic_progress_table_view', rset)
        allversionsrql = entity.related_rql('version_of', 'object') % {'x': entity.eid}
        self.w('<a href="%s">%s</a>'
               % (xml_escape(self.build_url(vid='list', rql=allversionsrql)),
                  self.req._('view all versions')))
        self.w(u'</div>')


class ProjectOutOfContextView(baseviews.OutOfContextView):
    """project's out of context view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = implements('Project')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        # no summary on ext project
        if getattr(entity, 'summary', None):
            self.w(u'&nbsp;')
            self.w(xml_escape(entity.summary))


# other views ##################################################################

class ProjectStatsView(EntityStartupView):
    """Some statistics : how many bugs, sorted by status, indexed by projects
    """
    id = 'stats'
    __select__ = none_rset() | implements('Project')
    title = _('projects statistics')
    default_rql = 'Any P,PN WHERE P name PN, P is Project'

    def call(self, sort_col=None):
        w = self.w
        req = self.req
        if self.rset is None:
            self.rset = req.execute(self.default_rql)
        table = _table.Table()
        statuslist = [row[0] for row in self.req.execute('DISTINCT Any N WHERE S name N, X in_state S, X is Ticket')]
        severities = ['minor', 'normal', 'important']
        table.create_columns(statuslist + severities + ['Total'])
        nb_cols = len(table.col_names)
        # create a stylesheet to compute sums over rows and cols
        stylesheet = _table.TableStyleSheet()
        # fill table
        i = -1
        for row in self.rset:
            i += 1
            eid = row[0]
            row = []
            total = 0
            for status in statuslist:
                rql = "Any COUNT(A) WHERE A is Ticket, A concerns P, A in_state S, S name %(s)s, P eid %(x)s"
                nbtickets = req.execute(rql, {'x': eid, 's': status}, 'x', build_descr=0)[0][0]
                total += nbtickets
                row.append(nbtickets)
            for severity in severities:
                rql = "Any COUNT(A) WHERE A is Ticket, A concerns P, A priority %(p)s, P eid %(x)s"
                nbtickets = req.execute(rql, {'x': eid, 'p': severity}, 'x', build_descr=0)[0][0]
                total += nbtickets
                row.append(nbtickets)
            row.append(total)
            table.append_row(row, xml_escape(self.entity(i).name))
            assert len(row) == nb_cols
        # sort table according to sort_col if wanted
        sort_col = sort_col or self.req.form.get('sort_col', '')
        if sort_col:
            table.sort_by_column_id(sort_col, method='desc')
        else:
            table.sort_by_column_index(0)
        # append a row to compute sums over rows and add appropriate
        # stylesheet rules for that
        if len(self.rset) > 1:
            table.append_row([0] * nb_cols, 'Total')
            nb_rows = len(table.row_names)
            for i in range(nb_cols):
                stylesheet.add_colsum_rule((nb_rows-1, i), i, 0, nb_rows-2)
            table.apply_stylesheet(stylesheet)
        # render the table
        w(u'<table class="stats" cellpadding="5">')
        w(u'<tr>')
        for col in [''] + table.col_names:
            url = self.build_url(vid='stats', sort_col=col,
                                 __force_display=1,
                                 rql=self.rset.printable_rql())
            self.w(u'<th><a href="%s">%s</a></th>\n' % (xml_escape(url), col))
        self.w(u'</tr>')
        for row_name, row, index in zip(table.row_names, table.data,
                                        xrange(len(table.data))):
            if index % 2 == 0:
                w(u'<tr class="alt0">')
            else:
                w(u'<tr class="alt1">')
            if index == len(table.data) - 1:
                w(u'<td>%s</td>' % row_name)
            else:
                url = self.build_url('project/%s' % self.req.url_quote(row_name))
                self.w(u'<td><a href="%s">%s</a></td>' % (xml_escape(url), row_name))
            for cell_data in row:
                w(u'<td>%s</td>' % cell_data)
            w(u'</tr>')
        w(u'</table>')

