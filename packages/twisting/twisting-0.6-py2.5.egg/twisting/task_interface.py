"""
"""
from zope.interface import Interface, Attribute

class ITask(Interface):
    """
    """
    # the task id
    id_ = Attribute("Mandatory")

    # the task pretty name
    pretty_name = Attribute("Mandatory")

    # the task event queue
    task_event_queue = Attribute("Mandatory")

    # the task event queue
    task_event_queue = Attribute("Mandatory")

    # the task finish flag
    is_finished = Attribute("Mandatory")

    # the task play flag
    is_playing = Attribute("Mandatory")

    # the task play flag
    is_playing = Attribute("Mandatory")

    # the task pulse values
    max_pulse = Attribute("Mandatory")
    current_pulse = Attribute("Mandatory")
    fraction_step = Attribute("Mandatory")

    # the task remove callback
    remove_callback = Attribute("Mandatory")

    # the task remove callback
    finish_callback = Attribute("Mandatory")

    # the task max pulse setting method
    set_max_pulse = Attribute("Mandatory")

    # the task pulse method
    pulse = Attribute("Mandatory")

    # the task play/pause methods
    on_play = Attribute("Mandatory")
    play = Attribute("Mandatory")

    # the task stop/finish methods
    on_stop = Attribute("Mandatory")
    stop = Attribute("Mandatory")
    finish = Attribute("Mandatory")
    set_progress_end_state = Attribute("Mandatory")

    # the task remove methods
    on_remove = Attribute("Mandatory")
    remove = Attribute("Mandatory")

    # the task text/label update methods
    set_title = Attribute("Mandatory")
    set_text = Attribute("Mandatory")
