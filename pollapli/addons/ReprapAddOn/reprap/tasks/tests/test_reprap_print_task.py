import os
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn.reprap.tasks.reprap_print_task import ReprapPrintTask
from pollapli.addons.ReprapAddOn.reprap.tasks.tests.mock_reprap_device import MockReprapDevice
from pollapli.exceptions import InvalidFile


class TestReprapPrintTask(unittest.TestCase):
    def setUp(self):
        self._gcode_input_file = "test.gcode"
        self._write_input_gcode_file()

    def tearDown(self):
        os.remove(self._gcode_input_file)

#    @defer.inlineCallbacks
#    def test_run_simple(self):
#        target_device = MockReprapDevice()
#        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
#        yield rep_print_task.start()
#        exp_progress = 100.0
#        obs_progress = rep_print_task.status.progress
#        self.assertEquals(obs_progress,exp_progress)

    def test_run_simple_bad_gcode_file(self):
        target_device = MockReprapDevice()
        rep_print_task = ReprapPrintTask(target=target_device, file_name="")
        deferred = rep_print_task.start()
        return self.assertFailure(deferred, InvalidFile)

#    @defer.inlineCallbacks
#    def test_stop(self):
#        target_device = MockReprapDevice(command_delay=10)
#        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
#        deferred = rep_print_task.start()
#        yield rep_print_task.stop()
#
#        self.assertFalse(rep_print_task.status.is_started)

#    def test_pause_unpause(self):
#        target_device = MockReprapDevice(command_delay=2)
#        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
#        deferred = rep_print_task.start()
#        rep_print_task.pause()
#        self.assertTrue(rep_print_task.status.is_paused)
#        rep_print_task.pause()
#        self.assertFalse(rep_print_task.status.is_paused)
#        return deferred
#        yield rep_print_task.pause()
#        self.assertTrue(rep_print_task.status.is_paused)

    def _write_input_gcode_file(self):
        gcode_input_file = open(self._gcode_input_file, 'w')
        gcode_input_file.write("G0 X10\n")
        gcode_input_file.write("G1 X0.25 Y105\n")
        gcode_input_file.write("G1 Z7.25 Y2\n")
        gcode_input_file.close()
