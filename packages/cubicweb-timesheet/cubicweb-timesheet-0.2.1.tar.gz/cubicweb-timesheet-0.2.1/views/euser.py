import datetime
from urlparse import urlparse

from logilab.mtconverter import xml_escape
from logilab.common.date import date_range, previous_month, next_month

from rql.utils import rqlvar_maker

from cubicweb.view import AnyRsetView, EntityView
from cubicweb.selectors import match_form_params, implements, one_line_rset
from cubicweb.uilib import toggle_action
from cubicweb.web import INTERNAL_FIELD_VALUE, stdmsgs, form

from cubes.calendar.views.main import (get_date_range_from_req, WORKING_DAYS,
                                       WORKING_AM_DAYS, WORKING_PM_DAYS)
from cubes.calendar.entities import BadCalendar

WORKING_HALF_DAYS = list(WORKING_AM_DAYS) + list(WORKING_PM_DAYS)


class CWUserActivitySummaryView(EntityView):
    __regid__ = 'euser-stats'
    __select__ = match_form_params('start', 'stop') & implements('CWUser')

    def cell_call(self, row, col):
        _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        start = strptime(self._cw.form['start'], '%Y-%m-%d')
        stop = strptime(self._cw.form['stop'], '%Y-%m-%d')
        self.w(u'<h1>%s %s</h1>' % (_('statisitics for user'), self._cw.user.login))
        self.w(u'<div class="actsum"><table class="listing"><tr>')
        self.w(u'<th>%s</th><th>%s</th><th>%%</th>' %
               (_('project'), _('days worked')))
        self.w(u'</tr><tr>')
        total_days = 0
        # select workcases' activities
        rql = ("Any W, SUM(DUR) WHERE A is Activity, A done_by R, "
               "R euser U, U eid %(x)s, A diem >= %(start)s, "
               "A diem < %(stop)s, A duration DUR, A wp WP, W split_into WP GROUPBY W")
        wactivities = self._cw.execute(rql, {'x' : entity.eid,
                                             'start' : start, 'stop' : stop})
        if wactivities:
            total_days += sum(dur for __, dur in wactivities)
        # select projects' activities
        rql = ("Any P, SUM(DUR) WHERE A is Activity, A done_by R, "
               "R euser U, U eid %(x)s,A diem >= %(start)s, "
               "A diem < %(stop)s, A duration DUR, A wp WP, WP version_of P GROUPBY P")
        pactivities = self._cw.execute(rql, {'x' : entity.eid,
                                             'start' : start, 'stop' : stop})
        if pactivities:
            total_days += sum(dur for __, dur in pactivities)
        for acts in (wactivities, pactivities):
            for row, (__, dur) in enumerate(acts):
                self.w(u'<tr>')
                self.w(u'<td>%s</td><td>%s</td><td>%s</td>' % (
                    self.view('incontext', acts, row=row, col=0), dur,
                    (100. * dur / total_days)))
                self.w(u'</tr>')
        self.w(u'</table></div>')


class CWUserActivitySubmitFormView(form.FormViewMixIn, EntityView):
    __regid__ = 'euser-activities-submitform'
    __select__ = one_line_rset() & implements('CWUser')
    domid = 'activityForm'

    def cell_call(self, row, col, year=None, month=None, day=None, startup=False):
        self._cw.add_css('cubicweb.form.css')
        user = self.cw_rset.get_entity(row, col)
        year = year or self._cw.form.get('year')
        month = month or self._cw.form.get('month')
        day = day or self._cw.form.get('day')
        if year and month and day:
            date = datetime.date(int(year), int(month), int(day))
        else:
            date = datetime.date.today()
        self.w(u'<h2>%s</h2>' % self._cw._('declare activities').capitalize())
        self._make_activity_form(user, date, startup)

    def _build_redirect_url(self, date, startup):
        html = u'<fieldset>'
        if startup:
            curpath = u'/'
            errurl = self._cw.base_url()
            params = None
        else:
            curpath = self._cw.relative_path(includeparams=False)
            errurl = self._cw.url()
            params = urlparse(errurl)[4]
        html += u'<input type="hidden" name="__redirectpath" value="%s" />' % (
            xml_escape(curpath))
        if params:
            html += u'<input type="hidden" name="__redirectparams" value="%s" />' % (
                xml_escape(params))
        html += u'<input type="hidden" name="__errorurl" value="%s" />' % (
            xml_escape(self.session_key()))
        html += u'</fieldset>'
        return html

    def _make_activity_form(self, cwuser, date, startup):
        resource = cwuser.default_resource
        if resource is None:
            return u'<div class="error">%s</div>' % (
                self._cw._('no resource for user %s') % cwuser.login)
        display_fields = [('diem', 'subject'), ('duration', 'subject'),
                          ('done_for', 'subject'), ('description', 'subject'),
                          ('done_by', 'subject')]
        vreg = self._cw.vreg
        activity = vreg['etypes'].etype_class('Activity')(self._cw)
        activity.eid = self._cw.varmaker.next()
        form = vreg['forms'].select('edition', self._cw, entity=activity,
                                    display_fields=display_fields,
                                    redirect_path=self._cw.relative_path(False))
        form.form_buttons = form.form_buttons[:1] # only keep ok button
        renderer = vreg['formrenderers'].select_or_none('htable', self._cw)
        self.w(form.render(formvalues={'done_by':resource.eid, 'diem':date},
                           renderer=renderer))



