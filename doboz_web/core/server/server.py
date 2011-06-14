import logging
import os
import sys
import time
import datetime
import socket
import json

from bottle import Bottle, route, run, send_file, redirect, abort, request, response 
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

"""Convert any dict keys to str, because of a bug in pre 2.6.5 python"""
def stringify_data(obj):
        if type(obj) in (int, float, str, bool):
                return obj
        elif type(obj) == unicode:
                return obj#return str(obj)
        elif type(obj) == dict:
                modobj={}
                for i,v in obj.iteritems():
                        modobj[str(i)]=stringify_data(v)
                obj=modobj
                       # obj[i] = filter_data(v)
        else:
                print "invalid object in data, converting to string"
                obj = str(obj) 
        return obj    

def fetch_jsonData():
    """ In python pre 2.6.5, bug in unicode dict keys"""
    data=request.body.readline()
    params=json.loads(data,encoding='utf8')
    params=stringify_data(params)
    return params 

def format_jsonResponse():
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    
data_fetchers={}
data_fetchers["application/json"]=fetch_jsonData


    
def request_handler(xmlHandler=None,jsonHandler=None,errorMessage="",contentTypeErrorMessage=""):
    """only handles json for now"""
    handlers={}
    handlers["application/json"]=jsonHandler
    handlers["application/xml"]=xmlHandler
    
    content_type=request.headers.get("Content-Type")
    print(content_type)
    if not handlers[content_type]: 
        abort(501,contentTypeErrorMessage)
    else:
        try: 
            handlers[content_type](**data_fetchers[content_type]())
        except Exception as inst:
            server.logger.critical("error %s",str(inst))
            abort(500,errorMessage)    

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
    
            

@server.route('/environments' , method='GET')
@server.route('/environments' , method='POST')
@server.route('/environments' , method='PUT')
@server.route('/environments' , method='DELETE')
@server.route('/environments/' , method='GET')
@server.route('/environments/' , method='POST')
@server.route('/environments/' , method='PUT')
@server.route('/environments/' , method='DELETE')
def handle_envs():
    envsHandler=EnvsRestHandler(server.environmentManager)
    return envsHandler._handle(request)


@server.route('/environments/:envName' , method='GET')
@server.route('/environments/:envName' , method='POST')
@server.route('/environments/:envName' , method='PUT')
@server.route('/environments/:envName' , method='DELETE')
@server.route('/environments/:envName/' , method='GET')
@server.route('/environments/:envName/' , method='POST')
@server.route('/environments/:envName/' , method='PUT')
@server.route('/environments/:envName/' , method='DELETE')
def handle_env(envName):
    envHandler=EnvRestHandler(server.environmentManager,envName)
    return envHandler._handle(request)


@server.route('/environments/:envName/nodes' , method='GET')
@server.route('/environments/:envName/nodes' , method='POST')
@server.route('/environments/:envName/nodes' , method='PUT')
@server.route('/environments/:envName/nodes' , method='DELETE')
@server.route('/environments/:envName/nodes/' , method='GET')
@server.route('/environments/:envName/nodes/' , method='POST')
@server.route('/environments/:envName/nodes/' , method='PUT')
@server.route('/environments/:envName/nodes/' , method='DELETE')
def handle_nodes(envName):
    nodesHandler=NodesRestHandler(server.environmentManager,envName)
    return nodesHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/' , method='DELETE')
def handle_node(envName,nodeId):
    nodeHandler=NodeRestHandler(server.environmentManager,envName,int(nodeId))
    return nodeHandler._handle(request)


@server.route('/environments/:envName/nodes/:nodeId/connector' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='DELETE')
def handle_connector(envName,nodeId):
    connectorHandler=ConnectorRestHandler(server.environmentManager,envName,int(nodeId))
    return connectorHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId/connector/status' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/connector/status' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/connector/status' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/connector/status' , method='DELETE')
def handle_connector_status(envName,nodeId):
    connectorStatusHandler=ConnectorStatusRestHandler(server.environmentManager,envName,int(nodeId))
    return connectorStatusHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/tasks/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/' , method='DELETE')
def handle_tasks(envName,nodeId):
    tasksHandler=TasksRestHandler(server.environmentManager,envName,int(nodeId))
    return tasksHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/' , method='DELETE')
def handle_task(envName,nodeId,taskId):
    taskHandler=TaskRestHandler(server.environmentManager,envName,int(nodeId),int(taksId))
    return taskHandler._handle(request)


@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/status/' , method='DELETE')
def handle_task_status(envName,nodeId,taskId):
    pass
    #taskHandler=TaskRestHandler(server.environmentManager,envName,int(nodeId),int(taksId))
    #return taskHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/condtions/' , method='DELETE')
def handle_task_conditions(envName,nodeId,taskId):
    pass#taskHandler=TaskRestHandler(server.environmentManager,envName,int(nodeId),int(taksId))
    #return taskHandler._handle(request)

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='DELETE')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions/' , method='GET')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions/' , method='POST')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions/' , method='PUT')
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions/' , method='DELETE')
def handle_task_actions(envName,nodeId,taskId):
    pass#taskHandler=TaskRestHandler(server.environmentManager,envName,int(nodeId),int(taksId))
    #return taskHandler._handle(request)
#############################################
  
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/conditions' , method='GET')
def task_conditions_get(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).get_conditions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envName,int(nodeId), str(inst))       
 
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/conditions' , method='POST')
def task_conditions_post(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).add_condition(**params)
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envName,int(nodeId), str(inst))       

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/conditions' , method='DELETE')
def task_conditions_delete(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).clear_conditions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task conditions get: error: %s",envName,int(nodeId), str(inst))       


        
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='GET')
def task_actions_get(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).get_actions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envName,int(nodeId), str(inst))       
 
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='POST')
def task_actions_post(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).add_action(**params)
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envName,int(nodeId), str(inst))       

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/actions' , method='DELETE')
def task_actions_delete(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).clear_actions(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task actions get: error: %s",envName,int(nodeId), str(inst))       
    
        
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/start' , method='POST')
def task_start(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).start_task(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task start: error: %s",envName,int(nodeId), str(inst))
    
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId/stop' , method='POST')
def task_stop(envName,nodeId,taskId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).stop_task(int(taskId))
    except Exception as inst:
        server.logger.critical("in env %s node id %d task stop: error: %s",envName,int(nodeId), str(inst))
    
#############################################
    



def start_webServer():
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(('google.com', 0))
    #hostIp=s.getsockname()[0]
    hostIp='127.0.0.1'
    
    run(app=server,server=server.chosenServer, host=hostIp, port=server.chosenPort)
