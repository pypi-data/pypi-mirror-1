"""Custom form for tracker

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import implements, entity_implements, match_transition
from cubicweb.web.formfields import DateField
from cubicweb.web.views import workflow, editviews, autoform

class VersionChangeStateForm(workflow.ChangeStateForm):
    __select__ = implements('Version') & match_transition('publish')

    publication_date = DateField(eidparam=True)

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
                rset = self.req.execute(
                    'Any V, VN, P WHERE V version_of P, P eid %(p)s, V num VN, '
                    'V in_state ST, NOT ST name "published"', {'p': peids[0]})
                return sorted((v.view('combobox'), v.eid) for
                              v in rset.entities())
            return []
        return self.subject_relation_vocabulary(rtype, limit)
