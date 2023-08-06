import os
import sys
import time
import datetime
import logging
from interfaces import IAmInstalled


DEFAULT_MIN_LOG_TIME = "0"
MIN_LOG_TIME = int(os.environ.get("MIN_LOG_TIME", DEFAULT_MIN_LOG_TIME))

DEFAULT_LOGNAME = "/tmp/requestlet.txt"
LOGNAME= os.environ.get("REQUESTLET_LOGNAME", DEFAULT_LOGNAME)

logger = logging.getLogger("requestlet")

def initialize(context):
    fhd = logging.handlers.RotatingFileHandler(LOGNAME, maxBytes=5*1024*1024, backupCount=5) # will make about 10k lines per file.
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    fhd.setLevel(logging.INFO)
    fhd.setFormatter(formatter)
    logger.addHandler(fhd)

    logger.debug("LOGNAME=%s" % LOGNAME)
    logger.debug("MIN_LOG_TIME=%s" % MIN_LOG_TIME)

def mark_start_request(obj, event):
    # IAmInstalled is not available here (seems like ISiteRoot marks the request).
    event.request.requestlet_time_start = time.time()

def meminfo():
    # vm info
    return [x for x in file('/proc/%d/status' % os.getpid()).readlines() if x.startswith("VmSize")][0].split()[1]

def log_request_time(event):
    # only do something if we are installed.
    if not IAmInstalled.providedBy(event.request):
        return

    request = event.request

    if getattr(request, "requestlet_time_start", None):
        elapsed = time.time() - request.requestlet_time_start

        if elapsed >= MIN_LOG_TIME:
            url = "%s%s" % (request.environ["HTTP_HOST"], request.environ["PATH_INFO"])
            method = request.environ["REQUEST_METHOD"]
            rinfo = " ".join(["%s='%s'" % (k,v) for k,v in request.response.headers.items()])
            mem_info = meminfo()
            logger.debug("ELAPSED %.3fs (min %ss) METHOD %s RAM %skB URL: %s rinfo: %s" % (elapsed, MIN_LOG_TIME, method, mem_info, url, rinfo))

