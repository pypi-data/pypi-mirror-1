============================
 Frequently Asked Questions
============================

Questions
=========

MySQL is throwing deadlock errors, what can I do?
-------------------------------------------------

**Answer:** MySQL has default isolation level set to ``REPEATABLE-READ``,
if you don't really need that, set it to ``READ-COMMITTED``.
You can do that by adding the following to your ``my.cnf``::

    [mysqld]
    transaction-isolation = READ-COMMITTED

For more information about InnoDBs transaction model see `MySQL - The InnoDB
Transaction Model and Locking`_ in the MySQL user manual.

(Thanks to Honza Kral and Anton Tsigularov for this solution)

.. _`MySQL - The InnoDB Transaction Model and Locking`: http://dev.mysql.com/doc/refman/5.1/en/innodb-transaction-model.html

celeryd is not doing anything, just hanging
--------------------------------------------

**Answer:** See `MySQL is throwing deadlock errors, what can I do?`_.
            or `Why is Task.delay/apply\* just hanging?`.

Why is Task.delay/apply\* just hanging?`
----------------------------------------

**Answer:** :mod:`amqplib` hangs if it isn't able to authenticate to the
AMQP server, so make sure you are able to access the configured vhost using
the user and password.

Why won't celeryd run on FreeBSD?
---------------------------------

**Answer:** multiprocessing.Pool requires a working POSIX semaphore
implementation which isn't enabled in FreeBSD by default. You have to enable
POSIX semaphores in the kernel and manually recompile multiprocessing.

I'm having ``IntegrityError: Duplicate Key`` errors. Why?
----------------------------------------------------------

**Answer:** See `MySQL is throwing deadlock errors, what can I do?`_.
Thanks to howsthedotcom.

Why won't my Task run?
----------------------

**Answer:** Did you register the task in the applications ``tasks.py`` module?
(or in some other module Django loads by default, like ``models.py``?).
Also there might be syntax errors preventing the tasks module being imported.

You can find out if the celery daemon is able to run the task by executing the
task manually:

    >>> from myapp.tasks import MyPeriodicTask
    >>> MyPeriodicTask.delay()

Watch celery daemons logfile (or output if not running as a daemon), to see
if it's able to find the task, or if some other error is happening.

Why won't my Periodic Task run?
-------------------------------

**Answer:** See `Why won't my Task run?`_.

How do I discard all waiting tasks?
------------------------------------

**Answer:** Use ``celery.task.discard_all()``, like this:

    >>> from celery.task import discard_all
    >>> discard_all()
    1753

The number ``1753`` is the number of messages deleted.

You can also start celeryd with the ``--discard`` argument which will
accomplish the same thing.

I've discarded messages, but there are still messages left in the queue?
------------------------------------------------------------------------

**Answer:** Tasks are acknowledged (removed from the queue) as soon
as they are actually executed. After the worker has received a task, it will
take some time until it is actually executed, especially if there are a lot
of tasks already waiting for execution. Messages that are not acknowledged are
hold on to by the worker until it closes the connection to the broker (AMQP
server). When that connection is closed (e.g because the worker was stopped)
the tasks will be re-sent by the broker to the next available worker (or the
same worker when it has been restarted), so to properly purge the queue of
waiting tasks you have to stop all the workers, and then discard the tasks
using ``discard_all``.

Can I send some tasks to only some servers?
--------------------------------------------

**Answer:** As of now there is only one use-case that works like this,
and that is tasks of type ``A`` can be sent to servers ``x`` and ``y``,
while tasks of type ``B`` can be sent to server ``z``. One server can't
handle more than one routing_key, but this is coming in a later release.

Say you have two servers, ``x``, and ``y`` that handles regular tasks,
and one server ``z``, that only handles feed related tasks, you can use this
configuration:

    * Servers ``x`` and ``y``: settings.py:

    .. code-block:: python

        AMQP_SERVER = "rabbit"
        AMQP_PORT = 5678
        AMQP_USER = "myapp"
        AMQP_PASSWORD = "secret"
        AMQP_VHOST = "myapp"

        CELERY_AMQP_CONSUMER_QUEUE = "regular_tasks"
        CELERY_AMQP_EXCHANGE = "tasks"
        CELERY_AMQP_PUBLISHER_ROUTING_KEY = "task.regular"
        CELERY_AMQP_CONSUMER_ROUTING_KEY = "task.#"
        CELERY_AMQP_EXCHANGE_TYPE = "topic"

    * Server ``z``: settings.py:

    .. code-block:: python

        AMQP_SERVER = "rabbit"
        AMQP_PORT = 5678
        AMQP_USER = "myapp"
        AMQP_PASSWORD = "secret"
        AMQP_VHOST = "myapp"
        
        CELERY_AMQP_EXCHANGE = "tasks"
        CELERY_AMQP_PUBLISHER_ROUTING_KEY = "task.regular"
        CELERY_AMQP_EXCHANGE_TYPE = "topic"
        # This is the settings different for this server:
        CELERY_AMQP_CONSUMER_QUEUE = "feed_tasks"
        CELERY_AMQP_CONSUMER_ROUTING_KEY = "feed.#"

Now to make a Task run on the ``z`` server you need to set its
``routing_key`` attribute so it starts with the words ``"task.feed."``:

.. code-block:: python

    from feedaggregator.models import Feed
    from celery.task import Task

    class FeedImportTask(Task):
        name = "import_feed"
        routing_key = "feed.importer"

        def run(self, feed_url):
            # something importing the feed
            Feed.objects.import_feed(feed_url)


You can also override this using the ``routing_key`` argument to
:func:`celery.task.apply_async`:

    >>> from celery.task import apply_async
    >>> from myapp.tasks import RefreshFeedTask
    >>> apply_async(RefreshFeedTask, args=["http://cnn.com/rss"],
    ...             routing_key="feed.importer")

