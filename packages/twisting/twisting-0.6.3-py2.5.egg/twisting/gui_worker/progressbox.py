"""Simple progress box we can add in a status bar of the main window to have
information about current works progress.
"""
# gtk import
import gtk

# component import
from twisting.progress_info import ProgressInfo

__all__ = ['ProgressBox']

class ProgressBox():
    """Our simple progress box for the parent window of a work. Must create
    in the parent and updated by the progress window of the twisting
    framework.
    """

    def __init__(self, progress_bar, fraction_step=None):
        """Init the progress box and call init widget method to create and
        set basic gtk element for the progress representation.
        """
        # init class variable
        self.progress_bar = progress_bar

        # set default fraction step
        if not fraction_step:
            self.fraction_step = float(1) / float(10)

    def set_text(self, text):
        """Update the progession text.

        @param text: text to be set
        @type text: str
        """
        self.progress_bar.set_text(text)

    def pulse(self, fraction=0, nb_of_active_task=0, end_task=False,
            pulse_only=False):
        """Set the progress bar to the corresponding fraction. Update the
        remaining info with the progress info tool.

        @param fraction: new progress bar fraction
        @type fraction: float
        """
        if not self.progress_bar:
            return

        if pulse_only:
                self.progress_bar.set_pulse_step(self.fraction_step)
                self.progress_bar.pulse()
                return

        #
        if fraction == 0:
            # update the progress text
            self.progress_bar.set_text('')
            self.progress_bar.set_fraction(0)
        
        #
        elif fraction < nb_of_active_task:
            # update the progress bar
            self.progress_bar.set_fraction(fraction/nb_of_active_task)

        #
        else:
            # update the progress finish text
            self.progress_bar.set_text('done')
            # update the progress bar
            self.progress_bar.set_fraction(1)
