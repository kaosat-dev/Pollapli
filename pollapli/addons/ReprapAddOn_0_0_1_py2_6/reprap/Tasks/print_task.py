"""parsing and printing a gcode/other reprap file"""
from __future__ import division
import os
import time
import logging
from twisted.internet import reactor, defer
from twisted.python import log,failure

from pollapli.exceptions import InvalidFile
from pollapli.addons.ReprapAddOn_0_0_1_py2_6.reprap.Tools.gcode_parser import GCodeParser
from pollapli.core.logic.tasks.task import Task


class ActionStatus(object):
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
        self.is_paused = True  # should it be paused or should is running be set  to false?
        self.is_started = False

    def update_progress(self, value=None, increment=None):
        if value:
            self.progress = value
        elif increment:
            self.progress += increment
        else:
            self.progress += self.progress_increment

        self.total_time = time.time() - self.start_time
        if self.progress == 100:
            self.is_paused = True  # should it be paused or should is running be set  to false?
            self.is_started = False


class PrintTask(Task):
    """"
    should a printstep action return a specific data structure ? for example :
    - 3D data from parsing
    - treated gcode ?
     should  things like the gcode history be stored in the action or the task 
     (i say the task,
     since an action is not supposed to be aware of the tasks global state
     -vectors/positions should be normalized
     things that seem to belong in the task,not the action:
    if z!=self.currentLayerValue:
    self.currentLayer+=1
    self.currentLayerValue=z
    self.point_cloud.add_point(Point(x/20,y/20,z/20))
    """

    def __init__(self, parent=None, print_file=None, file_type="gcode", params=None):
        Task.__init__(self, parent)
        self.params = params
        self.status = ActionStatus()
        self.file_type = file_type
        self.print_file_name = print_file
        self.print_file_path = None
        self.print_file = None

        self.line = ""
        self.line_index = 0
        self.line_count = 0
        self.curent_line = None
        self.file_parser = None
        self.start_time = 0

        if file_type == "gcode":
            self.file_parser = GCodeParser()
        self.point_cloud = []

    def setup(self, params={}, *args, **kwargs):
        self.print_file_name = params.get("file")
        self.file_type = params.get("file_type")
        self.params = params
        self.print_file_path = os.path.join("FileManager.rootDir", "printFiles", self.print_file_name)
        if self.file_type == "gcode":
            self.file_parser = GCodeParser()
        log.msg("Print action setup: file", self.print_file_name, "type", self.file_type, "filepath", self.print_file_path, \
        "file_parser", self.file_parser, system="Action", logLevel=logging.DEBUG)

    @defer.inlineCallbacks
    def start(self):
        """begin the task
        status.is_started : only allow start if not already started
        """
        if not self.status.is_started:
            self.status.start()

            def do_start(result):
                self.start_time = time.time()
                self.print_file = file(self.print_file_path, "r")
                self.point_cloud = []
                self._do_step(self.print_file).addBoth(self._step_done)
            yield self._getLineCount().addCallback(do_start)

    def pause(self):
        deferred = defer.Deferred()

        def do_pause_unpause(result):
            if self.status.is_paused:
                self.status.is_paused = False
                self._do_step(self.print_file).addBoth(self._step_done)
            else:
                self.status.is_paused = False

        deferred.addCallback(do_pause_unpause)
        reactor.callLater(0, deferred.callback, None)
        return deferred

    def stop(self):
        """stop the print"""
        deferred = defer.Deferred()

        def do_stop(result):
            self.status.stop()
            self.print_file.close()
            return self.status

        deferred.addCallback(do_stop)
        reactor.callLater(0, deferred.callback, None)
        return deferred

    def _getLineCount(self):
        """sets the total line count"""
        deferred = defer.Deferred()

        def count_lines(result):
            """counts the line in the gcode file"""
            line_count = 0
            try:
                print_file = file(self.print_file_path, "r")
                for line in print_file:
                    line_count += 1
                print_file.close()
                self.line_count = result
                self.status.progress_increment = float(1 / self.line_count) * 100
                log.msg("Total Lines in file", self.line_count, logLevel=logging.INFO)
            except Exception as inst:
                log.msg("Failed to get lines in file", logLevel=logging.CRITICAL)
                raise InvalidFile()
            return line_count
        deferred.addCallback(count_lines)
        reactor.callLater(0.1, deferred.callback, None)
        return deferred

    def _data_recieved(self, data, *args, **kwargs):
        log.msg("Print action recieved ", data, args, kwargs, logLevel=logging.DEBUG)
        if self.status.is_started:
            self._do_step(self.print_file).addBoth(self._step_done)

    def _step_done(self, result):
        """gets called when an actions is finished """
        if isinstance(result, failure.Failure):
            self.print_file.close()
            self.status.update_progress(value=100)
            log.msg("Finished print action. Status:", str(self.status), system="PrintAction", logLevel=logging.CRITICAL)
            #raise event "action finished"
            #self.parentTask._send_signal("action"+self.id+".actionDone")
        else:
            line, position = result
            self.point_cloud.append(position)
            self.line_index += 1
            self.status.update_progress()
            log.msg("Finished print action step. Status:", str(self.status), system="PrintAction", logLevel=logging.CRITICAL)

            if self.line_index % 1000 == 0:
                log.msg("1000 steps done in", time.time() - self.start_time, "s", logLevel=logging.CRITICAL)
                self.start_time = time.time()

    def _do_step(self, print_file):
        """
        gets the next line in the gCode file, sends it via serial
        and then increments the currentLine counter
        this action returns a tuple of the current line + the parsed position
        The sending of data to the driver might need to be moved elsewhere
        * we also need to specify WHO sent the request to the driver,
        * channels need to have some notion of id ?
        * what of these ?
            * self.connector.add_command(line,answerRequired=True)
            * send_command(self,data,sender=None):
        """
        deferred = defer.Deferred()

        def parse_and_send(print_file):
            if self.status.is_started and not self.status.is_paused:
                line = print_file.next()
                if line != "":
                    line = line.replace('\n', '')
                    #self.parentTask._send_signal(self.parentTask.driverChannel+".addCommand", line, True)
                    log.msg("Task", self.cid, "sent signal addCommand to node's driver", logLevel=logging.DEBUG)
                    pos = self.file_parser.parse(line)
                return (line, pos)

        deferred.addCallback(parse_and_send)
        reactor.callLater(0, deferred.callback, print_file)
        return deferred
