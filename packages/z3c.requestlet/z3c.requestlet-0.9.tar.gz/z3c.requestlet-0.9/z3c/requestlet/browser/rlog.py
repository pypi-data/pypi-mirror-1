from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from time import mktime
import datetime

from z3c.requestlet.rlog import LOGNAME

class RLog(BrowserView):
    """
    rlog browser view
    generate graphs ;)
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.min_memory = None
        self.max_memory = 0
        self.data = []
        self.first_timestamp = self.last_timestamp = None

        self.update()

    def update(self):
        # fetch info
        f = file(LOGNAME)
        for line in f.readlines():
            if 'ELAPSED' not in line:
                continue
            date, time, _, _, _, elapsed, _, _, _, _, method, meminfo, _, uri = line.split()[:14]
            memory = int(meminfo[:-2])
            y, m, d = date.split("-")
            h, i, s =  time.split(",")[0].split(":")

            timestamp = mktime(datetime.datetime(int(y), int(m), int(d), int(h), int(i), int(s)).timetuple())

            timestamp = round(timestamp, 2)

            if not self.first_timestamp:
                self.first_timestamp = timestamp

            self.data.append("[%s,%s,'%s']" % (timestamp, memory, uri))
            if self.min_memory is None:
                self.min_memory = memory
            elif memory < self.min_memory:
                self.min_memory = memory

            if memory > self.max_memory:
                self.max_memory = memory

            self.last_timestamp = timestamp

    def data_array(self):
        return "[%s]" % ', '.join([str(x) for x in self.data])

    def title(self):
        date = datetime.datetime.fromtimestamp(self.first_timestamp)
        title = date.strftime('%Y/%m/%d %H:%M:%S')
        seconds = self.last_timestamp - self.first_timestamp
        if seconds < 60:
            title += ' (%d seconds)' % seconds
        elif seconds < 60*60:
            title += ' (%.1f minutes)' % (seconds/60.0)
        elif seconds < 60*60*24:
            title += ' (%.1f hours)' % (seconds/60.0/60.0)
        else:
            title += ' (%.1f days)' % (seconds/60.0/60/24)
        
        return title
