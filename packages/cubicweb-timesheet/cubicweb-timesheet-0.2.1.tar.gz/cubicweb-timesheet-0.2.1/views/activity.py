# -*- coding: utf-8 -*-
"""activity related views.

:organization: Logilab
:copyright: 2007-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

import datetime

from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.schema import display_name
from cubicweb.selectors import (implements, empty_rset, multi_columns_rset,
                                match_user_groups, score_entity)
from cubicweb.view import AnyRsetView, EntityView
from cubicweb.web import INTERNAL_FIELD_VALUE, stdmsgs, action
from cubicweb.web.views import tableview, calendar


class ActivitySummaryView(AnyRsetView):
    __regid__ = 'actsummary'
    __select__ = implements('Activity') & multi_columns_rset(7)

    # XXX we should make a very strict selector here
    def call(self):
        total_duration = sum(e.duration for e in self.cw_rset.entities())
        self.w(u'<h3>%s: %s</h3>' % (_('total'), total_duration))
        self.wview('table', self.cw_rset, 'null', displaycols=range(1,6))

        resdict = {}
        for __, __, res, __, duration, __, login in self.cw_rset:
            resdur = resdict.get(login, 0)
            resdur += duration
            resdict[login] = resdur
        self.w(u'<h2>%s</h2>' % _('statistics'))
        self.w(u'<table class="listing">')
        self.w(u'<tr><th>%s</th><th>%s</th></tr>' % (_('resource'), _('duration')))
        for even_odd, (login, resdur) in enumerate(sorted(resdict.iteritems())):
            self.w(u'<tr class="%s">' % (even_odd % 2 and "odd" or "even"))
            self.w(u'<td>%s</td>' % login)
            self.w(u'<td>%s</td>' % resdur)
            self.w(u'</tr>')
        self.w(u'</table>')


class ActivitySubmitView(EntityView):
    __regid__ = 'activities-submit'
    __select__ = empty_rset | implements('Activity')

    def call(self, year=None, month=None, day=None):
        self.wview('activitytable', self.cw_rset, 'null')
        self._cw.user.view('euser-activities-submitform', w=self.w,
                           year=year, month=month, day=day)


# XXX see generic definition for tablecontext view in gingouz.views
class ActivityTableContext(EntityView):
    __regid__ = 'tablecontext'
    __select__ = implements('Activity')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s"><img alt="%s" src="data/accessories-text-editor.png" /></a>' %
               (xml_escape(entity.absolute_url(vid='edition')),
                self._cw._('actions_edit')))


class ActivityTable(EntityView):
    __regid__ = 'activitytable'
    __select__ = implements('Activity')
    title = _('activitytable')

    def call(self, showresource=True):
        _ = self._cw._
        headers  = [_("diem"), _("duration"), _("workpackage"), _("description"), _("state"), u""]
        eids = ','.join(str(row[0]) for row in self.cw_rset)
        rql = ('Any R, D, DUR, WO, DESCR, S, A, SN, RT, WT ORDERBY D DESC '
               'WHERE '
               '   A is Activity, A done_by R, R title RT, '
               '   A diem D, A duration DUR, '
               '   A done_for WO, WO title WT, '
               '   A description DESCR, A in_state S, S name SN, A eid IN (%s)' % eids)
        if showresource:
            displaycols = range(7)
            headers.insert(0, display_name(self._cw, 'Resource'))
        else: # skip resource column if asked to
            displaycols = range(1, 7)
        rset = self._cw.execute(rql)
        self.wview('editable-table', rset, 'null', #subvid='tablecontext',
                   displayfilter=True, displayactions=False,
                   headers=headers, displaycols=displaycols)


class GenericActivityTable(tableview.EditableTableView):
    __regid__ = 'generic-activitytable'
    __select__ = multi_columns_rset()
    title = _('activitytable')

    def call(self, title=None):
        labels = self.columns_labels()
        labels[0] = u'edit'
        strio = UStringIO()
        self.paginate(self, w=strio.write, page_size=20)
        super(GenericActivityTable, self).call(
            #subvid='tablecontext', headers=headers,
            displayfilter=True, displayactions=False, actions=())
        self.w(strio.getvalue())


class ActivityCalendarItemView(calendar.CalendarItemView):
    __select__ = implements('Activity')

    def cell_call(self, row, col):
        activity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s">%s %s</a>' % (xml_escape(activity.absolute_url()),
                                            xml_escape(activity.done_for[0].dc_long_title()),
                                            activity.duration))


class ValidateActivitiesAction(action.Action):
    __regid__ = 'movetonext'
    __select__ = (action.Action.__select__
                  & match_user_groups('managers')
                  & implements('Activity')
                  & score_entity(lambda x: x.state == 'pending'))

    category = 'mainactions'
    title = _('validate activities')

    def url(self):
        if self.cw_row is None:
            eids = [row[0] for row in self.cw_rset]
        else:
            eids = (self.cw_rset[self.cw_row][self.cw_col or 0],)
        def validate_cb(req, eids):
            for eid in eids:
                entity = req.entity_from_eid(eid, 'Activity')
                entity.fire_transition('validate')
        msg = self._cw._('activities validated')
        return self._cw.user_callback(validate_cb, (eids,), msg=msg)
