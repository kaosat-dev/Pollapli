import os, logging, sys, shutil
from twisted.trial import unittest
from twisted.enterprise import adbapi 
from twisted.internet import reactor, defer
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver
from pollapli.core.logic.tools.signal_system import SignalDispatcher


class Test_Signal_System(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_with_basic_message(self):
        iSignalDispatcher = SignalDispatcher("test_channel")
        def signalHandler(signal=None,sender=None,realsender=None,data=None,time=None,*args,**kwargs):
            self.assertEquals(signal,"just a test message")
            self.assertEquals(sender,"test_channel")
        iSignalDispatcher.add_handler(channel="test_channel",handler=signalHandler)
        iSignalDispatcher.send_message("just a test message")
        
    def test_with_complex_message(self):
        iSignalDispatcher = SignalDispatcher("test_channel")
        def signalHandler(signal=None,sender=None,realsender=None,data=None,time=None,*args,**kwargs):
            self.assertEquals(signal,"just a test message")
            self.assertEquals(sender,"test_channel")
            self.assertEquals(realsender,self)
            self.assertEquals(data, 42)
        iSignalDispatcher.add_handler(channel="test_channel",handler=signalHandler)
        iSignalDispatcher.send_message("just a test message",self,42)
        
    