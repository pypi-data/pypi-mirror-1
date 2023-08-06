"""views for Version entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import (objectify_selector, implements, score_entity,
                                match_search_state, one_line_rset)
from cubicweb.view import StartupView
from cubicweb.common import tags
from cubicweb.web import uicfg, component, action
from cubicweb.web.views import primary, baseviews, iprogress, xmlrss

# primary view and tabs ########################################################

class VersionPrimaryView(primary.PrimaryView):
    __select__ = implements('Version')

    def render_entity_title(self, entity):
        w = self.w
        w(u'<div class="titleGroup">')
        w(u'<h2 class="complete">') #% entity.progress_class())
        if entity.version_of:
            project_name = entity.version_of[0].name
        else:
            project_name = ''
        self.wdata('%s %s %s %s' % (entity.dc_type().capitalize(),
                                    project_name, entity.num,
                                    self.req._(entity.state)))
        w(u'</h2>\n')
        w(u'</div>')

    def render_entity_metadata(self, entity):
        super(VersionPrimaryView, self).render_entity_metadata(entity)
        pdfcomp = self.vreg['components'].select_object('pdfview', self.req,
                                                        rset=self.rset)
        if pdfcomp:
            pdfcomp.render(w=self.w, vid=self.id)

    def summary(self, entity):
        return xml_escape(entity.project.summary)

    def render_entity_attributes(self, entity):
        if entity.description:
            self.w(u'<div class="entityDescr"><b>%s</b> %s</div>' % (
                self.req._('focus for this release'),
                entity.view('reledit', rtype='description')))

    def render_entity_relations(self, entity):
        w = self.w; req = self.req
        req.add_js('cubicweb.ajax.js')
        if entity.conflicts:
            w(u"<div class='entityDescr'><b>%s</b>:<ul>"
              % display_name('conflicts', context='Version'))
            vid = len(entity.conflicts) > 1 and 'list' or 'outofcontext'
            w(vid, entity.conflicts)
            w(u'</ul></div>')
        # Tickets in version
        params = req.build_url_params(displaycols=range(entity.tickets_rql_nb_displayed_cols),
                                      displayfilter=1, displayactions=1,
                                      divid='bugs', subvid='incontext',
                                      title=req._('Ticket_plural'))
        hackedvid = xml_escape('table&' + params)
        req.html_headers.define_var('LOADING_MSG', _('Loading'))
        w(u'<div class="dynamicFragment" id="buglist" cubicweb:vid="%s" '
          'cubicweb:fallbackvid="null" cubicweb:rql="%s"></div>'
          % (hackedvid, req.url_quote(entity.tickets_rql())))
        # Defects appeared in version
        params = req.build_url_params(displaycols=range(entity.defects_rql_nb_displayed_cols),
                                      displayfilter=1, displayactions=1,
                                      divid='defects', subvid='incontext',
                                      title=_('Defects_plural'))
        hackedvid = xml_escape('table&' + params)
        w(u'<div class="dynamicFragment" id="defectslist" cubicweb:vid="%s" '
          'cubicweb:fallbackvid="null" cubicweb:rql="%s"></div>'
          % (hackedvid, req.url_quote(entity.defects_rql())))


# pluggable sections ###########################################################

class VersionInfoVComponent(component.EntityVComponent):
    """display version information table in the context of the project"""
    id = 'versioninfo'
    __select__ = component.EntityVComponent.__select__ & implements('Version')
    context = 'navcontenttop'
    order = 10

    def cell_call(self, row, col, view=None):
        self.w(u'<div class="section">')
        version = self.entity(row, col)
        view = self.vreg['views'].select('progress_table_view', self.req,
                                         rset=version.as_rset())
        columns = list(view.columns)
        for col in ('project', 'milestone'):
            try:
                columns.remove(col)
            except ValueError:
                self.warning('could not remove %s from columns' % col)
        view.render(w=self.w, columns=columns)
        self.w(u'</div>')


# secondary views ##############################################################

class VersionTextView(baseviews.TextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(entity.num)
        if entity.in_state:
            self.w(u' [%s]' % self.req._(entity.state))


class VersionIncontextView(baseviews.InContextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        self.w(tags.a(entity.num, href=entity.absolute_url()))


class VersionOutOfContextView(baseviews.OutOfContextView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.entity(row, col)
        if entity.version_of:
            project = entity.version_of[0]
            self.w(tags.a(project.name, href=project.absolute_url()))
        self.w(u'&nbsp;-&nbsp;')
        self.w(u'<a href="%s">' % xml_escape(entity.absolute_url()))
        self.wdata(entity.num)
        if entity.in_state:
            self.wdata(u' [%s]' % self.req._(entity.state))
        self.w(u'</a>')


# other views ##################################################################

class VersionProgressTableView(iprogress.ProgressTableView):
    __select__ = implements('Version')

    title = _('version progression')

    columns = (_('project'), _('milestone'), _('state'), _('planned_start'),
               _('planned_delivery'), _('depends_on'), _('todo_by'))

    def build_depends_on_cell(self, entity):
        vrset = entity.depends_on_rset()
        if vrset: # may be None
            vid = len(vrset) > 1 and 'list' or 'outofcontext'
            return self.view(vid, vrset, 'null')
        return u''

    def build_planned_start_cell(self, entity):
        """``starting_date`` column cell renderer"""
        if entity.starting_date:
            return self.format_date(entity.starting_date)
        return u''

    def build_planned_delivery_cell(self, entity):
        """``initial_prevision_date`` column cell renderer"""
        if entity.finished():
            return self.format_date(entity.completion_date())
        return self.format_date(entity.initial_prevision_date())


class VersionsInfoView(StartupView):
    """display versions in state ready or development, or marked as prioritary.
    """
    id = 'versionsinfo'
    title = _('All current versions')

    def call(self, sort_col=None):
        rql = ('Any X,P,N,PN ORDERBY PN, version_sort_value(N) '
               'WHERE X num N, X version_of P, P name PN, '
               'EXISTS(X in_state S, S name IN ("dev", "ready")) ')
        rset = self.req.execute(rql)
        self.wview('progress_table_view', rset, 'null')
        url = self.build_url(rql='Any P,X ORDERBY PN, version_sort_value(N) '
                             'WHERE X num N, X version_of P, P name PN')
        self.w(u'<a href="%s">%s</a>\n'
               % (xml_escape(url), self.req._('view all versions')))


class RssItemVersionView(xmlrss.RSSItemView):
    __select__ = implements('Version')

    def cell_call(self, row, col):
        entity = self.complete_entity(row, col)
        self.w(u'<item>\n')
        self.w(u'<guid isPermaLink="true">%s</guid>\n'
               % xml_escape(entity.absolute_url()))
        self.render_title_link(entity)
        self._marker('description', entity.dc_description(format='text/html'))
        self._marker('dc:date', entity.dc_date(self.date_format))
        self.render_user_in_charge(entity)
        self.w(u'</item>\n')

    def render_user_in_charge(self, entity):
        if entity.todo_by:
            for user in entity.todo_by:
                self._marker('dc:creator', user.name())


# actions ######################################################################

class VersionAddTicketAction(action.LinkToEntityAction):
    id = 'addticket'
    __select__ = (action.LinkToEntityAction.__select__ & implements('Version')
                  & score_entity(lambda x: x.state in ('planned', 'dev')))

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
    __select__ = (action.LinkToEntityAction.__select__ & implements('Version')
                  & score_entity(lambda x: x.state == 'published'))

    title = _('add Ticket appeared_in Version object')
    rtype = 'appeared_in'
    category = 'mainactions'

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'done_in', 'Version'), False)
_abaa.tag_object_of(('*', 'appeared_in', 'Version'), False)

