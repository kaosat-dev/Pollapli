import os
from twisted.trial import unittest
from twisted.internet import defer, reactor, task
from pollapli.addons.ReprapAddOn.reprap.tasks.reprap_print_task import ReprapPrintTask
from pollapli.addons.ReprapAddOn.reprap.tasks.tests.mock_reprap_device import MockReprapDevice
from pollapli.exceptions import InvalidFile

from twisted.python import log
import sys
from twisted.internet.task import deferLater
import logging

logger = logging.getLogger("testlog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

observer = log.PythonLoggingObserver("testlog")
observer.start()
#log.startLogging(sys.stdout)


class TestReprapPrintTask(unittest.TestCase):
    def setUp(self):
        self._gcode_input_file = "test.gcode"
        self._write_input_gcode_file()

    def tearDown(self):
        os.remove(self._gcode_input_file)

    @defer.inlineCallbacks
    def test_run_simple(self):
        target_device = MockReprapDevice()
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
        yield rep_print_task.start()
        exp_progress = 100.0
        obs_progress = rep_print_task.status.progress
        self.assertEquals(obs_progress,exp_progress)

    def test_run_simple_bad_gcode_file(self):
        target_device = MockReprapDevice()
        rep_print_task = ReprapPrintTask(target=target_device, file_name="")
        deferred = rep_print_task.start()
        return self.assertFailure(deferred, InvalidFile)

    def test_stop(self):
        target_device = MockReprapDevice(command_delay=10)
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
        deferred = rep_print_task.start()
        rep_print_task.stop()
        self.assertFalse(rep_print_task.status.is_started)

    def test_pause_simple(self):
        target_device = MockReprapDevice(command_delay=2)
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)

        def pause_and_check():
            rep_print_task.pause()
            self.assertTrue(rep_print_task.status.is_paused)
            self.assertEquals(rep_print_task.curent_line, "G1 X0.25 Y105\n")
            rep_print_task.stop()

        def_1 = deferLater(reactor, 2.1, pause_and_check)
        def_2 = rep_print_task.start()
        return  defer.DeferredList([def_1, def_2])

    def test_pause_at_start(self):
        target_device = MockReprapDevice(command_delay=2)
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)

        deferred = rep_print_task.start()
        rep_print_task.pause()
        self.assertTrue(rep_print_task.status.is_paused)
        self.assertEquals(rep_print_task.curent_line, None)
        rep_print_task.stop()
        return deferred
    
#    def test_pause_unpause(self):
#        exp_lines = ["G0 X10\n", "G1 X0.25 Y105\n", "G1 Z7.25 Y2\n"]
#        target_device = MockReprapDevice(command_delay=2)
#        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
#
#        def pause_and_check(line_index):
#            rep_print_task.pause()
#            self.assertEquals(rep_print_task.curent_line, exp_lines[line_index])
#            rep_print_task.resume()
#
#        def1 = deferLater(reactor, 2.1, pause_and_check, 0)
#        def2 = deferLater(reactor, 4.1, pause_and_check, 1)
#        def3 = deferLater(reactor, 6.1, pause_and_check, 2)
#        deferred = rep_print_task.start()
#        d_list = [def1, def2, def3, deferred]
#        return defer.DeferredList(d_list)

    @defer.inlineCallbacks
    def test_command_delay(self):
        target_device = MockReprapDevice(command_delay=4)
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
        yield rep_print_task.start()
        exp_progress = 100.0
        obs_progress = rep_print_task.status.progress
        self.assertEquals(obs_progress,exp_progress)

    def _write_input_gcode_file(self):
        gcode_input_file = open(self._gcode_input_file, 'w')
        gcode_input_file.write("G0 X10\n")
        gcode_input_file.write("G1 X0.25 Y105\n")
        gcode_input_file.write("G1 Z7.25 Y2\n")
        gcode_input_file.close()
