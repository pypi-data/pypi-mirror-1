"""celery.backends.database"""
from celery.models import TaskMeta
from celery.backends.base import BaseBackend


class Backend(BaseBackend):
    """The database backends. Using Django models to store task metadata."""

    def __init__(self, *args, **kwargs):
        super(Backend, self).__init__(*args, **kwargs)
        self._cache = {}

    def store_result(self, task_id, result, status):
        """Mark task as done (executed)."""
        if status == "DONE":
            result = self.prepare_result(result)
        elif status == "FAILURE":
            result = self.prepare_exception(result)
        return TaskMeta.objects.store_result(task_id, result, status)

    def is_done(self, task_id):
        """Returns ``True`` if task with ``task_id`` has been executed."""
        return self.get_status(task_id) == "DONE"

    def get_status(self, task_id):
        """Get the status of a task."""
        return self._get_task_meta_for(task_id).status

    def get_result(self, task_id):
        """Get the result for a task."""
        meta = self._get_task_meta_for(task_id)
        if meta.status == "FAILURE":
            return self.exception_to_python(meta.result)
        else:
            return meta.result

    def _get_task_meta_for(self, task_id):
        if task_id in self._cache:
            return self._cache[task_id]
        meta = TaskMeta.objects.get_task(task_id)
        if meta.status == "DONE":
            self._cache[task_id] = meta
        return meta

    def cleanup(self):
        """Delete expired metadata."""
        TaskMeta.objects.delete_expired()
