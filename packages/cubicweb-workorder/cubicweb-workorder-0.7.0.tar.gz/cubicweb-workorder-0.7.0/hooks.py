# -*- coding: utf-8 -*-
"""
:organization: Logilab
:copyright: 2009-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements
from cubicweb.server.hook import Hook, match_rtype

class WorkOrderProgressHook(Hook):

    __regid__ = 'workorder_progress_hook'
    __select__ = Hook.__select__ & implements('WorkOrder')
    events = ('before_add_entity', 'before_update_entity', )

    def __call__(self):
        self.entity._compute_progress()

class SplitIntoProgressHook1(Hook):

    __regid__ = 'split_into_progress_hook1'
    __select__ = Hook.__select__ & implements('WorkOrder')
    events = ('after_update_entity', )

    def __call__(self):
        orders = self.entity.reverse_split_into
        if orders:
            orders[0].update_progress()

class SplitIntoProgressHook2(Hook):

    __regid__ = 'split_into_progress_hook2'
    __select__ = Hook.__select__ & match_rtype('split_into')
    events = ('after_add_relation', 'after_delete_relation', )

    def __call__(self):
        order = self._cw.entity_from_eid(self.eidfrom)
        order.update_progress()

