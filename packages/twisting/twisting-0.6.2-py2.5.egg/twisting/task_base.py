"""Gui box managed by the progress window for a task progress information
presentation.
"""
# python import
from Queue import Queue

# twisted import
from twisted.internet import reactor

# zope import
from zope.interface import implements

# twisting import
from twisting import ITask
#
from twisting.messages import Pause, Play, Stop
from twisting.progress_info import ProgressInfo

__all__ = ['TaskBase']

class TaskBase(object):
    """Gtk event box to be added in the progress window for task progress view.
    """

    # declare our implementation
    implements(ITask)

    def __init__(self, id_, pretty_name, remove_callback, finish_callback):
        """Init the task box variables and call init widget method to create
        and set an nice object for the progress representation of a specific
        task.

        @param id_: specific id of the task, common in all the twisting
        framework for separated management in the progress window
        @type id_: str

        @param pretty_name: much pretty name than the id for information
        displaying.
        @type pretty_name: str

        @param remove_callback: callback from the parent progress window
        to call on remove signal to ask for self removal when ask by the user
        @type remove_callback: function

        @param finish_callback: callback from the parent progress window
        to call at then end for main progress status update
        @type finish_callback: function
        """
        # set the task id
        self.id_ = id_

        # set the task id
        self.pretty_name = pretty_name

        # queues
        self.task_event_queue = Queue()

        # finish flag
        self.is_finished = False

        # play flag
        self.is_playing = True

        # progress variables init
        self.max_pulse = 1
        self.current_pulse = 0
        self.fraction_step = 0

        # progress info variable
        self.progress_info = None

        # parent window callback for removing
        self.remove_callback = remove_callback

        # parent window callback call when finish for global progress update
        self.finish_callback = finish_callback

    def set_max_pulse(self, max_pulse):
        """Init the number of expected iterations. Must be define at the
        begining of the task. It will be use by the progress info library
        for remaining time computing.

        @param max_pulse: number of iterations of the task
        @type max_pulse: int
        """
        if max_pulse > 1:
            # update progress info tools
            self.progress_info = ProgressInfo(max_pulse)
            # set fraction step
            self.max_pulse = max_pulse
            self.current_pulse = 0
            if self.max_pulse > 0:
                self.fraction_step = float(1) / float(self.max_pulse)
            else:
                self.fraction_step = 1

        else:
            self.fraction_step = float(1) / float(10)

    def get_fraction(self):
        """
        """
        return float(self.current_pulse) / float(self.max_pulse)

    def pulse(self):
        """Increment the progress status, get the progress info and update
        all the components used for progress status view.
        """
        # update the current pulse
        self.current_pulse += 1

        #
        msg = '%s/%s ' % (self.current_pulse, self.max_pulse)
        # manage percent
        if self.progress_info:
            self.progress_info.update()
            msg += self.progress_info.progress_text
            self.set_text(msg)

        if self.max_pulse > 1:
            #
            return self.get_fraction() + self.fraction_step < 1

        else:
            return True

    def on_play(self, widget):
        """Play or pause gtk callback. Put the play or pause event message
        in the queue to be managed by the task function throw the state_machine
        function work or result.
        """
        # pause
        if self.is_playing:
            self.task_event_queue.put(Pause(self.id_))

        # resume
        else:
            self.task_event_queue.put(Play(self.id_))

        # play state update
        self.play()

    def play(self):
        """Update the play or pause picto on the gtk button.
        """
        # update the play or pause picto
        self.is_playing = not self.is_playing

    def on_stop(self, widget):
        """Stop callback that put an event message in the queue to be managed
        by the task function throw the state_machine to stop the current job.
        """
        # ask for stop
        self.task_event_queue.put(Stop(self.id_))

    def stop(self, label=None):
        """Method call when the stop status is effective. Automatically call
        by the state_machine function when the previous sent stop signal is
        catched. the final label can be overrided, by default the label is
        *pretty_name_of_the_task stopped*.

        @param label: specific label to display at the task stop
        @type label: str
        """
        #
        if label == None:
            label = '%s stopped' % self.pretty_name

        #
        self.set_progress_end_state(label)

    def finish(self, label=None):
        """Method call when the finish status is effective. Must be call at
        the end of the task loop in a callFromThread. the final label can be
        overrided, by default the label is *pretty_name_of_the_task stopped*.

        @param label: specific label to display at the task end
        @type label: str
        """
        if label == None:
            label = '%s finished' % self.pretty_name

        #
        self.set_progress_end_state(label)

    def set_progress_end_state(self, label):
        """Common internal terminal method call from stop or finish for gtk
        and finish flag update.

        @param label: specific label to display at the task end
        @type label: str
        """
        # finish flag
        self.is_finished = True
        # call the parent for progress update
        reactor.callFromThread(self.finish_callback, self.id_)

    def on_remove(self, widget):
        """Remove gtk callback call the common remove method.
        """
        self.remove()

    def remove(self):
        """Call the remove callback from the progress window to remove itself.
        Then put a stop message in the event queue to ask the working task to
        stop.
        """
        if not self.is_finished:
            # ask for stop
            self.task_event_queue.put(Stop(self.id_))

        # remove itself from the progress window
        reactor.callFromThread(self.remove_callback, self.id_)

    def set_title(self, text):
        """Simple title label update. Can be used at the end somewhere
        else to pass a message to the user.
        """
        NotImplementedError('You must implement parse method')

    def set_text(self, text):
        """Simple progress info label update. Can be used at the end somewhere
        else to pass a message to the user.
        """
        NotImplementedError('You must implement parse method')
