"""
.. py:module:: task
   :synopsis: main module of tasks (automation): task , task and action status, task manager etc.
"""
from pollapli.core.base.base_component import BaseComponent
import time


class TaskStatus(object):
    def __init__(self, progress_increment=0, progress=0):
        self.is_started = False
        self.is_paused = False
        self.progress_increment = progress_increment
        self.progress = progress
        self.start_time = 0
        self.total_time = 0

    def start(self):
        self.is_started = True
        self.is_paused = False
        self.progress = 0
        self.start_time = time.time()

    def stop(self):
        """
        sets the status to stopped
        should it be paused or should is running be set  to false?
        """
        self.is_paused = True
        self.is_started = False

    def update_progress(self, value=None, increment=None):
        """updates the progress
        :param is_paused: should it be paused or should is running be set
        to false ?
        """
        if value:
            self.progress = value
        elif increment:
            self.progress += increment
        else:
            self.progress += self.progress_increment

        self.total_time = time.time() - self.start_time
        if self.progress == 100:
            self.is_paused = True
            self.is_started = False


class Task(BaseComponent):
    """
    Base class for tasks
    """
    def __init__(self, parent=None, name="Default Task", description="Default task description", target=None, *args, **kwargs):
        """progress need to be computed base on the number of actions needed
        for this task to complete"""
        BaseComponent.__init__(self, parent)
        self.name = name
        self.description = description
        self.status = TaskStatus()
        self.target = target

    def __eq__(self, other):
        return (self.cid == other.cid and self.name == other.name and
                self.description == other.description and
                self.status == other.status and self.target == other.target)

    def __ne__(self, other):
        return not self.__eq__(other)

    def setup(self):
        pass

    def start(self):
        """starts the task"""
        raise NotImplementedError()

    def stop(self):
        """stops the task: this is a definitive stop, not for pausing"""
        raise NotImplementedError()

    def add_action(self):
        pass

    def add_condition(self):
        pass
    
    
