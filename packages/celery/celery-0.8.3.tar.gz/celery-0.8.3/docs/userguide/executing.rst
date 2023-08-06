=================
 Executing Tasks
=================

Executing tasks is done with ``apply_async``, and it's shortcut ``delay``.

``delay`` is simple and convenient, as it looks like calling a regular
function:

.. code-block:: python

    MyTask.delay(arg1, arg2, kwarg1="x", kwarg2="y")

The same thing using ``apply_async`` is written like this:

.. code-block:: python

    AddTask.delay(args=[arg1, arg2], kwargs={"kwarg1": "x", "kwarg2": "y"})

But ``delay`` doesn't give you as much control as using ``apply_async``.
With ``apply_async`` you can override the execution options available as attributes on
the ``Task`` class; ``routing_key``, ``exchange``, ``immediate``, ``mandatory``,
``priority``, and ``serializer``.  In addition you can set a countdown or an eta, provide
a custom broker connection or change the broker connection timeout.

Let's go over these in more detail. The following examples uses this simple
task, used to add two numbers:

.. code-block:: python

    class AddTask(Task):

        def run(self, x, y):
            return x + y


ETA and countdown
-----------------

The ETA (estimated time of arrival) lets you set a specific date and time for
when after, your task should execute. ``countdown`` is a shortcut to set this
by seconds into the future.

.. code-block:: python

    >>> result = AddTask.apply_async(args=[10, 10], countdown=3)
    >>> result.get()    # this takes at least 3 seconds to return
    20

Note that your task is guaranteed to be executed at some time *after* the
specified date and time has passed, but not necessarily at that exact time.

While ``countdown`` is an integer, ``eta`` must be a ``datetime`` object,
specifying an exact date and time in the future. This is good if you already
have a ``datatime`` object and need to modify it with a ``timedelta``, or when
using time in seconds is not very readable.

.. code-block:: python

    from datetime import datetime, timedelta

    def quickban(username):
        """Ban user for 24 hours."""
        ban(username)
        tomorrow = datetime.now() + timedelta(days=1)
        UnbanTask.apply_async(args=[username], eta=tomorrow)


Serializer
----------

The default serializer used is :mod:`pickle`, but you can change this default by
changing the ``CELERY_SERIALIZER`` configuration directive. There is built-in
support for using ``pickle``, ``JSON`` and ``YAML``, and you can add your own
custom serializers by registering them in the carrot serializer registry.

You don't have to do any work on the worker receiving the task, the
serialization method is sent with the message so the worker knows how to
deserialize any task (of course, if you use a custom serializer, this must also be
registered in the worker.)

When sending a task the serializition method is taken from the following
places in order: The ``serializer`` argument to ``apply_async``, the
Task's ``serializer`` attribute, and finally the global default ``CELERY_SERIALIZER``
configuration directive.

.. code-block:: python

    >>> AddTask.apply_async(args=[10, 10], serializer="JSON")

Connections and connection timeouts.
------------------------------------

Currently there is no support for broker connection pooling in celery, but
this might change in the future. This is something you need to be aware of
when sending more than one task at a time, as ``apply_async`` establishes and
closes a connection every time.

If you need to send more than one task at the same time, it's a good idea to
establish the connection yourself and pass it to ``apply_async``:

.. code-block:: python

    from carrot.connection import DjangoBrokerConnection

    numbers = [(2, 2), (4, 4), (8, 8), (16, 16)]

    results = []
    connection = DjangoBrokerConnection()
    try:
        for args in numbers:
            res = AddTask.apply_async(args=args, connection=connection)
            results.append(res)
    finally:
        connection.close()

    print([res.get() for res in results])


In Python 2.5 and above, you can use the ``with`` statement:

.. code-block:: python

    from __future__ import with_statement
    from carrot.connection import DjangoBrokerConnection

    numbers = [(2, 2), (4, 4), (8, 8), (16, 16)]

    results = []
    with DjangoBrokerConnection() as connection:
        for args in numbers:
            res = AddTask.apply_async(args=args, connection=connection)
            results.append(res)

    print([res.get() for res in results])


*NOTE* TaskSets already re-uses the same connection, but not if you need to
execute more than one TaskSet.

The connection timeout is the number of seconds to wait before we give up on
establishing the connection, you can set this with the ``connect_timeout``
argument to ``apply_async``:

.. code-block:: python

    AddTask.apply_async([10, 10], connect_timeout=3)

or if you handle your connection manually by using the connection objects
``timeout`` argument:

.. code-block:: python

    connection = DjangoAMQPConnection(timeout=3)


Routing options
---------------

Celery uses the AMQP routing mechanisms to route tasks to different workers.
You can route tasks using the following entitites: exchange, queue and routing key.

Messages (tasks) are sent to exchanges, a queue binds to an exchange with a
routing key. Let's look at an example:

Our application has a lot of tasks, some process video, others process images,
and some gathers collective intelligence about users. Some of these have
higher priority than others so we want to make sure the high priority tasks
get sent to powerful machines, while low priority tasks are sent to dedicated
machines that can handle these at their own pace, uninterrupted.

For the sake of example we have only one exchange called ``tasks``.
There are different types of exchanges that matches the routing key in
different ways, the exchange types are:

* direct

    Matches the routing key exactly.

* topic

    In the topic exchange the routing key is made up of words separated by dots (``.``).
    Words can be matched by the wildcars ``*`` and ``#``, where ``*`` matches one
    exact word, and ``#`` matches one or many.

    For example, ``*.stock.#`` matches the routing keys ``usd.stock`` and
    ``euro.stock.db`` but not ``stock.nasdaq``.

(there are also other exchange types, but these are not used by celery)

So, we create three queues, ``video``, ``image`` and ``lowpri`` that binds to
our ``tasks`` exchange, for the queues we use the following binding keys::

    video: video.#
    image: image.#
    lowpri: misc.#

Now we can send our tasks to different worker machines, by making the workers
listen to different queues:

.. code-block:: python

    >>> CompressVideoTask.apply_async(args=[filename],
    ...                               routing_key="video.compress")

    >>> ImageRotateTask.apply_async(args=[filename, 360],
                                    routing_key="image.rotate")

    >>> ImageCropTask.apply_async(args=[filename, selection],
                                  routing_key="image.crop")
    >>> UpdateReccomendationsTask.apply_async(routing_key="misc.recommend")


Later, if suddenly the image crop task is consuming a lot of resources,
we can bind some new workers to handle just the ``"image.crop"`` task,
by creating a new queue that binds to ``"image.crop``".


AMQP options
------------

* mandatory

This sets the delivery to be mandatory. An exception will be raised
if there are no running workers able to take on the task.

* immediate

Request immediate delivery. Will raise an exception
if the task cannot be routed to a worker immediately.

* priority

A number between ``0`` and ``9``, where ``0`` is the highest priority.
Note that RabbitMQ does not implement AMQP priorities, and maybe your broker
does not either, please consult your brokers documentation for more
information.
