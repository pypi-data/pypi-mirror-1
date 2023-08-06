"""entity classes for task entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import date

from logilab.common.date import date_range

from cubicweb.mixins import TreeMixIn
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ICalendarViews

class Task(TreeMixIn, AnyEntity):
    """customized class for Task entities

    XXX graph structure, not tree structure
    """
    __regid__ = 'Task'
    __implements__ = (ICalendarViews,)
    fetch_attrs, fetch_order = fetch_config(['title'])
    tree_attribute = 'depends_on'
    parent_target = 'object'
    children_target = 'subject'

    def dc_title(self):
        return self.title

    def matching_dates(self, begin, end):
        """calendar views interface"""
        start = self.start
        stop = self.stop
        cost = self.cost
        if not start and not stop:
            return []
        elif start and not stop:
            if cost:
                stop = start + cost/4
            else:
                stop = start
        elif stop and not start:
            if cost:
                start = stop - cost/4
            else:
                start = stop
        return list(date_range(start, stop))

