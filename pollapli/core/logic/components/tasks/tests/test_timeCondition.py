from twisted.trial import unittest
import datetime
import time
 
class Test_TimeCondition(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_timeCondition_basic(self):
        startTime = datetime.datetime.now()
        interval = "@once"
        schedule = Schedule(startTime=startTime, interval=interval)
        
        iTimeCondition = TimeCondition(schedule=schedule)
        iTimeCondition.addValidationCallback(onValidatedCallBack)
        iTimeCondition.addInvalidationCallback(onInvalidatedCallback)   
        iTimeCondition.enable()
        
        def onValidatedCallBack():
            self.assertEquals(time.time(),startTime)
            self.assertEquals(iTimeCondition.isValid,True)
        
        def onInvalidatedCallback():
            self.assertEquals(iTimeCondition.isValid,False)
        
                
    def test_scheduler_run_interval_manyTimes(self):
        startTime = datetime.datetime.now()
        interval = "* * * * *"
        schedule = Schedule(startTime, interval)
        
        lastCallTime = time.time()
        currentCall = 0
        maxCalls = 5
        
        def methodToCall():
            if currentCall ==0 :
                lastCallTime = startTime
            if currentCall < maxCalls:
                self.assertEquals(time.time(),lastCallTime+repeatTime)
            else:
                iSchedule.stop()
            
        iSchedule = Scheduler(schedule,methodToCall)
        iSchedule.start()
