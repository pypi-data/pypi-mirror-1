"""Useful window for  progress task boxes display and management.
"""
# zope import
from zope.interface import implements

# simple worker import
from twisting import IProgress, ProgressBase, NotInitializeError
from twisting.worker import Task

import logging
log = logging.getLogger()

__all__ = ['Progress']

class Progress(ProgressBase):
    """Specific manager for tasks for the base worker API.
    """

    def add_task(self, id_, pretty_name):
        """Add a new task box into the progress window and init the twisted
        *deferToThread* callbacks for work, error, and result.

        @param id_: id of the task to create
        @type id_: str

        @param pretty_name: pretty name of the task to display in the box
        @type pretty_name: str
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # task already exist
        if self.task_dict.has_key(id_):
            return True

        # create a task box
        task = Task(id_, pretty_name, self.remove_task, self.task_finish)

        # add the task box to the dict
        self.task_dict[id_] = task

        # new task
        return False
