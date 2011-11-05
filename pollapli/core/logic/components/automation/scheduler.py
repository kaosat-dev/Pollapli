import logging, uuid, pkgutil,zipfile ,os,sys,json,shutil,time,traceback,datetime
from zipfile import ZipFile
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver

class Schedule(object):
    def __init__(self):
        self._seconds=seconds
        self._minutes=minutes
        self._hours=hours
        self._months=months
        
        self._hods=hods# hours of the day
        self._dows=dows# days of the week
        self._doms=doms# days of the month
    
    
class ScheduledCall(object):
    def __init__(self,callback,startTime,repeatTime=None):  
        self.startTime=startTime
        self.repeatTime=repeatTime
        self._lastTime=None
        self.callback=callback
        self.running=False
             
    def start(self):
        if self.running:
            raise Exception("Scheduled call is already running")
        self.deferred=defer.Deferred()
        return self.deferred
    
    def stop(self):
        pass
    
    def _next_time(self):
        interval=0
        
    def _reschedule(self):
        delay=self._next_time()
        self._lastTime=reactor.seconds()
        self.call=reactor.callLater(delay,self.callback)

class Scheduler(object):
    cls.updateCheck= task.LoopingCall(cls.refresh_updateList)
    cls.updateCheck.start(interval=240,now=False)