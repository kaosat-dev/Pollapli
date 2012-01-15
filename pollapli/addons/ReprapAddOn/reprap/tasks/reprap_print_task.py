"""parsing and printing a gcode/other reprap file"""
from __future__ import division
import os
import time
import logging
from twisted.internet import reactor, defer
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
    self.print_file_path = os.path.join("FileManager.rootDir", "printFiles", self.print_file_name)
    """

    def __init__(self, parent=None, name="Print Task", description="A Print task, for repraps & co", target=None, file_name=None, file_type="gcode"):
        Task.__init__(self, parent, name, description, target)
        self.file_type = file_type
        self.print_file_name = file_name
        self.print_file_path = file_name
        self.print_file = None

        self.line = ""
        self.line_index = 0
        self.line_count = 0
        self.curent_line = None
        self.file_parser = None
        self.start_time = 0

        if file_type == "gcode":
            self.file_parser = GCodeParser()
        self.deferred = None

    def setup(self):
        log.msg("Print task setup: file", self.print_file_name, "type", self.file_type, "filepath", self.print_file_path, \
        "file_parser", self.file_parser, system="Action", logLevel=logging.DEBUG)

    def start(self):
        """begin the task
        status.is_started : only allow start if not already started
        """

        @defer.inlineCallbacks
        def do_start(result):
            try:
                yield self.get_line_count()
                if not self.status.is_started:
                    self.status.start()
                self.print_file = file(self.print_file_path, "r")
                self.run()
            except Exception as inst:
                if not self.deferred.called:
                    self.deferred.errback(inst)
        self.deferred = defer.Deferred()
        reactor.callLater(0, do_start, None)
        return self.deferred

    def pause(self):
#        deferred = defer.Deferred()
#
#        def do_pause_unpause(result):
        if self.status.is_started:
            if self.status.is_paused:
                self.status.is_paused = False
                self.run()
            else:
                self.status.is_paused = True

#        deferred.addCallback(do_pause_unpause)
#        reactor.callLater(0, deferred.callback, None)
#        return deferred

    def stop(self):
        """stop the print"""
        deferred = defer.Deferred()

        def do_stop(result):
            if self.status.is_started:
                self.status.stop()
                self.print_file.close()
            self.deferred.callback(None)

        deferred.addCallback(do_stop)
        reactor.callLater(0, deferred.callback, None)
        return deferred

    def get_line_count(self):
        """sets the total line count"""
        deferred = defer.Deferred()

        def count_lines():
            """counts the line in the gcode file"""
            try:
                print_file = file(self.print_file_path, "r")
                self.line_count = sum(1 for line in print_file)
                print_file.close()
                self.status.progress_increment = float(1 / self.line_count) * 100
                log.msg("Total Lines in file", self.line_count, logLevel=logging.INFO)
                deferred.callback(self.line_count)
            except Exception as inst:
                log.msg("Error %s Failed to get lines in file" % str(inst), logLevel=logging.CRITICAL)
                #raise InvalidFile()
                deferred.errback(InvalidFile())

#        deferred.addCallback(count_lines)
#        reactor.callLater(0, deferred.callback, None)
#        return deferred
        reactor.callLater(0, count_lines)
        return deferred

    @defer.inlineCallbacks
    def run(self):
        """target : a device instance"""
        if not self.status.is_paused:
            for line_index, line in enumerate(self.print_file.readlines()):
                try:
                    self.line_index = line_index
                    command = self.file_parser.parse(line)
                    command.sender = self
                    command.device = self.target
                    yield command.run()
                    self.status.update_progress()
                    log.msg("Finished print task line. Status:", str(self.status), system="PrintAction", logLevel=logging.DEBUG)
                except Exception as inst:
                    log.msg("Error %s In Task %s" % (str(inst), self.cid), system="Task", logLevel=logging.DEBUG)
                if self.line_index % 1000 == 0:
                    #log.msg("1000 lines done in %is" % (time.time() - self.start_time), logLevel=logging.CRITICAL)
                    self.start_time = time.time()

            self.print_file.close()
            self.status.update_progress(value=100)
            log.msg("Finished print action. Status:", str(self.status), system="PrintAction", logLevel=logging.CRITICAL)
            self.deferred.callback(None)
