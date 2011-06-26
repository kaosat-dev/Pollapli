from doboz_web.core.server.rest.base_rest_handler import BaseRestHandler
from doboz_web.core.server.bottle import  response 

class FilesRestHandler(BaseRestHandler):
    def __init__(self,rootUri="http://localhost"):
        BaseRestHandler.__init__(self)
        self.rootUri=rootUri
        
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
