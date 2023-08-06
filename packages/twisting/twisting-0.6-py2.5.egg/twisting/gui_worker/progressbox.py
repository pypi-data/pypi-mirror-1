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

    def __init__(self, progress_bar):
        """Init the progress box and call init widget method to create and
        set basic gtk element for the progress representation.
        """
        # init class variable
        self.progress_bar = progress_bar

        # progress info variable
        self.__progress_info = ProgressInfo()

    def set_text(self, text):
        """Update the progession text.

        @param text: text to be set
        @type text: str
        """
        self.progress_bar.set_text(text)

    def pulse(self, fraction=0, nb_of_active_task=0, end_task=False):
        """Set the progress bar to the corresponding fraction. Update the
        remaining info with the progress info tool.

        @param fraction: new progress bar fraction
        @type fraction: float
        """
        if not self.progress_bar:
            return

        #
        if fraction == 0:
            # update the progress text
            self.progress_bar.set_text('')
            self.progress_bar.set_fraction(0)
        #
        elif fraction < nb_of_active_task:
            # clear bucket for good calculation
            if end_task:
                self.__progress_info.clear_bucket()
            # update the progress
            self.__progress_info.update(
                            item_count=(nb_of_active_task*100),
                            index_=(fraction*100))
            # update the progress text
            self.progress_bar.set_text(self.__progress_info.progress_text)
            # update the progress bar
            self.progress_bar.set_fraction(fraction/nb_of_active_task)
        else:
            # update the progress finish text
            self.progress_bar.set_text('done')
            # update the progress bar
            self.progress_bar.set_fraction(1)
