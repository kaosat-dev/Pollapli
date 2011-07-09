class PrintTask():
    def __init__(self,printFile):
        self.saveSensorData=False
        self.printFile=printFile
        self.printFilePath=os.path.join(self.rootPath,"data","printFiles",printFile)
        self.lineIndex=0
        self.lineCount=0
        self.curentLine=None
        
    def start(self):
        f=file(self.printFilePath,"r")
        reactor.callLater(0,PrintStepAction,f)
        
    def stop(self):
        pass
    
    def _getLineCount(self):
        d=defer.Deferred()
        def countLines(result):
            f=file(self.printFilePath,"r")
            for line in f:
                self.lineCount+=1
            f.close()
        d.addCallback(countLines)
        reactor.callLater(0.2,d.callback)
        return d
        
    def action_done(self,result):
        """gets called when an actions is finished """
        self.totalTime+=time.time()-self.startTime
        self.startTime=time.time()
        
        
        
        
        if isinstance(result,Failure):
            self.progress=100
        else:
            line,position=result
            self.lineIndex+=1
            """progress need to be computed base on the number of actions needed for this task to complete"""
            self.progress+=self.progressFraction
            self._do_action_step()
        #need to set status somewhere
        #self.status="F"
        #self.events.OnExited(self,"OnExited")
                 
            
""""
should a printstep action return a specific data structure ? for exam^ple :
- 3D data from parsing
- treated gcode ?
 should  things like the gcode history be stored in the action or the task (i say the task,
 since an action is not supposed to be aware of the tasks global state
 -vectors/positions should be normalized
 things that seem to belong in the task,not the action:
    if z!=self.currentLayerValue:
                            self.currentLayer+=1
                            self.currentLayerValue=z
                            self.pointCloud.add_point(Point(x/20,y/20,z/20)) 
"""
    
class PrintStepAction():
    def __init__(self,task,source):
        self.source=source
        self.line=None
        self.gcodeParser=None
        self.task=task
        
    def __call__(self,printfile):
        """
        gets the next line in the gCode file, sends it via serial, updates the logFile
        and then increments the currentLine counter
        """
        d=defer.Deferred()
        def parseAndSend():
            try:
                line=printfile.next()      
                self.line=line
                self.lastLine=line
                if line!= "":    
                    #this might need to be moved to the task
                    self.connector.add_command(line,answerRequired=True)                              
                    self.logger.debug("Sent command "+ line)
                    self.currentLine+=1
                    pos=self.gcodeParser.parse(line)
                    if pos:
                        try:
                            x=float(pos.xcmd.value.to_eng_string())
                            y=float(pos.ycmd.value.to_eng_string())
                            z=float(pos.zcmd.value.to_eng_string())         
                        except Exception as inst:
                            self.logger.debug("failed to add point to movement map %s",str(inst))  
                #reactor.callLater(0,truc,f)
                """this action returns a tuple of the current line + the parsed position"""
                return (line,pos)
            except StopIteration:
                print("at end of file")
            
        return d
        
       
                    
                    