class EuserMonitorCalendar(EntityView):
    __regid__ = 'user_activity_calendar'
    __select__ = implements('CWUser',)

    def cell_call(self, row, col, year=None, month=None, calid=None):
        self._cw.add_js('cubicweb.ajax.js')
        self._cw.add_css('cubes.calendar.css')
        user = self.cw_rset.get_entity(row, col)
        calid = calid or 'tid%s' % user.eid
        firstday, lastday = get_date_range_from_req(self._cw, year, month)

        # make calendar
        caption = '%s %s' % (self._cw._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(firstday, user, calid)
        prevlink = '<a href="%s">&lt;&lt;</a>' % xml_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % xml_escape(nexturl)

        # build cells
        try:
            celldatas = self._build_activities(user, firstday, lastday)
        except BadCalendar, exc: # in case of missing week day information
            self.w(u'<div class="error">%s</div>' % exc)
            return
        # build table/header
        self.w(u'<table id="%s" class="activitiesCal">'
               u'<tr><th class="prev">%s</th>'
               u'<th class="calTitle" colspan="5"><span>%s</span></th>'
               u'<th class="next">%s</th></tr>'
               u'<tr><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>'
               % (calid, prevlink, caption, nextlink))
        start = firstday - datetime.timedelta(firstday.weekday())
        # date range exclude last day so we should add one day, hence the 7
        stop = lastday + datetime.timedelta(7 - lastday.weekday())
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0: # sunday
                self.w(u'<tr>')
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            cssclasses, total_duration, url, workcases = celldatas[curdate]
            total = total_duration
            if workcases:
                total = u"%s (%s)" % (total, workcases)
            cellcontent = u'<a title="total %s" href="%s">%s</a>' % (
                total, url, curdate.day)
            self.w(u'<td class="%s">%s</td>' % (u' '.join(cssclasses),  cellcontent))

    def _prevnext_links(self, curdate, user, calid):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % user.eid
        prevlink = self._cw.build_ajax_replace_url(calid, rql, 'user_activity_calendar',
                                                   replacemode='swap',
                                                   month=prevdate.month, year=prevdate.year)
        nextlink = self._cw.build_ajax_replace_url(calid, rql, 'user_activity_calendar',
                                                   replacemode='swap',
                                                   month=nextdate.month, year=nextdate.year)
        return prevlink, nextlink

    def _build_activities(self, user, firstday, lastday):
        # figure out which days of month are working days
        resource = user.default_resource
        if resource:
            day_types = dict((date, (dtype, state)) for date, dtype, state in
                             user.reverse_euser[0].get_day_types(firstday, lastday))
        else:
            day_types = {}
        working_dtype = {}
        for eid, state in set(day_types.values()):
            working_dtype[eid] = self._cw.eid_rset(eid).get_entity(0, 0)

        # get activities
        activities = {}
        workcases = {}
        pending_activities = set()
        rql = ("Any DI,DU,S,WR WHERE A is Activity, "
               "  A in_state ST, ST name S, "
               "  A diem <= %(l)s, A diem >= %(f)s, "
               "  A diem DI, A duration DU, "
               "  A done_by R, R euser U, U eid %(u)s, "
               "  A done_for WO, W split_into WO, W title WR")
        rset = self._cw.execute(rql, {'u': user.eid, 'l': lastday, 'f': firstday})
        for diem, duration, state, workcase in rset:
            activities.setdefault(diem, 0)
            workcases.setdefault(diem, [])
            activities[diem] += float(duration)
            workcases[diem].append(workcase)
            if state == 'pending':
                pending_activities.add(diem)

        # build result
        celldatas = {}
        _today = datetime.date.today()
        # date range exclude last day so we should add one day, hence the 7
        for date_ in date_range(firstday, lastday + datetime.timedelta(days=1)):
            cssclass = []
            total_duration = activities.get(date_, 0.)
            dtype, state = day_types.get(date_, (None, None))
            if state == 'pending':
                cssclass.append(u'daytype_pending')
            if dtype and working_dtype[dtype].work_during:
                if date_ <= _today:
                    dtype_title = working_dtype[dtype].title
                    if ((total_duration != 1. and  dtype_title in WORKING_DAYS) or
                        (total_duration != 0.5 and dtype_title in WORKING_HALF_DAYS)):
                        cssclass.append(u'problem')
                    else:
                        if date_ in pending_activities:
                            cssclass.append(u'pending')
                        else:
                            cssclass.append(u'completed')
                    if dtype_title in WORKING_DAYS:
                        total_duration = u'%s / 1.0' % total_duration
                    elif dtype_title in WORKING_HALF_DAYS:
                        total_duration = u'%s / 0.5' % total_duration
                else:
                    if total_duration:
                        cssclass.append(u'problem')
            else:
                if state != 'pending':
                    cssclass.append(u'closed')
                if total_duration:
                    cssclass.append(u'problem')
            a_rql = ("Any A WHERE A is Activity, A diem = '%(d)s', "
                     "A done_by R, R euser U, U eid %(u)s"
                     % {'u': user.eid, 'd': date_.strftime('%Y-%m-%d')})
            url = xml_escape(self._cw.build_url('activities/%s/%s' % (user.login, date_.strftime('%Y-%m-%d'))))
            workcases_str = ','.join(workcases.get(date_, ''))
            celldatas[date_] = (cssclass, total_duration, url, workcases_str)
        if _today in celldatas:
            # celldatas maps days to tuples (cssclass, duration, url, descr)
            celldatas[_today][0].append(u'today')
        return celldatas
