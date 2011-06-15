import logging
import os
import sys
import time
import datetime
import socket
import json

from bottle import Bottle, route, run, send_file, redirect, abort, request, response,Response, debug
import bottle
from doboz_web.core.components.automation.print_task import PrintTask
from doboz_web.core.components.automation.scan_task import ScanTask
from doboz_web.core.components.automation.transition_task import TransitionTask
from doboz_web.core.components.automation.timer_task import TimerTask

from doboz_web.core.server.rest.envs_handler import EnvsRestHandler
from doboz_web.core.server.rest.env_handler import EnvRestHandler
from doboz_web.core.server.rest.nodes_handler import NodesRestHandler
from doboz_web.core.server.rest.node_handler import NodeRestHandler
from doboz_web.core.server.rest.connector_handler import ConnectorRestHandler
from doboz_web.core.server.rest.connector_status_handler import ConnectorStatusRestHandler
from doboz_web.core.server.rest.tasks_handler import TasksRestHandler
from doboz_web.core.server.rest.task_handler import TaskRestHandler
server = Bottle()
server.rootPath=os.path.join(os.path.abspath("."),"core","server")
server.logger=logging.getLogger("dobozweb.core.WebServer")

"""Helper functions"""

def fullPrintFileInfo(file):
    return {"fileName":str(file),"modDate": str(time.ctime(os.path.getmtime(os.path.join(server.rootPath,"files","machine","printFiles",file))))}



@server.route('/files' , method='GET')
def files_get():
    #request.params["callback"].strip()
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    fileList=os.listdir(os.path.join(server.rootPath,"files","machine","printFiles"))
    try:     
        finalFileList=map(fullPrintFileInfo, fileList)
        data={"files": finalFileList }
        response=callback+"("+str(data)+")"
    except Exception as inst:    
        server.logger.critical("error in file list generation  %s",str(inst))
    server.logger.critical("response %s",str(response))
    return response  
  
@server.route('/files' , method='POST')
def files_post():
    datafile = request.params["datafile"]
    print("filename",datafile.filename)
    try:
        server.uploadProgress=0
        saved_file=open(os.path.join(server.rootPath,"files","machine","printFiles",datafile.filename),'w')
        saved_file.write(datafile.value)
        saved_file.close()
        server.uploadProgress=100
    except Exception as inst:
        server.logger.critical("error %s",str(inst))
    
@server.route('/files' , method='PUT')
def files_put():
    print("puting to file list")
    
@server.route('/files' , method='DELETE')
def files_delete():
    fileName=request.params["filename"].strip()
    try:
        filePath=os.path.join(server.rootPath,"files","machine","printFiles",fileName)
        os.remove(filePath)
        server.logger.critical("Deleted file: %s",fileName)
    except Exception as inst:
        server.logger.critical("error %s",str(inst))
        abort(500,"Error in attempting to delete files")
    
            
@server.route('/environments' , method='ANY')
@server.route('/environments/' , method='ANY')
def handle_envs():
    envsHandler=EnvsRestHandler(server.environmentManager)
    return envsHandler._handle(request) 


@server.route('/environments/:envId' , method='ANY')
@server.route('/environments/:envId/' , method='ANY')
def handle_env(envId):
    envHandler=EnvRestHandler(server.environmentManager,int(envId))
    return envHandler._handle(request)


@server.route('/environments/:envId/nodes' , method='ANY')
@server.route('/environments/:envId/nodes/' , method='ANY')
def handle_nodes(envId):
    nodesHandler=NodesRestHandler(server.environmentManager,int(envId))
    return nodesHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/' , method='ANY')
def handle_node(envId,nodeId):
    nodeHandler=NodeRestHandler(server.environmentManager,int(envId),int(nodeId))
    return nodeHandler._handle(request)


@server.route('/environments/:envId/nodes/:nodeId/connector' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/connector/' , method='ANY')
def handle_connector(envId,nodeId):
    connectorHandler=ConnectorRestHandler(server.environmentManager,int(envId),int(nodeId))
    return connectorHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId/connector/status' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/connector/status/' , method='ANY')
def handle_connector_status(envId,nodeId):
    connectorStatusHandler=ConnectorStatusRestHandler(server.environmentManager,int(envId),int(nodeId))
    return connectorStatusHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId/tasks' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/tasks/' , method='ANY')
def handle_tasks(envId,nodeId):
    tasksHandler=TasksRestHandler(server.environmentManager,int(envId),int(nodeId))
    return tasksHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/' , method='ANY')
def handle_task(envId,nodeId,taskId):
    taskHandler=TaskRestHandler(server.environmentManager,int(envId),int(nodeId),int(taksId))
    return taskHandler._handle(request)


@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/status' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/status/' , method='ANY')
def handle_task_status(envId,nodeId,taskId):
    pass
    #taskHandler=TaskRestHandler(server.environmentManager,int(envId),int(nodeId),int(taksId))
    #return taskHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/condtions' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/condtions/' , method='ANY')
def handle_task_conditions(envId,nodeId,taskId):
    pass#taskHandler=TaskRestHandler(server.environmentManager,envId,int(nodeId),int(taksId))
    #return taskHandler._handle(request)

@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/actions' , method='ANY')
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/actions/' , method='ANY')
def handle_task_actions(envId,nodeId,taskId):
    pass#taskHandler=TaskRestHandler(server.environmentManager,int(envId),int(nodeId),int(taksId))
    #return taskHandler._handle(request)
#############################################
  
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/conditions' , method='GET')
def task_conditions_get(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).get_conditions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envId,int(nodeId), str(inst))       
 
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/conditions' , method='POST')
def task_conditions_post(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).add_condition(**params)
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envId,int(nodeId), str(inst))       

@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/conditions' , method='DELETE')
def task_conditions_delete(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).clear_conditions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envId,int(nodeId), str(inst))       


        
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/actions' , method='GET')
def task_actions_get(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).get_actions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envId,int(nodeId), str(inst))       
 
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/actions' , method='POST')
def task_actions_post(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).add_action(**params)
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envId,int(nodeId), str(inst))       

@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/actions' , method='DELETE')
def task_actions_delete(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).clear_actions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envId,int(nodeId), str(inst))       
    
        
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/start' , method='POST')
def task_start(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).start_task(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task start: error: %s",envId,int(nodeId), str(inst))
    
@server.route('/environments/:envId/nodes/:nodeId/tasks/:taskId/stop' , method='POST')
def task_stop(envId,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envId).get_node(int(nodeId)).stop_task(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task stop: error: %s",envId,int(nodeId), str(inst))
    
#############################################
    
class tutu():
    def __init__(self):
        route(callback=self.say, path="/environments",method=["GET","POST","PUT","DELETE"])
        #r = route("/environments")
        #r2 = r(self.say)
    def say(self):
        try:
            #return "gnee"
            
            print("lkj")
            r= Response()
            r.body="gnee"
            print("mlk")
            print(r)
            response.status=501
            return str(r)
        except exception as  inst:
            print("mlk")
            print(inst)   
    
    def run(self):
        debug(True)
        run(port="8000")


def start_webServer():
    bottle.debug(True)
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(('google.com', 0))
    #hostIp=s.getsockname()[0]
    hostIp='127.0.0.1'
    #tutu().run()
    run(app=server,server=server.chosenServer, host=hostIp, port=server.chosenPort)
