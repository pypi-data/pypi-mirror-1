# zinspect import for interface checking
from zinspect import conforms

# interface import
from twisting import IProgress, ITask, ProgressBase, TaskBase

class ProgressManager(object):

    state_machine = None
    instance = None

    def __new__(klass, title='Progression dialog',
            all_finish_callback=None, ui=False):
        """
        """
        #
        if klass.instance is None:
            #
            if ui:
                from twisting.gui_worker import ProgressWindow, TaskBox
                conforms(ProgressBase, IProgress)
                conforms(TaskBase, ITask)
                instance_ = ProgressWindow(
                        title=title, all_finish_callback=all_finish_callback)

            else:
                from twisting.worker import Progress, Task
                conforms(ProgressBase, IProgress)
                conforms(TaskBase, ITask)
                instance_ = Progress(
                        all_finish_callback=all_finish_callback)

            #
            klass.instance = instance_

        #
        return klass.instance
