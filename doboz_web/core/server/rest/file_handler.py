from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class FilesRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost"):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        
    def render_GET(self, request):
        self.logger.critical("Using files GET handler")
        callback=request.GET.get('callback', '').strip()
        response=callback+"()"
        fileList=os.listdir(os.path.join(server.rootPath,"files","machine","printFiles"))
        try:     
            finalFileList=map(self.fullPrintFileInfo, fileList)
            data={"files": finalFileList }
            response=callback+"("+str(data)+")"
        except Exception as inst:    
            self.logger.critical("error in file list generation  %s",str(inst))
            self.logger.critical("response %s",str(response))
        return response  
#        if request.headers.get("Content-Type")=="application/json":
#            callback=request.GET.get('callback', '').strip()
#            resp=""
#            #response=callback+"()"
#            try:
#                envData=self.environmentManager.get_environments()
#                thingy=[]
#                for env in envData:
#                    
#                    lnk='{"link" : {"href":"'+self.rootUri+str(env.id)+'", "rel": "environment"},'
#                    thingy.append(lnk+env._toJson()+'}')
##                   
#                resp=callback+'{"Environments List":{"link":{"href":"'+self.rootUri+'", "rel": "environments"}},"items":['+','.join(thingy)+']}'
#            except Exception as inst:
#                self.logger.exception("Error in envs get %s",str(inst))
#                abort(500,"error in getting environments")
#            response.content_type = 'application/json'
#            return resp
#        else:
#            abort(501,"Not Implemented")
            
    def render_POST(self,request):
        try:       
            datafile = request.params["datafile"]
            self.uploadProgress=0
            saved_file=open(os.path.join(server.rootPath,"files","machine","printFiles",datafile.filename),'w')
            saved_file.write(datafile.value)
            saved_file.close()
            self.uploadProgress=100
#            env=self.environmentManager.add_environment(**self._fetch_jsonData(request))
#            resp=""
#            if env:
#                lnk='{"link" : {"href":"'+self.rootUri+str(env.id)+'", "rel": "environment"},'
#                resp='{"Environment":'+lnk+env._toJson()+'}}'
#            else:
#                response.status=500
#                error='{"error":{"id":0,"message":"failed to create environment"}}'
#                resp='{"Environments":'+error+'}'
            
        except Exception as inst:
            self.logger.critical("error %s",str(inst))
            response.status=500
            #error='{"error":{"id":0,"message":"failed to create environment"}}'
            #resp='{"Environments":'+error+'}'
        finally:
            pass#return resp
            
    def render_DELETE(self,request):
        try:
            fileName=request.params["filename"].strip()
            filePath=os.path.join(server.rootPath,"files","machine","printFiles",fileName)
            os.remove(filePath)
            self.logger.critical("Deleted file: %s",fileName)
        except Exception as inst:
            self.logger.critical("file deletion error %s",str(inst))
            abort(500,"Failed to delete file")
            
    def fullPrintFileInfo(self,file):
        return {"fileName":str(file),"modDate": str(time.ctime(os.path.getmtime(os.path.join(server.rootPath,"files","machine","printFiles",file))))}
