from cubicweb.selectors import implements
from cubicweb.web.facet import RelationFacet, AttributeFacet

class TicketConcernsFacet(RelationFacet):
    id = 'concerns-facet'
    __select__ = AttributeFacet.__select__ & implements('Ticket')
    rtype = 'concerns'
    target_attr = 'name'


class TicketDoneInFacet(RelationFacet):
    id = 'done_in-facet'
    __select__ = AttributeFacet.__select__ & implements('Ticket')
    rtype = 'done_in'
    target_attr = 'num'
    sortfunc = 'VERSION_SORT_VALUE'
    sortasc = False


class TicketPriorityFacet(AttributeFacet):
    id = 'priority-facet'
    __select__ = AttributeFacet.__select__ & implements('Ticket')
    rtype = 'priority'
    sortfunc = 'PRIORITY_SORT_VALUE'


class TicketTypeFacet(AttributeFacet):
    id = 'type-facet'
    __select__ = AttributeFacet.__select__ & implements('Ticket')
    rtype = 'type'
