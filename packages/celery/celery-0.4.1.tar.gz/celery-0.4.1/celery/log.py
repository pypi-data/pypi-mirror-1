"""celery.log"""
import os
import sys
import time
import logging
from celery.conf import LOG_FORMAT, DAEMON_LOG_LEVEL


def setup_logger(loglevel=DAEMON_LOG_LEVEL, logfile=None, format=LOG_FORMAT,
        **kwargs):
    """Setup the ``multiprocessing`` logger. If ``logfile`` is not specified,
    ``stderr`` is used.

    Returns logger object.
    """
    import multiprocessing
    logger = multiprocessing.get_logger()
    logger.setLevel(loglevel)
    if logger.handlers:
        return logger
    if logfile:
        if hasattr(logfile, "write"):
            log_file_handler = logging.StreamHandler(logfile)
        else:
            log_file_handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(format)
        log_file_handler.setFormatter(formatter)
        logger.addHandler(log_file_handler)
    else:
        multiprocessing.log_to_stderr()
    return logger


def emergency_error(logfile, message):
    """Emergency error logging, for when there's no standard file
    descriptors open because the process has been daemonized or for
    some other reason."""
    logfh_needs_to_close = False
    if not logfile:
        logfile = sys.stderr
    if hasattr(logfile, "write"):
        logfh = logfile
    else:
        logfh = open(logfile, "a")
        logfh_needs_to_close = True
    logfh.write("[%(asctime)s: FATAL/%(pid)d]: %(message)s\n" % {
                    "asctime": time.asctime(),
                    "pid": os.getpid(),
                    "message": message})
    if logfh_needs_to_close:
        logfh.close()
