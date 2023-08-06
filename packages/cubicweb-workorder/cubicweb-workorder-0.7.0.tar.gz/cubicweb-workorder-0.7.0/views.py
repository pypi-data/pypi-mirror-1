"""template-specific forms/views/actions/components"""

from cubicweb.web import uicfg

# Order
uicfg.primaryview_section.tag_subject_of(('Order', 'split_into', '*'),
                                         'relations')
uicfg.primaryview_section.tag_attribute(('Order', 'budget'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Order', 'progress_target'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Order', 'progress_done'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Order', 'progress_todo'), 'hidden')
uicfg.primaryview_display_ctrl.tag_subject_of(('Order', 'split_into', '*'),
                                              {'vid': 'ic_progress_table_view'})

uicfg.autoform_section.tag_attribute(('Order', 'budget'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('Order', 'progress_target'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('Order', 'progress_todo'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('Order', 'progress_done'), 'main', 'hidden')
uicfg.autoform_section.tag_subject_of(('Order', 'split_into', '*'), 'main', 'attributes')

# WorkOrder
uicfg.autoform_section.tag_attribute(('WorkOrder', 'progress_target'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('WorkOrder', 'progress_todo'), 'main', 'hidden')
uicfg.autoform_section.tag_attribute(('WorkOrder', 'progress_done'), 'main', 'hidden')
