class ErrorMessage(object):
    def __init__(self,responseCode,errorCode,errorMessage):
        self.responseCode=responseCode
        self.errorCode=errorCode
        self.errorMessage=errorMessage
    def _toDict(self):
        return {"error":{"errorCode":self.errorCode,"errorMessage":self.errorMessage}} 
         
class ExceptionConverter(object):
    """Utility class that converts an exception to an errorCode/errorMessage tuple
    This is meant only to have a standardized responseCode/errorCode/errorMessage combo for the 
    rest api 
    """
    def __init__(self):
        self.exceptionsToCodes={}
    def add_exception(self,exceptionClass,responseCode,errorCode,errorMessage):
        self.exceptionsToCodes[exceptionClass]=ErrorMessage(responseCode,errorCode,errorMessage)
       
    def get_exception(self,exceptionInstance):
        print(exceptionInstance)
        if exceptionInstance:     
            if exceptionInstance in self.exceptionsToCodes:
                return self.exceptionsToCodes[exceptionInstance]
            else:
                return ErrorMessage(500,0,str(exceptionInstance))
        else:
           return ErrorMessage(500,-1,"Other Error") 
    def get_exceptionList(self):
        return self.exceptionsToCodes.keys()