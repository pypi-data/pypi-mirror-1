"""Little tools package form relative packaged resource path retrieval.
"""
# python import
import pkg_resources
from twisted.internet import reactor

# twisting import
from twisting.messages import Pause, Play, Stop
from twisting import ProgressManager

__ALL__ = ['check', 'get_filepath', 'pulse', 'state_machine']

def get_filepath(class_path, file_name):
    """return the relative static path to a file

    @param class_path: must be call with __name__
    @type class_path: str

    @param file_name: name of the expected file
    @type file_name: str
    """
    if pkg_resources.resource_exists(
                            class_path, file_name):
        return pkg_resources.resource_filename(
                            class_path, file_name)
    else:
        return None

def pulse(task):
    ProgressManager().pulse(task.id_)

def check(task):
    """Check the current progress state of a specific task.

    @param task: task to be checked
    @type task: twisting.base_worker.Task

    @return: boolean info:
        - True: when a stop message from the task is catched
        - False: no message catched, the worker can continue
    """
    # check for task event
    while not task.task_event_queue.empty():
        # dequeue
        event = task.task_event_queue.get()

        # if stop we stop and return True to stop the worker
        if isinstance(event, Stop):
            reactor.callFromThread(task.stop)
            return True

        # if pause we wait until next event
        if isinstance(event, Pause):
            event_pause = task.task_event_queue.get(block=True)

            # if play we continue
            if isinstance(event_pause, Play):
                pass

            # if stop we stop and return True to stop the worker
            elif isinstance(event_pause, Stop):
                reactor.callFromThread(task.stop)
                return True

    # not stopped by default
    return False

def state_machine(task):
    """Sate machine method call by the worker to up update a task and the
    progress window, or be paused or stopped. Must be call in the worker loop
    otherwhise no progress status or info will be updated.

    @param task: task to be checked
    @type task: twisting.base_worker.Task

    @return: boolean info:
        - True: when a stop message from the task is catched
        - False: no message catched, the worker can continue
    """
    # first pulse
    pulse(task)

    # check the current progress state
    return check(task)
