"""template-specific forms/views/actions/components"""
from cubicweb.web import uicfg, formwidgets as fw
from cubicweb.web.views.urlrewrite import SimpleReqRewriter, rgx

_afs = uicfg.autoform_section
_afs.tag_attribute(('WorkOrder', 'progress_target'), 'main', 'hidden')
_afs.tag_attribute(('WorkOrder', 'progress_todo'), 'main', 'hidden')
_afs.tag_attribute(('WorkOrder', 'progress_done'), 'main', 'hidden')
_afs.tag_subject_of(('WorkOrder', 'uses_technology', '*'), 'main', 'attributes')
_afs.tag_subject_of(('WorkOrder', 'uses_technology', '*'), 'muledit', 'attributes')
_afs.tag_subject_of(('Resource', 'use_calendar', '*'), 'main', 'inlined')
# XXX should not be always hidden
uicfg.autoform_field_kwargs.tag_subject_of(('Activity', 'done_by', '*'),
                                           {'widget': fw.HiddenInput})


uicfg.primaryview_section.tag_object_of(('*', 'use_calendar', 'Calendar'), 'hidden')

uicfg.actionbox_appearsin_addmenu.tag_subject_of(('Resource', 'has_vacation', '*'), True)
uicfg.actionbox_appearsin_addmenu.tag_object_of(('Resource', 'euser', 'CWUser'), True)


class TimesheetReqRewriter(SimpleReqRewriter):
    rules = [
        (rgx('/activities/(.*?)/(\d{4})-(\d\d)-(\d\d)'),
         dict(year=r'\2', month=r'\3', day=r'\4',
              vid='activities-submit',
              rql=r'Any A WHERE A is Activity, A diem "\2-\3-\4", A done_by R, '
              r'R euser U, U login "\1"')),
        ]
