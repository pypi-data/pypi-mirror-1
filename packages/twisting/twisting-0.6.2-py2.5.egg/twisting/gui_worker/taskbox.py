"""Gui box managed by the progress window for a task progress information
presentation.
"""
# python import
from Queue import Queue

# twisted import
from twisted.internet import reactor

# zope import
from zope.interface import implements

# gtk import
import gtk
from gtk.gdk import keyval_name

# twisting import
from twisting import ITask, TaskBase
from twisting.messages import Pause, Play, Stop
from twisting.tools import get_filepath

__all__ = ['TaskBox']

class TaskBox(TaskBase, gtk.EventBox):
    """Gtk event box to be added in the progress window for task progress view.
    """

    # declare our implementation
    implements(ITask)

    def __init__(self, id_, pretty_name, remove_callback, finish_callback,
            icon='gears_medium'):
        """Init the task box variables and call init widget method to create
        and set an nice gtk event box for the progress representation of a
        specific task.

        @param id_: specific id of the task, common in all the twisting
        framework for separated management in the progress window
        @type id_: str

        @param pretty_name: much pretty name than the id, only use for gtk
        rendering and information displaying.
        @type pretty_name: str

        @param remove_callback: callback from the parent progress window
        to call on remove signal to ask for self removal when ask by the user
        @type remove_callback: function

        @param finish_callback: callback from the parent progress window
        to call at then end for main progress status update
        @type finish_callback: function

        @param icon: picto, gears representing a task work by default, can be
        overrided by other picto to and in the static img folder for other task
        type like pdf, sql...
        @type icon: str
        """
        # call parent
        TaskBase.__init__(self, id_, pretty_name,
                remove_callback, finish_callback)

        # init parent class
        gtk.EventBox.__init__(self)

        # id of the currently drawn objects
        self.__can_draw = True

        # init progress info
        self.__progress_bar = None
        self.__progression_label = None

        # our buttons
        self.__task_image = None
        self.play_button = None
        self.stop_button = None
        self.remove_button = None

        # widget init
        self.__init_widgets()
        self.set_icon(icon)

        # init gtk callbacks
        self.__init_callbacks()

    def __get_image(self, image_name):
        """Common internal method to obtain a gtk image from
        """
        # get the image file path
        file_path = get_filepath(
                __name__, '/static/%s.png' % image_name)

        # if image found
        if file_path:
            # create the icon
            image = gtk.Image()
            # set image on the widget
            image.set_from_file(file_path)
            # set the image at the end
            return image

        else:
            return None

    def __get_progress_button(self, image_name):
        """Generic method to init a progress button with the corresponding
        image.
        """
        # create the remote button
        button = gtk.Button()
        button.set_relief(gtk.RELIEF_NONE)
        # get the gtk image
        image = self.__get_image(image_name)
        if image:
            # set the button image
            button.set_image(image)
        # return the button
        return button

    def __init_progress_box(self):
        """Format a progress box with default values for the task box.
        """
        # create the progress box
        progressbox = gtk.VBox()

        # add the porgress title
        self.__progression_title = gtk.Label()
        self.__progression_title.set_markup('<b>%s</b>' % self.pretty_name)
        self.__progression_title.set_property('xalign', 0)
        self.__progression_title.set_property('yalign', 0)
        progressbox.pack_start(
                self.__progression_title, expand=True, fill=False)

        # add the progress bar
        self.__progress_bar = gtk.ProgressBar()
        # set pulse step of the progress bar
        self.__progress_bar.set_fraction(0)
        # pack the progress
        progressbox.pack_start(self.__progress_bar, expand=True, fill=False)

        # add the progress info
        self.__progression_label = gtk.Label()
        self.__progression_label.set_markup('')
        self.__progression_label.set_property('xalign', 0)
        self.__progression_label.set_property('yalign', 1)
        progressbox.pack_start(self.__progression_label, expand=True, fill=False)

        # return the progress box
        return progressbox

    def set_icon(self, icon):
        """Public method to modify the taskbox icon on fly. The corresponding file must be placed in the twisting package.

        """
        # get the image file path
        gears_file_path = get_filepath(
                __name__, '/static/%s.png' % icon)

        # gears by default
        if not gears_file_path:
            gears_file_path = get_filepath(
                __name__, '/static/gears_medium.png' % icon)

        # set the image content from the file
        self.__task_image.set_from_file(gears_file_path)

    def __init_widgets(self):
        """Init the gtk widgets from scratch to obtain the nice task box.

        @param icon: icon nam to use for nicer progress small description
        @type icon: str
        """
        # theme color
        color = gtk.gdk.color_parse("#EAEAEA")
        self.modify_bg(gtk.STATE_NORMAL, color)

        # box container
        h_box = gtk.HBox()

        # small padding
        h_box.set_border_width(4)

        # create the task icon
        self.__task_image = gtk.Image()
        # add the gtk image in the box
        h_box.pack_start(self.__task_image,
                expand=False, fill=False, padding=10)

        # get the formatted prgress box
        progressbox = self.__init_progress_box()

        # add the progress box to the taskbox
        h_box.pack_start(progressbox, expand=True, fill=True, padding=10)

        # add the play button to the taskbox
        self.play_button = self.__get_progress_button('pause_very_small')
        h_box.pack_start(self.play_button, expand=False, fill=False)

        # add the stop button to the taskbox
        self.stop_button = self.__get_progress_button('stop_very_small')
        h_box.pack_start(self.stop_button, expand=False, fill=False)

        # add the remove button to the taskbox
        self.remove_button = self.__get_progress_button('cross_very_small')
        h_box.pack_start(self.remove_button, expand=False, fill=False)

        # the HBox to the current eventbox window
        self.add(h_box)
        # show now
        self.show_all()

    def __init_callbacks(self):
        """
        """
        # play callback
        self.play_button.connect("clicked", self.on_play)

        # destroy callback
        self.connect("destroy", self.on_stop)

        # stop callback
        self.stop_button.connect("clicked", self.on_stop)

        # remove callback
        self.remove_button.connect("clicked", self.on_remove)

    def pulse(self):
        """Increment the progress status, get the progress info and update
        all the gtk components used for progress status view.
        """
        #
        if TaskBase.pulse(self):
            if self.max_pulse > 1:
                fraction_ = self.get_fraction() + self.fraction_step
                self.__progress_bar.set_fraction(fraction_)

            else:
                self.__progress_bar.set_pulse_step(self.fraction_step)
                self.__progress_bar.pulse()

            return True

        else:
            self.__progress_bar.set_fraction(1)
            self.play_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)
            return False

    def set_progress_end_state(self, label):
        """Common internal terminal method call from stop or finish for gtk
        and finish flag update.

        @param label: specific label to display at the task end
        @type label: str
        """
        # call parent
        TaskBase.set_progress_end_state(self, label)

        # set the label text
        if self.__can_draw:
            # set progress
            self.__progress_bar.set_fraction(1)
            self.set_text(label)

        # set sentitive flag for stop button to False
        self.stop_button.set_sensitive(False)
        # set sentitive flag for play button to False
        self.play_button.set_sensitive(False)

    def play(self):
        """Update the play or pause picto on the gtk button.
        """
        # call parent
        TaskBase.play(self)

        if self.is_playing:
            img = 'pause'

        else:
            img = 'play'

        # get the new gtk image
        image = self.__get_image('%s_very_small' % img)
        if image:
            # update the button image
            self.play_button.set_image(image)

    def set_title(self, text):
        """Simple title label update. Can be used at the end somewhere
        else to pass a message to the user.
        """
        if not self.__can_draw:
            return
        # set the label text
        self.__can_draw = False
        self.__progression_title.set_markup('<b>%s</b>' % text)
        self.__can_draw = True

    def set_text(self, text):
        """Simple progress info label update. Can be used at the end somewhere
        else to pass a message to the user.
        """
        if not self.__can_draw:
            return
        # set the label text
        self.__can_draw = False
        self.__progression_label.set_markup('<small>%s</small>' % text)
        self.__can_draw = True

    def set_sensitive(self, sensitive):
        """Active/deactive buttons, in case of non user manipulation
        expectation.
        """
        # set sentitive flag for stop button
        self.play_button.set_sensitive(sensitive)
        # set sentitive flag for stop button
        self.stop_button.set_sensitive(sensitive)
        # set sentitive flag for remove button
        self.remove_button.set_sensitive(sensitive)

    def __on_key_press(self, widget, event):
        """Catch the buttton enter press event.
        """
        if keyval_name(event.keyval) == "Return":
            pass

        if keyval_name(event.keyval) == "Escape":
            pass
