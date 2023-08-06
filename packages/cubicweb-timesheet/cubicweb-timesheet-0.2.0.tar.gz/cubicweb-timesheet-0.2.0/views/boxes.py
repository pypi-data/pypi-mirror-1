"""gingouz specific boxes

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.web.box import BoxTemplate
from cubicweb.web.htmlwidgets import BoxWidget, BoxHtml

class ActivitiesBox(BoxTemplate):
    """display a box with an activity calendar"""
    __regid__ = 'activities_box'

    visible = True # enabled by default
    title = _('My activities')
    order = 10

    def call(self, view=None, **kwargs):
        title = self._cw._(self.title)
        url = self._cw.build_url(rql="Any C WHERE R use_calendar CU, CU use_calendar C, "
                                 "R euser U, U eid %s" % self._cw.user.eid)
        title += '&nbsp;&nbsp;<a href="%s" title="%s"><img alt="calendar icon" src="data/office-calendar.png"/> </a>' % (
            xml_escape(url), self._cw._('see my calendars'))
        box = BoxWidget(title, self.__regid__, islist=False,
                        escape=False)
        html = self._cw.user.view('user_activity_calendar', calid='selftid')
        box.append(BoxHtml(html))
        box.render(self.w)


class MyActionsBox(BoxTemplate):
    """display a box with util links"""
    __regid__ = 'my_actions_box'

    visible = True # enabled by default
    title = _('Mes actions')
    order = 2

    def call(self, view=None, **kwargs):
        req = self._cw
        title = req._(self.title)
        box = BoxWidget(title, self.__regid__, islist=False)
        html = u'<div class="boxContent"><ul class="sideBox">'
        res = req.user.default_resource
        if res:
            url = xml_escape(res.absolute_url())
            html += u'<li><a class="boxManage" href="%s">%s</a></li>' % (url, req._('my_space'))
        else:
            html += '<li>%s</li>' % (req._('no resource for user %s') % req.user.login)
        # select default calendar for currently logged user
        cal = req.execute('Any C ORDERBY T DESC LIMIT 1 WHERE R use_calendar CU, '
                          'CU use_calendar C, C title T, R euser U, U eid %(u)s',
                          {'u': req.user.eid})
        if cal:
            url = xml_escape(req.build_url('view', etype='Timeperiod', vid='creation',
                                           __linkto='periods:%s:object' % cal[0][0]))
            html += u'<li><a class="boxManage" href="%s">%s</a></li>' % (url, req._('ask_off_days'))
        html += u'</ul></div>'
        box.append(BoxHtml(html))
        box.render(self.w)
