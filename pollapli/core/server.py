from twisted.application.service import Application
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

application = Application("Pollapli")
logfile = DailyLogFile("pollapli.log", ".")#"/tmp")
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)