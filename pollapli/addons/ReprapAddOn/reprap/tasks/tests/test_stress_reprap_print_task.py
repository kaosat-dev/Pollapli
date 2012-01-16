import os
from twisted.trial import unittest
from twisted.internet import defer, reactor
from pollapli.addons.ReprapAddOn.reprap.tasks.reprap_print_task import ReprapPrintTask
from pollapli.addons.ReprapAddOn.reprap.tasks.tests.mock_reprap_device import MockReprapDevice
from pollapli.exceptions import InvalidFile

from twisted.python import log
import sys
import logging

logger = logging.getLogger("testlog")
logger.setLevel(logging.CRITICAL)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.CRITICAL)
ch.setFormatter(formatter)
logger.addHandler(ch)

observer = log.PythonLoggingObserver("testlog")
observer.start()
#log.startLogging(sys.stdout)


class TestReprapPrintTask(unittest.TestCase):

    def setUp(self):
        self.timeout = 240
        self._gcode_input_file = "test.gcode"

    def tearDown(self):
        os.remove(self._gcode_input_file)

    @defer.inlineCallbacks
    def test_run_big_input(self):
        self._write_big_input_gcode_file()
        target_device = MockReprapDevice(command_delay=0)
        rep_print_task = ReprapPrintTask(target=target_device, file_name=self._gcode_input_file)
        yield rep_print_task.start()
        exp_progress = 100.0
        obs_progress = rep_print_task.status.progress
        self.assertEquals(obs_progress,exp_progress)

    @defer.inlineCallbacks
    def test_run_big_input_parallel_x4(self):
        self._write_big_input_gcode_file()
        target_device_one = MockReprapDevice(command_delay=0)
        target_device_two = MockReprapDevice(command_delay=0)
        target_device_three = MockReprapDevice(command_delay=0)
        target_device_four = MockReprapDevice(command_delay=0)

        rep_print_task_one = ReprapPrintTask(target=target_device_one, file_name=self._gcode_input_file)
        rep_print_task_two = ReprapPrintTask(target=target_device_two, file_name=self._gcode_input_file)
        rep_print_task_three = ReprapPrintTask(target=target_device_three, file_name=self._gcode_input_file)
        rep_print_task_four = ReprapPrintTask(target=target_device_four, file_name=self._gcode_input_file)

        d1 = rep_print_task_one.start()
        d2 = rep_print_task_two.start()
        d3 = rep_print_task_three.start()
        d4 = rep_print_task_four.start()
        yield defer.DeferredList([d1, d2, d3, d4])

        exp_progress = 100.0
        obs_progress = rep_print_task_one.status.progress
        self.assertEquals(obs_progress, exp_progress)

        obs_progress = rep_print_task_two.status.progress
        self.assertEquals(obs_progress, exp_progress)

        obs_progress = rep_print_task_three.status.progress
        self.assertEquals(obs_progress, exp_progress)

        obs_progress = rep_print_task_four.status.progress
        self.assertEquals(obs_progress, exp_progress)

    @defer.inlineCallbacks
    def test_run_big_input_parallel_x8(self):
        self._write_big_input_gcode_file()
        parrallel_prints = 8
        rep_print_tasks = []
        deffereds = []
        for i in range(parrallel_prints):
            device = MockReprapDevice(command_delay=0)
            task = ReprapPrintTask(target=device, file_name=self._gcode_input_file)
            rep_print_tasks.append(task)
            deffereds.append(task.start())

        yield defer.DeferredList(deffereds)

        exp_progress = 100.0
        for i in range(parrallel_prints):
            task = rep_print_tasks[i]
            obs_progress = task.status.progress
            self.assertEquals(obs_progress, exp_progress)

    def _write_input_gcode_file(self):
        gcode_input_file = open(self._gcode_input_file, 'w')
        gcode_input_file.write("G0 X10\n")
        gcode_input_file.write("G1 X0.25 Y105\n")
        gcode_input_file.write("G1 Z7.25 Y2\n")
        gcode_input_file.close()

    def _write_big_input_gcode_file(self):
        gcode_input_file = open(self._gcode_input_file, 'w')
        [gcode_input_file.write("G1 Z7.25 Y2\n") for i in range(80000)]
        gcode_input_file.close()
