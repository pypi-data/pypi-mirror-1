#!/usr/bin/python

import os
import datetime
import marshal
from time import mktime

def generate(file_name):
    
    html = open(os.path.join(os.path.dirname(__file__), 'template.html')).read()
     
    data = []
    first_timestamp = last_timestamp = None
    min_memory = None
    max_memory = 0
   
    f = file(file_name)
    for line in f.readlines():
        if 'ELAPSED' not in line:
            continue
        date, time, _, _, _, elapsed, _, _, _, _, method, meminfo, _, uri = line.split()[:14]
        memory = int(meminfo[:-2])
        y, m, d = date.split("-")
        h, i, s =  time.split(",")[0].split(":")

        timestamp = mktime(datetime.datetime(int(y), int(m), int(d), int(h), int(i), int(s)).timetuple()) # XXX

        timestamp = round(timestamp, 2)

        if not first_timestamp:
            first_timestamp = timestamp

        data.append("[%s,%s,'%s']" % (timestamp, memory, uri))
        if min_memory is None:
            min_memory = memory
        elif memory < min_memory:
            min_memory = memory
            
        if memory > max_memory:
            max_memory = memory

        last_timestamp = timestamp
    
    html = html.replace('{{max_value}}', str(max_memory))
    html = html.replace('{{min_value}}', str(min_memory))
    html = html.replace('{{data_array}}', '[%s]' % ', '.join([str(x) for x in data]))
    
    title = _generate_title(first_timestamp, last_timestamp)
    html = html.replace('{{title}}', title)
    
    save_dir = _title2foldername(title)
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    open(os.path.join(save_dir, 'index.html'),'w').write(html)
    
    report_file = os.path.join(save_dir, 'index.html')
    print report_file
    return report_file


def _generate_title(first_timestamp, last_timestamp):
    date = datetime.datetime.fromtimestamp(first_timestamp)
    title = date.strftime('%Y/%m/%d %H:%M:%S')
    seconds = last_timestamp - first_timestamp
    if seconds < 60:
        title += ' (%d seconds)' % seconds
    elif seconds < 60*60:
        title += ' (%.1f minutes)' % (seconds/60.0)
    elif seconds < 60*60*24:
        title += ' (%.1f hours)' % (seconds/60.0/60.0)
    else:
        title += ' (%.1f days)' % (seconds/60.0/60/24)
    
    return title
    
def _title2foldername(title):
    title = title.replace(':','.')
    title = title.replace('(',' ').replace(')','')
    title = title.replace(' ','_')
    title = title.replace('/','-')
    return title


if __name__=='__main__':
    import sys
    generate("/tmp/requestlet.txt")


