"""
"""
from zope.interface import Interface, Attribute

class IProgress(Interface):
    """
    """
    # factory init flag
    initialized = Attribute("Mandatory")

    # task dict for the progress
    task_dict = Attribute("Mandatory")

    # add task method
    add_task = Attribute("Mandatory")

    # start task method
    start_task = Attribute("Mandatory")

    # stop task method
    stop_task = Attribute("Mandatory")

    # stop all task method
    stop_all_tasks = Attribute("Mandatory")

    # remove task method
    remove_task = Attribute("Mandatory")

    # remove all task method
    remove_all_tasks = Attribute("Mandatory")

    # pulse task method
    pulse = Attribute("Mandatory")

    # task finish method
    task_finish = Attribute("Mandatory")
