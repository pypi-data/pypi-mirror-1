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
from cubicweb.interfaces import ICalendarViews, ICalendarable

class Event(AnyEntity):
    __regid__ = 'Event'
    __implements__ = (ICalendarViews, ICalendarable)

    fetch_attrs, fetch_order = fetch_config(['title'])

    @property
    def start(self):
        return self.diem

    @property
    def stop(self):
        return self.end_date

    def dc_title(self):
        return self.title

    def matching_dates(self, begin, end):
        """calendar views interface"""
        start = self.diem
        stop = self.end_date
        if not start and not stop:
            return []
        elif start and not stop:
            stop = start+1
        elif stop and not start:
            start = stop-1
        return list(date_range(start, stop))
