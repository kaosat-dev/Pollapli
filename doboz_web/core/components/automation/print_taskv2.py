class PrintTask():
    def __init__(self):
        self.saveSensorData=False

class PrintStepAction():
    """
    gets the next line in the gCode file, sends it via serial, updates the logFile
    and then increments the currentLine counter
    """
    line=None
    try:
        line = self.source.readline()
        self.line=line
        self.lastLine=line
    except :
        pass
        
        if line is not None: 
            if line!= "":# and line !="\n" and line != "\r\n" and line != "\n\r":
                self.connector.add_command(line,answerRequired=True)             
                try:
                    self.gcodeHistory.insert(self.gcodeHistoryIndex, line)
                    if len(self.gcodeHistory)>self.gcodeHistoryMaxSize:
                        self.gcodeHistoryIndex=0
                except:
                    pass
                """
                Update the logfile with the current Line number
                """

                self.logger.debug("Sent command "+ line)
                self.currentLine+=1
                pos=self.gcodeParser.parse(line)
                if pos:
                    try:
                        #self.position=[pos.xcmd.value.to_eng_string(),pos.zcmd.value.to_eng_string(),pos.ycmd.value.to_eng_string()]
                        x=float(pos.xcmd.value.to_eng_string())
                        y=float(pos.ycmd.value.to_eng_string())
                        z=float(pos.zcmd.value.to_eng_string())
                        if z!=self.currentLayerValue:
                            self.currentLayer+=1
                            self.currentLayerValue=z
                        self.pointCloud.add_point(Point(x/20,y/20,z/20))             
                    except Exception as inst:
                        self.logger.debug("failed to add point to movement map %s",str(inst))
                        
                
                self.totalTime+=time.time()-self.startTime
                self.startTime=time.time()
                
                if self.currentLine==self.totalLines:
                    self.progress=100
                    self.status="F"
                    self.events.OnExited(self,"OnExited")
                else:
                    
                    self.progress+=self.progressFraction
            else:
                print("empty line")
                self.currentLine+=1
                if (self.currentLine)<self.totalLines:
                    self.progress+=self.progressFraction
                   
                    self._do_action_step()
                else:
                    self.progress=100
                    self.status="F"
                    self.events.OnExited(self,"OnExited")
    def __call__(self):
        pass