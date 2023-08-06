"""Some messages for queue status workflow.
"""

class Message(object):
    """Base message to communicate between queues.
    """
    def __init__(self, id_):
        """Init with a taskbox id for multi task management.
        """
        self.id_ = id_

class TaskMessage(Message):
    """Specific message for taskbox communication.
    """
    pass

class Pause(TaskMessage):
    """Pause message for taskbox.
    """
    pass

class Play(TaskMessage):
    """Play message for taskbox.
    """
    pass

class Stop(TaskMessage):
    """Stop message for taskbox.
    """
    pass
