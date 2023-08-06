"""Useful window for  progress task boxes display and management.
"""
# gtk import
import gtk
from gtk.gdk import keyval_name

# zope import
from zope.interface import implements

# simple worker import
from twisting import IProgress, ProgressBase, NotInitializeError
from twisting.gui_worker import ProgressBox, TaskBox
from twisting.tools import get_filepath

import logging
log = logging.getLogger()

__all__ = ['ProgressWindow']

class ProgressWindow(ProgressBase):
    """Specific gtk window for task boxes from the twisting API management.
    """
    # declare our implementation
    implements(IProgress)

    def __init__(self, title='Progression dialog', all_finish_callback=None):
        """Instantiate a new singleton window that can be call everywhere
        after. Init main quit callback, variable and call gtk widgets building
        method.

        @param title: title of the windows, default: 'Progression dialog'
        @type title: str

        @param all_finish_callback: specific callback for all tasks ending
        @type all_finish_callback: function
        """
        # init base
        ProgressBase.__init__(self, all_finish_callback=all_finish_callback)

        # the progress box for the parent
        self.parent = None
        self.progress_bar = None
        self.progress_box = None

        #
        self.__separator_dict = dict()

        #
        self.reset(title)

    def reset(self, title='Progression dialog'):
        """
        """
        # widgets init
        self.__init_widgets(title)

        # window callback
        self.__init_callbacks()

        # add the task box to the dict
        if len(self.task_dict) > 0:
            #
            for key_ in self.task_dict.keys():
                #
                task_ = self.task_dict[key_]
                separator_ = self.__separator_dict[key_]

                # add the taskbox
                self.__mainbox.pack_start(task_, expand=False, fill=False)
                # add the separator
                self.__mainbox.pack_start(separator_, expand=False, fill=False)

                # display the window
                self.window.show_all()

    def set_parent(self, parent, progress_bar=None):
        """Update the parent window for quit management and progress box to
        update when the pulse method is called.

        @param parent: parent window
        @type parent: gtk.Window

        @param progress_bar: gtk progress bar from the parent to update
        @type progress_bar: gtk.ProgressBar
        """
        # set transient flag
        self.window.set_transient_for(parent)
        # set position center on parent
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        # we destroy the windo with the parent
        self.window.set_destroy_with_parent(True)

        # set the progress box and the parent
        self.parent = parent
        #
        if progress_bar:
            self.progress_box = ProgressBox(progress_bar)

    def set_progress_box(self, progress_bar):
        """
        @param progress_bar: gtk progress bar from the parent to update
        @type progress_bar: gtk.ProgressBar
        """
        self.progress_box = ProgressBox(progress_bar)

    def set_progress_bar(self, progress_bar):
        """Easy method to set a new progress bar callback. Useful when you
        change your main window.
        """
        self.progress_box.progress_bar = progress_bar

    def __init_widgets(self, title):
        """Init the worker progress window style.
        """
        # create the window
        self.window = gtk.Window()

        # is resizable
        self.window.set_resizable(True)
        # default size
        self.window.resize(420, 280)
        # not deletable with the cross, use hide button instead
        self.window.set_deletable(False)
        self.window.set_destroy_with_parent(True)

        # set the name
        self.window.set_title(title)

        if self.parent:
            self.set_parent(self.parent, self.progress_bar)

        # main box for the task
        self.__mainbox = gtk.VBox()
        # add dummy space
        self.__mainbox.pack_end(gtk.VBox(), padding=20)

        # box for the color theme
        event_box = gtk.EventBox()
        # theme color
        color = gtk.gdk.color_parse("#FFFFFF")
        event_box.modify_bg(gtk.STATE_NORMAL, color)
        # add the mainbox to the theme box
        event_box.add(self.__mainbox)

        # scrollable place
        scrolled_window = gtk.ScrolledWindow()
        # set scrollable policy
        scrolled_window.set_policy(
                gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        # add the main box to the viewport
        scrolled_window.add_with_viewport(event_box)

        # create the stop icon
        hide_image = gtk.Image()
        # get the image file path
        hide_file_path = get_filepath(
                __name__, '/static/hide_small.png')
        hide_image.set_from_file(hide_file_path)
        # hide label
        label = gtk.Label('Hide')

        hide_box = gtk.HBox()
        hide_box.pack_start(hide_image)
        hide_box.pack_start(label)

        # create the remote button
        self.hide_button = gtk.Button()
        self.hide_button.set_relief(gtk.RELIEF_HALF)
        self.hide_button.add(hide_box)

        # box for button positionning
        buttonbox = gtk.HButtonBox()
        #
        buttonbox.set_property('layout-style', gtk.BUTTONBOX_END)
        # add the hide button to the button box
        buttonbox.pack_start(self.hide_button)

        # border box for padding management
        borderbox = gtk.VBox()
        # padding set
        borderbox.set_border_width(5)
        # pack the the box
        borderbox.pack_start(scrolled_window)
        # pack the the box
        borderbox.pack_start(buttonbox, expand=False, fill=False, padding=4)

        # add the main box to the window
        self.window.add(borderbox)

    def __init_callbacks(self):
        """Set the pre-define callbacks.
        """
        # destroy callback
        self.hide_button.connect("clicked", self.__on_hide)

        # destroy callback
        self.window.connect("destroy", self.__on_quit)

    def show(self):
        """Show window wrapping to show the progess window.
        """
        if not self.window:
            self.reset()

        # display the window
        self.window.show_all()
        self.window.present()

    def __on_hide(self, widget):
        """Hide gui callback.
        """
        self.window.hide()

    def hide(self):
        """Show window wrapping to hide the progess window.
        """
        if not self.window:
            return

        self.window.hide()

        if self.parent:
            self.parent.present()

    def __on_quit(self, widget):
        """Quit gui callback.
        """
        self.window = None
        self.quit()

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
        task_ = TaskBox(id_, pretty_name, self.remove_task, self.task_finish)

        # add the taskbox
        self.__mainbox.pack_start(task_, expand=False, fill=False)

        # create a separator
        separator = gtk.HSeparator()

        # add the separator
        self.__mainbox.pack_start(separator, expand=False, fill=False)

        # display the window
        self.window.show_all()

        # add the task box to the dict
        self.task_dict[id_] = task_
        self.__separator_dict[id_] = separator

        # new task
        return False

    def remove_task(self, id_):
        """Remove a task box and the corresponding separator (pure esthetic
        problem, no functional need).

        @param id_: id of the task to remove
        @type id_: str
        """
        #
        if not self.task_dict.has_key(id_):
            return

        # task box to remove
        task = self.task_dict[id_]

        # call base
        ProgressBase.remove_task(self, id_)

        # remove the taskbox
        self.__mainbox.remove(task)
        # separator to remove
        separator = self.__separator_dict[id_]
        # remove the separator
        self.__mainbox.remove(separator)
        # remove the task box for the dico
        self.__separator_dict.pop(id_)

        # update the progress box for the parent
        self.__update_progress_box()

    def pulse(self, id_):
        """update a task box progress pulse status.

        @param id_: id of the task to update
        @type id_: str
        """
        # call base
        ProgressBase.pulse(self, id_)

        # refresh the progress box of the parent
        self.__update_progress_box()

    def task_finish(self, id_):
        """Set the final status for a specific method and check if all tasks
        are finished. If all task are ended call the all_task_finished callback
        from the parent window.

        @param id_: id of the task that was just ended
        @type id_: str
        """
        # call base
        ProgressBase.task_finish(self, id_)

        # refresh the progress box of the parent
        self.__update_progress_box(end_task=True)

    def __update_progress_box(self, end_task=False):
        """Refresh the progress box pulse status of the parent.
        """
        if not self.progress_box:
            return

        # must have a task
        if len(self.task_dict) == 0:
            self.progress_box.pulse()
            return

        # init variables
        fraction = 0
        nb_of_active_task = 0
        pulse_only_ = False

        # update variables
        for key in self.task_dict.keys():
            # a toolbox
            taskbox = self.task_dict[key]
            #
            if not taskbox.is_finished:
                #
                if taskbox.max_pulse > 1:
                    # update values
                    fraction += taskbox.get_fraction()
                    # inc the active box value
                    nb_of_active_task += 1

                # if pulse only
                else:
                    pulse_only_ = True
                    break

        #
        if pulse_only_ == True:
            #
            self.progress_box.pulse(pulse_only=True)
            return

        #
        else:
            if nb_of_active_task > 0:
                # pulse the progress box
                self.progress_box.pulse(fraction, nb_of_active_task, end_task)
            else:
                self.progress_box.pulse(1, 1)

    def __on_key_press(self, widget, event):
        """Catch the buttton enter press event or escape. Not used at the
        moment, may be one day :!).
        """
        if keyval_name(event.keyval) == "Return":
            pass

        if keyval_name(event.keyval) == "Escape":
            pass
