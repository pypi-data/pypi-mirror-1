"""Custom form for tracker

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import implements, entity_implements, match_transition
from cubicweb.web import uicfg, formfields
from cubicweb.web.views import workflow, editviews, autoform


_afs = uicfg.autoform_section
_afs.tag_attribute(('Version', 'publication_date'), 'generated')
_afs.tag_attribute(('Version', 'starting_date'), 'primary')
_afs.tag_attribute(('Version', 'prevision_date'), 'primary')
_afs.tag_subject_of(('Version', 'version_of', 'Project'), 'generated')
_afs.tag_object_of(('Version', 'version_of', 'Project'), 'generated')
_afs.tag_subject_of(('Ticket', 'concerns', 'Project'), 'secondary')
_afs.tag_object_of(('Ticket', 'concerns', 'Project'), 'generated')
_afs.tag_subject_of(('Ticket', 'done_in', 'Version'), 'primary')

_affk = uicfg.autoform_field_kwargs
_affk.tag_attribute(('Ticket', 'priority'), {'sort': False})
_affk.tag_subject_of(('Ticket', 'done_in', '*'), {'sort': False})


class VersionChangeStateForm(workflow.ChangeStateForm):
    __select__ = implements('Version') & match_transition('publish')

    publication_date = formfields.DateField(eidparam=True)

    def form_field_display_value(self, field, rendervalues, load_bytes=False):
        # using initial on the field doesn't work since it's not considered
        # (entity has an eid)
        if field.name == 'publication_date':
            return self.format_date(self.edited_entity.publication_date or datetime.now())
        return super(VersionChangeStateForm, self).form_field_display_value(
            field, rendervalues, load_bytes)


class ShortComboboxView(editviews.ComboboxView):
    """by default combobox view is redirecting to textoutofcontext view
    but in the case of projects we want a shorter view
    """
    __select__ = implements('Project')
    def cell_call(self, row, col):
        self.w(self.entity(row, col).dc_title())


class TicketEditionForm(autoform.AutomaticEntityForm):
    __select__ = entity_implements('Ticket')

    def subject_done_in_vocabulary(self, rtype, limit=None):
        if not self.edited_entity.has_eid():
            peids = self.edited_entity.linked_to('concerns', 'subject')
            if peids:
                rschema = self.req.vreg.schema['done_in']
                rset = self.req.execute(
                    'Any V, VN, P WHERE V version_of P, P eid %(p)s, V num VN, '
                    'V in_state ST, NOT ST name "published"', {'p': peids[0]})
                return sorted((v.view('combobox'), v.eid)
                              for v in rset.entities()
                              if rschema.has_perm(self.req, 'add', toeid=v.eid))
            return []
        return self.subject_relation_vocabulary(rtype, limit)
