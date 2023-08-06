"""tracker server side objects, mainly notification stuff

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from logilab.common.textutils import normalize_text

from cubicweb.selectors import implements
from cubicweb.common.mail import SkipEmail
from cubicweb.sobjects.notification import StatusChangeMixIn, NotificationView


def format_value(value):
    if isinstance(value, unicode):
        return u'"%s"' % value
    return value


class TrackerEmailView(NotificationView):

    def subject(self):
        entity = self.entity(0)
        return '[%s] %s' % (entity.project.name, self._subject(entity))

    def _subject(self, entity):
        return '%s %s (%s)' % (entity.dc_type(), self.message, entity.dc_title())


class TicketPropertiesChangeView(TrackerEmailView):
    id = 'notif_ticket_changed'
    __select__ = implements('Ticket')

    content = _("""
Ticket properties have been updated by %(user)s:
%(changes)s

url: %(url)s
""")

    no_detailed_change_attrs = ('description', 'description_format')

    def _subject(self, entity):
        return self.req._(u'%(etype)s "%(title)s" updated') % {
            'etype': entity.dc_type(), 'title': entity.dc_title()}

    def context(self, **kwargs):
        context = super(TicketPropertiesChangeView, self).context(**kwargs)
        changes = self.req.transaction_data['changes'][self.rset[0][0]]
        _ = self.req._
        formatted_changes = []
        for attr, oldvalue, newvalue in sorted(changes):
            # check current user has permission to see the attribute
            rschema = self.vreg.schema[attr]
            if rschema.is_final():
                if not rschema.has_perm(self.req, 'read', eid=self.rset[0][0]):
                    continue
            # XXX suppose it's a subject relation...
            elif not rschema.has_perm(self.req, 'read', fromeid=self.rset[0][0]):
                continue
            if attr in self.no_detailed_change_attrs:
                msg = _('%s updated') % _(attr)
            elif oldvalue not in (None, ''):
                msg = _('%(attr)s updated from %(oldvalue)s to %(newvalue)s') % {
                    'attr': _(attr),
                    'oldvalue': format_value(oldvalue),
                    'newvalue': format_value(newvalue)}
            else:
                msg = _('%(attr)s set to %(newvalue)s') % {
                    'attr': _(attr), 'newvalue': format_value(newvalue)}
            formatted_changes.append('* ' + msg)
        if not formatted_changes:
            # current user isn't allowed to see changes, skip this notification
            raise SkipEmail()
        context['changes'] = '\n'.join(formatted_changes)
        return context


class VersionStatusChangeView(StatusChangeMixIn, TrackerEmailView):
    __select__ = implements('Version')

    def _subject(self, entity):
        return self.req._(u'version %(num)s is now in state "%(state)s"') % {
            'num': entity.num,
            'state': self.req.__(self._kwargs['current_state'])}


class TicketStatusChangeView(StatusChangeMixIn, TrackerEmailView):
    __select__ = implements('Ticket')

    def _subject(self, entity):
        return self.req._(u'%(etype)s "%(title)s" is now in state "%(state)s"') % {
            'etype': entity.dc_type(), 'title': entity.dc_title(),
            'state': self.req.__(self._kwargs['current_state'])}


class ProjectAddedView(TrackerEmailView):
    id = 'notif_after_add_entity'
    __select__ = implements('Project')

    section_attrs = ['summary', 'description']
    content = _("""
A new project was created by %(user)s: #%(eid)s - %(pname)s

%(pcontent)s

URL
---
%(url)s
""")

    def context(self, **kwargs):
        context = super(ProjectAddedView, self).context(**kwargs)
        entity = self.rset.get_entity(0, 0)
        sections = []
        for attr in self.section_attrs:
            val = entity.printable_value(attr, format='text/plain')
            if val:
                sect = self.format_section(self.req._(attr).capitalize(), val)
                sections.append(sect)
        context['pcontent'] = '\n'.join(sections)
        context['pname'] = entity.name
        return context

    def subject(self):
        return u'[%s] %s: %s' % (
            self.config.appid, self.req.__('New Project'), self.entity(0).name)


class TicketSubmittedView(TrackerEmailView):
    id = 'notif_after_add_relation_concerns'
    __select__ = implements('Ticket')
    content = _("""
New %(etype)s for project %(pname)s :

#%(eid)s - %(title)s
====================
%(mainsection)s

description
-----------
%(description)s

submitter
---------
%(user)s

URL
---
%(url)s
(project URL: %(purl)s)
""")
    field_attrs = ['type', 'priority']

    def context(self, **kwargs):
        ctx = super(TicketSubmittedView, self).context(**kwargs)
        entity = self.rset.get_entity(0, 0)
        sect = []
        for attr in self.field_attrs:
            sect.append(self.format_field(attr, entity.printable_value(attr)))
        ctx['mainsection'] = '\n'.join(sect)
        description = entity.printable_value('description', format='text/plain')
        description = normalize_text(description, 80)
        ctx['description'] = description
        ctx['pname'] = entity.project.name
        ctx['purl'] = entity.project.absolute_url()
        return ctx

    def _subject(self, entity):
        return '%s %s' % (self.req.__('New %s' % entity.e_schema),
                          entity.dc_title())
