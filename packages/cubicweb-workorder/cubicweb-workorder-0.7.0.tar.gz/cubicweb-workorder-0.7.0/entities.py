from datetime import date

from cubicweb.mixins import ProgressMixIn
from cubicweb.interfaces import IMileStone
from cubicweb.entities import AnyEntity, fetch_config

class Order(AnyEntity):
    __regid__ = 'Order'
    fetch_attrs, fetch_order = fetch_config(('title', 'date'))

    def update_progress(self):
        """callable only on the server side"""
        workorders = self.split_into
        self.budget = sum(wod.budget or 0 for wod in workorders)
        self.progress_target = sum(wod.progress_target or 0 for wod in workorders)
        self.progress_done = sum(wod.progress_done or 0 for wod in workorders)
        self.progress_todo = sum(wod.progress_todo or 0 for wod in workorders)
        self._cw.unsafe_execute('SET W budget %(budget)s, '
                                'W progress_target %(target)s, '
                                'W progress_done %(done)s, '
                                'W progress_todo %(todo)s '
                                'WHERE W eid %(eid)s',
                                {'eid': self.eid,
                                 'budget': self.budget,
                                 'target': self.progress_target,
                                 'done': self.progress_done,
                                 'todo': self.progress_todo},
                                'eid')

    def progress_info(self):
        return {'estimated': self.progress_target,
                'estimatedcorrected': self.progress_target,
                'done': self.progress_done,
                'todo': self.progress_todo,
                }

class WorkOrder(ProgressMixIn, AnyEntity):
    __regid__ = 'WorkOrder'
    __implements__ = AnyEntity.__implements__ + (IMileStone,)

    fetch_attrs, fetch_order = fetch_config(('title', 'description_format',
                                             'description', 'budget',
                                             'begin_date', 'end_date', 'in_state'))

    def dc_title(self):
        return self.title

    def dc_long_title(self):
        return u'%s - %s' % (self.order.dc_title(), self.title)

    @property
    def order(self):
        return self.reverse_split_into[0]

    def parent(self):
        return self.order

    ## IProgress interface ####################################################
    parent_type = 'Order'
    def get_main_task(self):
        return self.order

    def initial_prevision_date(self):
        """returns the initial expected end of the milestone"""
        return date.today()

    def eta_date(self):
        """returns expected date of completion based on what remains
        to be done
        """
        return date.today()

    def completion_date(self):
        """returns date on which the subtask has been completed"""
        return date.today()

    def contractors(self):
        """returns the list of persons supposed to work on this task"""
        return []

    def in_progress(self):
        return self.state == u'in progress'

    def _compute_progress(self):
        self.progress_target = self.budget or 0
        self.progress_done = 0
        self.progress_todo = max(0, self.progress_target - self.progress_done)

    def update_progress(self):
        """callable only on the server side"""
        self._compute_progress()
        self._cw.unsafe_execute('SET W progress_target %(target)s, '
                                'W progress_done %(done)s, '
                                'W progress_todo %(todo)s '
                                'WHERE W eid %(eid)s',
                                {'eid': self.eid,
                                 'target': self.progress_target,
                                 'done': self.progress_done,
                                 'todo': self.progress_todo},
                                'eid')
        if self.reverse_split_into:
            self.order.update_progress()
        else:
            self.debug('should have a order as parent')

    def progress_info(self):
        return {'estimated': self.progress_target,
                'estimatedcorrected': self.progress_target,
                'done': self.progress_done,
                'todo': self.progress_todo,
                }

