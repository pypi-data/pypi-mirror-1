#!/usr/bin/env python
"""celeryd

.. program:: celeryd

.. cmdoption:: -c, --concurrency

    Number of child processes processing the queue.

.. cmdoption:: -f, --logfile

    Path to log file. If no logfile is specified, ``stderr`` is used.

.. cmdoption:: -l, --loglevel

    Logging level, choose between ``DEBUG``, ``INFO``, ``WARNING``,
    ``ERROR``, ``CRITICAL``, or ``FATAL``.

.. cmdoption:: -p, --pidfile

    Path to pidfile.

.. cmdoption:: -w, --wakeup-after

    If the queue is empty, this is the time *in seconds* the
    daemon sleeps until it wakes up to check if there's any
    new messages on the queue.

.. cmdoption:: -d, --daemon

    Run in the background as a daemon.

"""
import os
import sys
sys.path.append(os.getcwd())
django_project_dir = os.environ.get("DJANGO_PROJECT_DIR")
if django_project_dir:
    sys.path.append(django_project_dir)

from django.conf import settings
from celery.platform import PIDFile, daemonize, remove_pidfile
from celery.log import setup_logger, emergency_error
from celery.conf import LOG_LEVELS, DAEMON_LOG_FILE, DAEMON_LOG_LEVEL
from celery.conf import DAEMON_CONCURRENCY, DAEMON_PID_FILE
from celery.conf import QUEUE_WAKEUP_AFTER
from celery import discovery
from celery.worker import TaskDaemon
import traceback
import optparse
import atexit


def main(concurrency=DAEMON_CONCURRENCY, daemon=False,
        loglevel=DAEMON_LOG_LEVEL, logfile=DAEMON_LOG_FILE,
        pidfile=DAEMON_PID_FILE, queue_wakeup_after=QUEUE_WAKEUP_AFTER):
    if settings.DATABASE_ENGINE == "sqlite3" and concurrency > 1:
        import warnings
        warnings.warn("The sqlite3 database engine doesn't support "
                "concurrency. We'll be using a single process only.",
                UserWarning)
        concurrency = 1
    if daemon:
        sys.stderr.write("Launching celeryd in the background...\n")
        pidfile_handler = PIDFile(pidfile)
        pidfile_handler.check()
        daemonize(pidfile=pidfile_handler)
        atexit.register(remove_pidfile, pidfile)
    else:
        logfile = None # log to stderr when not running as daemon.

    discovery.autodiscover()
    celeryd = TaskDaemon(concurrency=concurrency,
                               loglevel=loglevel,
                               logfile=logfile,
                               queue_wakeup_after=queue_wakeup_after)
    try:
        celeryd.run()
    except Exception, e:
        emergency_error(logfile, "celeryd raised exception %s: %s\n%s" % (
                            e.__class__, e, traceback.format_exc()))


def parse_options(arguments):
    parser = optparse.OptionParser()
    parser.add_option('-c', '--concurrency', default=DAEMON_CONCURRENCY,
            action="store", dest="concurrency", type="int",
            help="Number of child processes processing the queue.")
    parser.add_option('-f', '--logfile', default=DAEMON_LOG_FILE,
            action="store", dest="logfile",
            help="Path to log file.")
    parser.add_option('-l', '--loglevel', default=DAEMON_LOG_LEVEL,
            action="store", dest="loglevel",
            help="Choose between DEBUG/INFO/WARNING/ERROR/CRITICAL/FATAL.")
    parser.add_option('-p', '--pidfile', default=DAEMON_PID_FILE,
            action="store", dest="pidfile",
            help="Path to pidfile.")
    parser.add_option('-w', '--wakeup-after', default=QUEUE_WAKEUP_AFTER,
            action="store", dest="queue_wakeup_after",
            help="If the queue is empty, this is the time *in seconds* the "
                 "daemon sleeps until it wakes up to check if there's any "
                 "new messages on the queue.")
    parser.add_option('-d', '--daemon', default=False,
            action="store_true", dest="daemon",
            help="Run in the background as a daemon.")
    options, values = parser.parse_args(arguments)
    if not isinstance(options.loglevel, int):
        options.loglevel = LOG_LEVELS[options.loglevel.upper()]
    return options

if __name__ == "__main__":
    options = parse_options(sys.argv[1:])
    main(concurrency=options.concurrency,
         daemon=options.daemon,
         logfile=options.logfile,
         loglevel=options.loglevel,
         pidfile=options.pidfile,
         queue_wakeup_after=options.queue_wakeup_after)
