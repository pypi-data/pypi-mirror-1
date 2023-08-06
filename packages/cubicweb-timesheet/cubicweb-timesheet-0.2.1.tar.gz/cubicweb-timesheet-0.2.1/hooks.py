# -*- coding: utf-8 -*-
"""
:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements
from cubicweb.server.hook import Hook, match_rtype

class ActivityProgressHook(Hook):
    __regid__ = 'timesheet_update_activity'
    __select__ = Hook.__select__ & implements('Activity')
    events = ('after_update_entity', )

    def __call__(self):
        self.entity.done_for[0].update_progress()

class DoneforProgressHook(Hook):
    __regid__ = 'timesheet_update_done_for'
    __select__ = Hook.__select__ & match_rtype('done_for')
    events = ('after_add_relation', 'after_delete_relation',)

    def __call__(self):
        self._cw.entity_from_eid(self.eidto).update_progress()

