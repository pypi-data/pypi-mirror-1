==============
 How it works
==============

A user delays a task by sending a message to the broker.

When the celery worker server is started, it establishes a connection to the
broker, this connection is always open. Whenever there is a new message, the
broker sends it to a worker.
