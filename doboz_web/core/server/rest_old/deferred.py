import traceback
import logging

class Failure(object):
    def __init__(self,excpt=None):
        self.exception=excpt
        
def passthru(arg):
    return arg
    
class Deferred(object):
    """
    Once again a class to ease transition to twisted
    Basically it has the same functionallity as a twisted defered
    (including callbacks and errbacks)
    except, well, its synch instead of asynch (yeah , weird and damned,but temporary)
    """
    def __init__(self):
        self.logger=logging.getLogger("dobozweb.core.server.rest.deferred")
        self.callbacks=[] 
        self.result=None
                     
   
    def start(self,result=None):
        self.result=result
        self._runCallbacks()
        
    def _runCallbacks(self):
        while self.callbacks:
            current=self.callbacks.pop(0)
            callback,args,kwargs=current[isinstance(self.result, Failure)]
            args=args or ()
            kwargs=kwargs or {}
            if  isinstance(self.result,Deferred):
                self.result=self.result.result
            print("result",self.result,"args",args,"kwargs",kwargs)
            try:
                
                self.result=callback(self.result,*args,**kwargs)
            except Exception as inst:
                print("ERROR in defered:",inst)
                self.result=Failure(inst)
                
    def add_callbacks(self,callback,errback=None,callbackArgs=None,callbackKeywords=None,errbackArgs=None, errbackKeywords=None):
        cbs=((callback,callbackArgs,callbackKeywords),(errback or (passthru),errbackArgs,errbackKeywords))
        #print("adding callback args:",callbackArgs,callbackKeywords)
        self.callbacks.append(cbs)
    
    def add_callback(self,callback,*callbackArgs,**callbackKeywords):
        
        self.add_callbacks(callback,callbackArgs=callbackArgs,callbackKeywords=callbackKeywords)
        
    def add_errback(self,errback,*errbackArgs,**errbackKeywords):
        self.add_callbacks(passthru,errback,errbackArgs=errbackArgs,errbackKeywords=errbackKeywords)
        
    def add_both(self,callback,*callbackArgs,**callbackKeywords):
        self.add_callbacks(callback,callback,callbackArgs,callbackKeywords,callbackArgs,callbackKeywords)
        
    def __call__(self):
        pass