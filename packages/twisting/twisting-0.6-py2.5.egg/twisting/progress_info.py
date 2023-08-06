"""ProgressionInfo is a tools to extract progression informations :
    - Speed number of iteration per seconds
    - Remaining time
"""
from datetime import datetime
from decimal import Decimal

class ProgressInfo(object):

    def __init__(self, item_count=0):
        """
        """
        #
        self.__last_timestamp = datetime.now()
        #
        self.__speed = 0.0
        #
        self.__items_bucket = list()
        #
        self.item_count = item_count
        #
        self.speed_text = ''
        #
        self.progress_text = ''

    def clear_bucket(self):
        """
        """
        self.__items_bucket = list()

    def __compute_speed(self, index_):
        """
        """
        # delta since last update
        timestamp_ = datetime.now()
        delta_ = timestamp_ - self.__last_timestamp

        # update last timestamp
        self.__last_timestamp = timestamp_

        # update the bucket
        self.__items_bucket.insert(0, delta_.microseconds)

        # enhance average
        if len(self.__items_bucket) < 5:
            return

        # update speed
        try:
            s_time_ = sum(self.__items_bucket[-index_:]) / 1000000.0
            self.__speed = index_ / s_time_
        except:
            pass

    def __get_remaining_info(self, index_):
        """
        """
        if self.__speed <= 0 or len(self.__items_bucket) < 5:
            return ''

        # compute remaining items
        remaining_items_ = self.item_count - index_

        # compute remaining seconds
        remaining_seconds_ = int(remaining_items_ / self.__speed)

        # format info hours
        hours = remaining_seconds_ / 3600
        remaining_seconds_ -= 3600 * hours

        # format info minutes
        minutes = remaining_seconds_ / 60
        remaining_seconds_ -= 60 * minutes

        # format infos seconds
        seconds = remaining_seconds_

        # format text
        remaining_info = '%02d' % hours
        remaining_info += ':%02d' % minutes
        remaining_info += ':%02d' % seconds
        remaining_info += ' Remaining'

        return remaining_info

    def update(self, item_count=None, index_=None):
        """
        """
        if index_ == None or index_ >= len(self.__items_bucket):
            # compute index
            index_ = len(self.__items_bucket) - 1

        # update item_count var
        if item_count:
            self.item_count = item_count

        # we update the progression status
        self.__compute_speed(index_)

        # update speed text
        if self.__speed > 0:
            self.speed_text = '%.2f items/s' % self.__speed
        else:
            self.speed_text = ''

        # update progress text
        self.progress_text = '%s  %s' % (
                self.speed_text,
                self.__get_remaining_info(index_))
