from cubicweb.selectors import implements
from cubicweb.web.views import autoform
from cubicweb.web import INTERNAL_FIELD_VALUE, uicfg, formfields as ff
from cubicweb.web.formwidgets import HiddenInput

_afs = uicfg.autoform_section
_afs.tag_attribute(('WorkOrder', 'progress_target'), 'main', 'hidden')
_afs.tag_attribute(('WorkOrder', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('WorkOrder', 'progress_done'), 'main', 'hidden')
_afs.tag_subject_of(('Resource', 'use_calendar', '*'), 'main', 'inlined')

_affk = uicfg.autoform_field_kwargs


def tp_periods_choices(form, field, limit=None):
    #voc = self.object_relation_vocabulary(rtype, limit)
    if form._cw.form.get('vid') == 'holidays_form':
        rset = form._cw.execute("Any C WHERE R use_calendar CU, CU use_calendar C, "
                                "R euser U, U eid %(u)s", {'u':form._cw.user.eid})
        return sorted((v.view('combobox'), v.eid)
                      for v in rset.entities())
    return field.__class__.choices(field, form, limit=limit)
_affk.tag_object_of(('*', 'periods', 'Timeperiod'),
                    {'choices': tp_periods_choices})

def tp_day_type_choices(form, field, limit=None):
    voc = field.__class__.choices(field, form, limit=limit)
    if form._cw.form.get('vid') == 'holidays_form':
        voc = [item for item in voc
               if item[0] in form.conges_days]
    return voc
_affk.tag_subject_of(('Timeperiod', 'day_type', '*'),
                     {'choices': tp_day_type_choices})



def activity_done_by_choices(form, field, limit=None):
    user = form._cw.user
    entity = form.edited_entity
    # managers can edit the done_by relation as they wish
    if user.is_in_group('managers'):
        rql = 'Any R,T '
        if limit is not None:
            rql += 'LIMIT %s ' % limit
        rql += 'WHERE R is Resource, R title T'
        return sorted((entity.view('combobox'), entity.eid)
                      for entity in form._cw.execute(rql).entities())
    # users can't edit an existing done_by relation
    if entity.has_eid():
        return []
    rql = 'Any R,T WHERE R euser U, R title T, U eid %(u)s'
    res = form._cw.execute(rql, {'u': user.eid}).get_entity(0, 0)
    return [(res.view('combobox'), res.eid)]
_affk.tag_subject_of(('Activity', 'done_by', '*'),
                     {'choices': activity_done_by_choices})

def activity_done_for_choices(form, field, limit=None):
    req = form._cw
    user = req.user
    entity = form.edited_entity
    options = []
    # managers can edit the done_for relation as they wish
    if user.is_in_group('managers'):
        rql = ('Any WO,T %s WHERE WO is WorkOrder, WO title T, '
               'WO in_state S, S name "in progress"')
        if limit is None:
            rql = rql % ''
        else:
            rql = rql % (' LIMIT %s' % limit)
        rset = form._cw.execute(rql)
        if rset:
            options += [(req._('work orders in progress'), None)]
            options += sorted((entity.view('combobox'), entity.eid)
                              for entity in rset.entities())
        else:
            options += [(req._('no work orders in progress'),
                         INTERNAL_FIELD_VALUE)]
        return options
    # for new entities, users will only see their matching resource
    rql = ('DISTINCT Any WO,T WHERE WO is WorkOrder, WO title T, '
           'WO in_state S, S name "in progress", '
           'WO todo_by R, R euser U')
    rset = req.execute(rql+', U eid %(u)s', {'u': req.user.eid})
    if rset:
        options += [(req._('your work orders'), None)]
        options += sorted((entity.view('combobox'), entity.eid)
                          for entity in rset.entities())
    rset = req.execute(rql+', NOT U eid %(u)s', {'u': req.user.eid})
    if rset:
        options += [(req._('other work orders'), None)]
        options += sorted((entity.view('combobox'), entity.eid)
                          for entity in rset.entities())
    if not options:
        options += [(req._('no work orders'),
                     INTERNAL_FIELD_VALUE)]
    return options
_affk.tag_subject_of(('Activity', 'done_for', '*'),
                     {'choices': activity_done_for_choices})
