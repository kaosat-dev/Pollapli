"""parsing and printing a gcode/other reprap file"""
from __future__ import division
import os
import time
import logging
from twisted.internet import reactor, defer, threads
from twisted.python import log
from pollapli.exceptions import InvalidFile
from pollapli.addons.ReprapAddOn.reprap.tools.gcode_parser import GCodeParser
from pollapli.core.logic.tasks.task import Task
from twisted.internet.task import deferLater


class ReprapPrintTask(Task):
    """"
    Task for 3d printing from a file : typically from a gcode file
     should  things like the gcode history be stored in the action or the task
     (i say the task,
     since an action is not supposed to be aware of the tasks global state
     -vectors/positions should be normalized
    Things that need to be put somewhere:
    if z!=self.currentLayerValue:
    self.currentLayer+=1
    self.currentLayerValue=z
    self.point_cloud.add_point(Point(x/20,y/20,z/20))
    self.print_file_path =
     os.path.join("FileManager.rootDir", "printFiles", self.print_file_name)
    """
    def __init__(self, parent=None, name="Print Task", description="A Print task, for repraps & co", target=None, file_name=None, file_type="gcode"):
        Task.__init__(self, parent, name, description, target)
        self.file_type = file_type
        self.print_file_name = file_name
        self.print_file_path = file_name
        self.print_file = None

        self.line = ""
        self.line_index = 0
        self.line_count = -1
        self.curent_line = None
        self.file_parser = None
        self.start_time = 0

        if file_type == "gcode":
            self.file_parser = GCodeParser()
        self.deferred = None
        self.current_loop_deferred = None
        self._is_processing = True

    def setup(self):
        log.msg("Print task setup: file", self.print_file_name, "type", \
                 self.file_type, "filepath", self.print_file_path, \
                 "file_parser", self.file_parser, system="Action", \
                  logLevel=logging.DEBUG)

    def start(self):
        """begin the task
        raise an exception if already started
        """
        if self.status.is_started:
            raise Exception("Task already started")

        def do_start():
            self.start_time = time.time()
            self.status.start()
            log.msg("Started print task %s at %f s" % (str(self.cid), self.status.start_time), system="Task", logLevel=logging.CRITICAL)
            self.run()

        self.deferred = defer.Deferred()
        deferLater(reactor, 0, do_start)
        return self.deferred

    @defer.inlineCallbacks
    def pause(self):
        """pause the task : might be delayed slightly
        if the previous run loop is not complete"""

        log.msg("Pausing Task %s" % (self.cid), system="Task", logLevel=logging.DEBUG)
        self.status.is_paused = True
        if self.current_loop_deferred is not None:
            yield self.current_loop_deferred

    @defer.inlineCallbacks
    def resume(self):
        """resumes the task : might be delayed slightly
        if the previous run loop is not complete"""

        log.msg("Resuming Task %s" % (self.cid), system="Task", logLevel=logging.DEBUG)
        self.status.is_paused = False
        if self.current_loop_deferred is not None:
            yield self.current_loop_deferred
        if not self._is_processing:
            self.run()

    @defer.inlineCallbacks
    def stop(self):
        """stop the print"""
        if self.current_loop_deferred is not None:
            yield self.current_loop_deferred
        self._cleanup()
        self.deferred.callback(None)

    @defer.inlineCallbacks
    def run(self):
        """main method for the task
        handles command parsing, sending and recieving
        """
        yield self._setup_run()
        while not self.status.is_paused and self.status.is_started and not self.status.is_finished:
            self._is_processing = True
            if self.current_loop_deferred is None:
                    self.current_loop_deferred = defer.Deferred()
            try:
                line = self.print_file.next()
                self.curent_line = line
                self.line_index += 1
                log.msg("Print task line: %s" % (str(line).strip()), system="Task", logLevel=logging.DEBUG)
                self.status.update_progress()
                if self.line_index % 1000 == 0:
                    log.msg("1000 lines done in %f s in task %s" % (time.time() - self.start_time, str(self.cid)), system="Task", logLevel=logging.INFO)
                    self.start_time = time.time()
                try:
                    command = self.file_parser.parse(line)
                    command.sender = self
                    command.device = self.target
                    command_result = yield command.run()
                except Exception as inst:
                    log.msg("Error %s In Task %s" % (str(inst), self.cid), system="Task", logLevel=logging.DEBUG)

                self.current_loop_deferred.callback(command_result)
                self.current_loop_deferred = defer.Deferred()
                self._is_processing = False

            except StopIteration as inst:
                self._cleanup(max_progress=True)
                break

    @defer.inlineCallbacks
    def _setup_run(self):
        """setup all required elements for run"""
        if not self.status.is_finished and self.line_count == -1:
            try:
                yield self._get_line_count()
                if self.print_file is None:
                    self.print_file = file(self.print_file_path, "r")
            except Exception as inst:
                if not self.deferred.called:
                    self.status.is_finished = True
                    self.deferred.errback(inst)

    def _cleanup(self, max_progress=False):
        """cleanup code : close open file etc"""
        self.status.stop()
        if self.print_file is not None:
            self.print_file.close()
        if max_progress:
            self.status.update_progress(value=100)
        log.msg("Finished print task %s in %f s" % (str(self.cid), self.status.total_time), system="Task", logLevel=logging.CRITICAL)
        self.deferred.callback(None)

    def _get_line_count(self):
        """gets the total line count in the file"""
        def count_lines():
            """counts the line in the gcode file"""
            try:
                print_file = file(self.print_file_path, "r")
                self.line_count = sum(1 for line in print_file)
                print_file.close()
                self.status.progress_increment = float(1 / self.line_count) * 100
                log.msg("Total Lines in file", self.line_count, logLevel=logging.INFO)
                return self.line_count
            except Exception as inst:
                log.msg("Error %s Failed to get lines in file" % str(inst), logLevel=logging.CRITICAL)
                raise InvalidFile()

        deferred = threads.deferToThread(count_lines)
        return deferred
