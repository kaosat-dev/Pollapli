import logging, uuid, pkgutil,zipfile ,os,sys,json,shutil,time,traceback,datetime
from zipfile import ZipFile
from twisted.internet import reactor, defer,task
from twisted.python import log,failure
from twisted.python.log import PythonLoggingObserver


class Schedule(object):
    _seconds=None
    _minutes = None
    _hours = None
    _doms = None # days of the month
    _months = None
    _dows = None # days of the week

class Scheduler(object):
    cls.updateCheck= task.LoopingCall(cls.refresh_updateList)
    cls.updateCheck.start(interval=240,now=False)