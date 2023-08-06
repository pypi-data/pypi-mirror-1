from cubicweb.selectors import implements
from cubicweb.web.facet import RelationFacet, AttributeFacet, RangeFacet, DateRangeFacet

class ActivityDurationFacet(RangeFacet):
    __regid__ = 'duration-facet'
    __select__ = RangeFacet.__select__ & implements('Activity')
    rtype = 'duration'

class ActivityDiemFacet(DateRangeFacet):
    __regid__ = 'diem-facet'
    __select__ = DateRangeFacet.__select__ & implements('Activity')
    rtype = 'diem'

class ActivityWorkorderFacet(RelationFacet):
    __regid__ = 'activity-workorder-facet'
    __select__ = RelationFacet.__select__ & implements('Activity')
    rtype = 'done_for'
    target_attr = 'title'

class ActivityResourceFacet(RelationFacet):
    __regid__ = 'activity-resource-facet'
    __select__ = RelationFacet.__select__ & implements('Activity')
    accepts = ('Activity',)
    rtype = 'done_by'
    target_attr = 'title'

