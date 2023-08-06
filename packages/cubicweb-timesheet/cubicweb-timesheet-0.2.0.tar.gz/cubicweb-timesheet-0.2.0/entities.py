from logilab.common.decorators import cached
from logilab.common.date import date_range, todate

from cubicweb.interfaces import IPrevNext, ICalendarViews
from cubicweb.entities import AnyEntity, fetch_config, authobjs

from cubes.workorder.entities import Order, WorkOrder
from cubes.calendar.entities import intersect

class Activity(AnyEntity):
    __regid__ = 'Activity'
    fetch_attrs, fetch_order = fetch_config(['diem', 'done_for', 'duration'])
    __implements__ = (IPrevNext, ICalendarViews)

    @property
    def user(self):
        return self.done_by[0].user

    def dc_title(self, format="text/plain"):
        duration = self.duration
        if self.user:
            login = self.user.login
        else:
            login = u''
        try:
            return u'%s %s %s %s [%s]' % (self._cw.format_date(self.diem),
                                          login, duration, self.wp[0].dc_title(),
                                          self._cw._(self.state))
        except:
            # remote sources unavailable or no related wp
            return u'%s %s %s [%s]' % (self._cw.format_date(self.diem),
                                    login, duration, self._cw._(self.state))

    def dc_long_title(self):
        return u'%s %s' % (self.dc_title(), self.description)

    def after_deletion_path(self):
        """return (path, parameters) which should be used as redirect
        information when this entity is being deleted
        """
        return 'view', {}

    def matching_dates(self, begin, end):
        """calendar views interface"""
        start = self.diem
        return list(date_range(start, start))


    # IPrevNext interfaces #######################################

    def previous_entity(self):
        # if the smallest duration
        rql = ("Activity A ORDERBY DUR DESC LIMIT 1 "
               "WHERE A done_by R, R euser U, U eid %(u)s, "
               "A diem = %(d)s, A duration DUR, A duration < %(t)s ")

        rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem,
                                      't':self.duration})
        if rset:
             return rset.get_entity(0, 0)
        else:
            # the smallest id
            rql = ("Activity A ORDERBY A DESC LIMIT 1 WHERE A done_by R,"
                   "R euser U, U eid %(u)s, A diem = %(d)s, "
                   "A duration < %(t)s, A eid < %(eid)s ")

            rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem,
                                          't': self.duration,
                                          'eid':self.eid})
            if rset:
                 return rset.get_entity(0, 0)
            else:
                # next days
                rql = ("Activity A ORDERBY D DESC LIMIT 1 WHERE A done_by R,"
                       "R euser U, U eid %(u)s, A diem D, A diem < %(d)s ")
                rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem})
                if rset:
                    return rset.get_entity(0, 0)


    def next_entity(self):
        rql = ("Activity A ORDERBY DUR LIMIT 1 WHERE A done_by R,"
               "R euser U, U eid %(u)s, A diem = %(d)s, "
               "A duration DUR, A duration > %(t)s ")
        rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem,
                                      't': self.duration})
        if rset:
             return rset.get_entity(0, 0)
        else:
            rql = ("Activity A ORDERBY A LIMIT 1 WHERE A done_by R,"
                   "R euser U, U eid %(u)s, A diem = %(d)s, A eid > %(eid)s, "
                   "A duration > %(t)s")

            rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem,
                                          't':self.duration,
                                          'eid':self.eid})
            if rset:
                 return rset.get_entity(0, 0)

            else:
                rql = ("Activity A ORDERBY D LIMIT 1 WHERE A done_by R,"
                       "R euser U, U eid %(u)s, A diem D,  A diem > %(d)s ")
                rset = self._cw.execute(rql, {'u': self.user.eid, 'd': self.diem})
                if rset:
                    return rset.get_entity(0, 0)


class TimesheetCWUserMixIn(object):

    @property
    def default_resource(self):
        if self.reverse_euser:
            return self.reverse_euser[0]
        return None

class TimesheetCWUser(TimesheetCWUserMixIn, authobjs.CWUser):
    pass

AWHERE = ('WHERE A is Activity, A diem DI, A duration DU, A description DE, '
          'A done_by R, A in_state S, A done_for WO, O split_into WO, ')
ADETAILS = 'Any A, DI, R, DU, WO, DE, S ORDERBY DI,R ' + AWHERE
A_BY_R = 'Any R, S, SUM(DU), MIN(DI), MAX(DI) GROUPBY R,S ORDERBY S ' + AWHERE
A_BY_W = 'Any WO, S, SUM(DU), MIN(DI), MAX(DI) GROUPBY WO, S ORDERBY S ' + AWHERE

class Resource(AnyEntity):
    __regid__ = 'Resource'
    rest_attr = 'title'
    fetch_attrs, fetch_order = fetch_config(('title',))

    rql_activities = ADETAILS+'R eid %(eid)s'
    rql_activities_groupby_workorder = A_BY_W + 'R eid %(eid)s'

    def dc_title(self):
        return '%s' % (self.title)

    def dc_long_title(self):
        return '%s (%s)' % (self.title, self.rtype[0].title)

    @property
    def calendars(self):
        return [cuse.use_calendar[0] for cuse in self.use_calendar]

    @property
    def user(self):
        if self.euser:
            return self.euser[0]
        return None

    def get_day_types(self, start, stop):
        day_types = []
        cuses = []
        for cuse in self.use_calendar:
            cstart = cuse.start or start
            cstart = todate(cstart)
            cstop = cuse.stop or stop
            cstop = todate(cstop)
            if intersect((start, stop), (cstart, cstop)):
                cuses.append( (cstart, cstop, cuse) )
        for date in date_range(start, stop):
            for cstart, cstop, cuse in cuses:
                if cstart <= date <= cstop:
                    day_types.append(cuse.use_calendar[0].get_days_type(date, date)[0])
                    break
        return day_types


class TimesheetOrder(Order):
    rest_attr = 'title'

    rql_activities_groupby_resource = A_BY_R+'O eid %(eid)s'
    rql_activities = ADETAILS+'O eid %(eid)s'

class TimesheetWorkOrder(WorkOrder):

    rql_activities_groupby_resource = A_BY_R+'WO eid %(eid)s'
    rql_activities = ADETAILS+'WO eid %(eid)s'

    def contractors(self):
        return self.todo_by

    def _compute_progress(self):
        self.progress_target = self.budget or 0
        self.progress_done = sum(activity.duration for activity in self.reverse_done_for)
        self.progress_todo = max(0, self.progress_target - self.progress_done)

    # number of columns to display
    activities_rql_nb_displayed_cols = 10
    def activities_rql(self, limit=None):
        return ADETAILS+'WO eid %(eid)s'
