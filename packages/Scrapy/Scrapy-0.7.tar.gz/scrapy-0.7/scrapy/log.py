""" 
Scrapy logging facility

See documentation in docs/topics/logging.rst
"""
import sys
from traceback import format_exc

from twisted.python import log
from scrapy.xlib.pydispatch import dispatcher

from scrapy.conf import settings
from scrapy.utils.python import unicode_to_str
 
# Logging levels
SILENT, CRITICAL, ERROR, WARNING, INFO, DEBUG = range(6)
level_names = {
    0: "SILENT",
    1: "CRITICAL",
    2: "ERROR",
    3: "WARNING",
    4: "INFO",
    5: "DEBUG",
}

BOT_NAME = settings['BOT_NAME']

# signal sent when log message is received
# args: message, level, domain
logmessage_received = object()

# default logging level
log_level = DEBUG

started = False

def start(logfile=None, loglevel=None, logstdout=None):
    """Initialize and start logging facility"""
    global log_level, started

    # set loglevel
    loglevel = loglevel or settings['LOG_LEVEL'] or settings['LOGLEVEL']
    log_level = globals()[loglevel] if loglevel else DEBUG
    if started or not settings.getbool('LOG_ENABLED'):
        return
    started = True

    # set log observer
    if log.defaultObserver: # check twisted log not already started
        logfile = logfile or settings['LOG_FILE'] or settings['LOGFILE']
        if logstdout is None:
            logstdout = settings.getbool('LOG_STDOUT')

        file = open(logfile, 'a') if logfile else sys.stderr
        log.startLogging(file, setStdout=logstdout)

def msg(message, level=INFO, component=BOT_NAME, domain=None):
    """Log message according to the level"""
    if level > log_level:
        return
    dispatcher.send(signal=logmessage_received, message=message, level=level, \
        domain=domain)
    system = domain if domain else component
    msg_txt = unicode_to_str("%s: %s" % (level_names[level], message))
    log.msg(msg_txt, system=system)

def exc(message, level=ERROR, component=BOT_NAME, domain=None):
    message = message + '\n' + format_exc()
    msg(message, level, component, domain)

def err(_stuff=None, _why=None, **kwargs):
    if ERROR > log_level:
        return
    domain = kwargs.pop('domain', None)
    component = kwargs.pop('component', BOT_NAME)
    kwargs['system'] = domain if domain else component
    if _why:
        _why = unicode_to_str("ERROR: %s" % _why)
    log.err(_stuff, _why, **kwargs)
