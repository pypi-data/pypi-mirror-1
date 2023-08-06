"""Useful window for  progress task boxes display and management.
"""
# twisted import
from twisted.internet import reactor, threads

# zope import
from zope.interface import implements

# simple worker import
from twisting import IProgress
from twisting.messages import Stop

import logging
log = logging.getLogger()

__all__ = ['ProgressException', 'NotInitializeError', 'ProgressBase']

class ProgressException(Exception):
    pass

class NotInitializeError(ProgressException):
    pass

class ProgressBase(object):
    """Specific manager for tasks for the base worker API.
    """
    # declare our implementation
    implements(IProgress)

    def __init__(self, all_finish_callback=None):
        """Instantiate a new singleton that can be call everywhere after.

        @param title: title of the manager, default: 'Progression manager'
        @type title: str

        @param all_finish_callback: specific callback for all tasks ending
        @type all_finish_callback: function
        """
        # initialized flag
        self.initialized = True

        # init dict of taskbox
        self.task_dict = dict()

        # callbacks init
        self.all_finish_callback = all_finish_callback

    def add_task(self, id_, pretty_name):
        """Add a new task box into the progress window and init the twisted
        *deferToThread* callbacks for work, error, and result.

        @param id_: id of the task to create
        @type id_: str

        @param pretty_name: pretty name of the task to display in the box
        @type pretty_name: str
        """
        NotImplementedError('You must implement parse method')

    def start_task(self, id_, worker_callback, end_callback=None,
            error_callback=None, param=None):
        """Start a specific task.

        @param id_: id of the task to start
        @type id_: str

        @param worker_callback: worker function to manage
        @type worker_callback: function

        @param end_callback: function to call at the end
        @type end_callback: function

        @param error_callback: function to call in case of error
        @type error_callback: function

        @param param: simple way to add specific parameter when the task will be
        executed.
        @type param: obj
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # if the event come after removal we quit
        if not self.task_dict.has_key(id_):
            # task not started
            return False

        # need a task function
        if not worker_callback:
            return False

        # get the task box
        task = self.task_dict[id_]
        
        # create the worker thread
        # with an additional parameter
        if param:
            defered_thread = threads.deferToThread(worker_callback, task, param)
        # without parameter
        else:
            defered_thread = threads.deferToThread(worker_callback, task)

        # set the thread result callback
        if end_callback:
            defered_thread.addCallback(end_callback)

        # set the thread error callback
        if error_callback:
            defered_thread.addErrback(error_callback)

        # task started
        return True

    def stop_task(self, id_):
        """Stop a specific task using queue.

        @param id_: id of the task to remove
        @type id_: str
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # if the event come after removal we quit
        if not self.task_dict.has_key(id_):
            return

        # task box to stop
        task = self.task_dict[id_]
        # stop the task
        task.task_event_queue.put(Stop(id_))

    def stop_all_tasks(self):
        """Stop all the tasks.
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # update variables
        for key in self.task_dict.keys():
            # remove
            self.stop_task(key)

    def remove_task(self, id_):
        """Remove a task box and the corresponding separator (pure esthetic
        problem, no functional need).

        @param id_: id of the task to remove
        @type id_: str
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # if the event come after removal we quit
        if not self.task_dict.has_key(id_):
            return

        # remove the task box for the dico
        self.task_dict.pop(id_)

    def remove_all_tasks(self):
        """Remove all the tasks for next works.
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # update variables
        for key in self.task_dict.keys():
            # remove
            self.remove_task(key)

    def quit(self):
        """Stop and remove all.
        """
        self.stop_all_tasks()
        self.remove_all_tasks()

    def pulse(self, id_):
        """update a task box progress pulse status.

        @param id_: id of the task to update
        @type id_: str
        """
        if not hasattr(self, 'initialized'):
            msg = 'You should initialize the progress window before using it'
            raise NotInitializeError(msg)

        # if the event come after removal we quit
        if not self.task_dict.has_key(id_):
            return

        # update the task progress
        reactor.callFromThread(self.task_dict[id_].pulse)

    def task_finish(self, id_):
        """Set the final status for a specific method and check if all tasks
        are finished. If all task are ended call the all_task_finished callback
        from the parent window.

        @param id_: id of the task that was just ended
        @type id_: str
        """
        number_of_finished_tasks = 0

        # update variables
        for key in self.task_dict.keys():
            # a toolbox
            if self.task_dict[key].is_finished:
                number_of_finished_tasks += 1

        if number_of_finished_tasks == len(self.task_dict) \
        and number_of_finished_tasks > 0:
            # call the finish call back when everything is done
            self.all_finish_callback()
