import multiprocessing
import time
from multiprocessing import TimeoutError

JOIN_TIMEOUT = 2
CHECK_INTERVAL = 2
MAX_RESTART_FREQ = 3
MAX_RESTART_FREQ_TIME = 10


class MaxRestartsExceededError(Exception):
    """Restarts exceeded the maximum restart frequency."""


class OFASupervisor(object):
    """Process supervisor using the `one_for_all`_ strategy.

    .. _`one_for_all`:
        http://erlang.org/doc/design_principles/sup_princ.html#5.3.2

    However, instead of registering a list of processes, you have one
    process which runs a pool. Makes for an easy implementation.

    :param target: see :attr:`target`.
    :param args: see :attr:`args`.
    :param kwargs: see :attr:`kwargs`.
    :param max_restart_freq: see :attr:`max_restart_freq`.
    :param max_restart_freq_time: see :attr:`max_restart_freq_time`.
    :param check_interval: see :attr:`max_restart_freq_time`.

    .. attribute:: target

        The target callable to be launched in a new process.

    .. attribute:: args

        The positional arguments to apply to :attr:`target`.

    .. attribute:: kwargs

        The keyword arguments to apply to :attr:`target`.

    .. attribute:: max_restart_freq

        Limit the number of restarts which can occur in a given time interval.

        The max restart frequency is the number of restarts that can occur
        within the interval :attr:`max_restart_freq_time`.

        The restart mechanism prevents situations where the process repeatedly
        dies for the same reason. If this happens both the process and the
        supervisor is terminated.

    .. attribute:: max_restart_freq_time

        See :attr:`max_restart_freq`.

    .. attribute:: check_interval

        The time in seconds, between process pings.

    """
    Process = multiprocessing.Process

    def __init__(self, target, args=None, kwargs=None,
            max_restart_freq=MAX_RESTART_FREQ,
            join_timeout=JOIN_TIMEOUT,
            max_restart_freq_time=MAX_RESTART_FREQ_TIME,
            check_interval=CHECK_INTERVAL):
        self.target = target
        self.join_timeout = join_timeout
        self.args = args or []
        self.kwargs = kwargs or {}
        self.check_interval = check_interval
        self.max_restart_freq = max_restart_freq
        self.max_restart_freq_time = max_restart_freq_time
        self.restarts_in_frame = 0

    def start(self):
        """Launches the :attr:`target` in a seperate process and starts
        supervising it."""
        target = self.target

        def _start_supervised_process():
            """Start the :attr:`target` in a new process."""
            process = self.Process(target=target,
                                   args=self.args, kwargs=self.kwargs)
            process.start()
            return process

        def _restart(process):
            """Terminate the process and restart."""
            process.join(timeout=self.join_timeout)
            process.terminate()
            self.restarts_in_frame += 1
            process = _start_supervised_process()

        process = _start_supervised_process()
        try:
            restart_frame = 0
            while True:
                if restart_frame > self.max_restart_freq_time:
                    if self.restarts_in_frame >= self.max_restart_freq:
                        raise MaxRestartsExceededError(
                                "Supervised: Max restart frequency reached")
                restart_frame = 0
                self.restarts_in_frame = 0

                try:
                    proc_is_alive = process.is_alive()
                except TimeoutError:
                    proc_is_alive = False

                if not proc_is_alive:
                    _restart(process)

                time.sleep(self.check_interval)
                restart_frame += self.check_interval
        finally:
            process.join()
