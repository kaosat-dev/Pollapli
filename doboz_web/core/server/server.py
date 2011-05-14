import logging
import os
import sys
import time
import datetime
import socket

from bottle import Bottle, route, run, send_file, redirect, abort, request, response 
import bottle
from doboz_web.core.components.automation.print_task import PrintTask
from doboz_web.core.components.automation.scan_task import ScanTask
from doboz_web.core.components.automation.transition_task import TransitionTask
from doboz_web.core.components.automation.timer_task import TimerTask

server = Bottle()
server.rootPath=os.path.join(os.path.abspath("."),"core","server")
server.logger=logging.getLogger("dobozweb.core.WebServer")

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
    
    

@server.route('/environments' , method='GET')
def environments_get():
    print("getting env list")
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    response=callback+"("+str(server.environmentManager.get_environments())+")"
    return response
    
@server.route('/environments' , method='POST')
def environments_post():
    print("posting to env list")
@server.route('/environments' , method='PUT')
def environments_put():
    try:
        server.environmentManager.add_environment(**request.params)
    except Exception as inst:
        server.logger.critical("error %s",str(inst))
  
@server.route('/environments' , method='DELETE')
def environments_delete():
    try:
        server.environmentManager.remove_environment(**request.params)
    except Exception as inst:
        server.logger.critical("environment deletion error %s",str(inst))

@server.route('/environments/:envName' , method='GET')
def environment_get(envName):
    try:
        server.environmentManager.get_environementInfo(envName)
    except Exception as inst:
        server.logger.critical("environment %s get error %s",envName, str(inst))
    
@server.route('/environments/:envName' , method='POST')
def environment_post(command):
    pass
@server.route('/environments/:envName' , method='PUT')
def environment_put(envName):
    print("putting info for "+ envName)
@server.route('/environments/:envName' , method='DELETE')
def environment_delete(envName):
    print("deleting "+ envName)

#############################################

@server.route('/environments/:envName/nodes' , method='GET')
def nodes_get(envName):
    callback=request.GET.get('callback', '').strip()
    response=callback+"()"
    try:
        data=server.environmentManager.get_environment(envName).get_nodes()
        response=callback+"("+str(data)+")"
    except Exception as inst:
        server.logger.critical("in env %s  node get error: %s",envName, str(inst))
    return response
@server.route('/environments/:envName/nodes' , method='POST')
def nodes_post(envName):
    try:
        server.environmentManager.get_environment(envName).add_node(**request.params)
    except Exception as inst:
        server.logger.critical("in env %s  node post error: %s",envName, str(inst))
    
@server.route('/environments/:envName/nodes' , method='PUT')
def nodes_put(envName):
    pass
    
@server.route('/environments/:envName/nodes' , method='DELETE')
def nodes_delete(envName):
    try:
        server.environmentManager.get_environment(envName).clear_nodes()
    except Exception as inst:
        server.logger.critical("in env %s  node delete error: %s",envName, str(inst))
    

@server.route('/environments/:envName/nodes/:nodeId' , method='GET')
def node_get(envName,nodeId):
    try:
        server.environmentManager.get_environment(envName).add_node("pouet","reprap")
    except Exception as inst:
        server.logger.critical("in env %s node get error: %s",envName, str(inst))
    
@server.route('/environments/:envName/nodes/:nodeId' , method='POST')
def node_post(envName,nodeId):
    print("posting info for node"+ nodeId+" in env"+envName)
@server.route('/environments/:envName/nodes/:nodeId' , method='PUT')
def node_put(envName,nodeId):
    print("putting info for node"+ nodeId+" in env"+envName)
@server.route('/environments/:envName/nodes/:nodeId' , method='DELETE')
def node_delete(envName,nodeId):
    try:
        server.environmentManager.get_environment(envName).delete_node(int(nodeId))
    except Exception as inst:
        server.logger.critical("in env %s  node %d connector delete error: %s",envName,nodeId, str(inst))
    
#############################################
@server.route('/environments/:envName/nodes/:nodeId/connect' , method='PUT')
def node_connect_put(envName,nodeId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).connect()
    except Exception as inst:
        server.logger.critical("in env %s node connect error: %s",envName, str(inst))
@server.route('/environments/:envName/nodes/:nodeId/disconnect' , method='PUT')
def node_disconnect_put(envName,nodeId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).disconnect()
    except Exception as inst:
        server.logger.critical("in env %s node connect error: %s",envName, str(inst))

#############################################

@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='GET')
def tasks_get(envName,nodeId):
    print("getting info for tasks in node "+ nodeId+" in env "+envName)
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='POST')
def tasks_post(envName,nodeId):
    try:
        server.environmentManager.get_environment(envName).get_node(int(nodeId)).add_task(**request.params)
    except Exception as inst:
        server.logger.critical("in env %s node id %d task post error: %s",envName,int(nodeId), str(inst))
        
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='PUT')
def tasks_put(envName,nodeId):
    print("putting into tasks in node "+ nodeId+" in env "+envName)
@server.route('/environments/:envName/nodes/:nodeId/tasks' , method='DELETE')
def tasks_delete(envName,nodeId):
    print("deleting tasks in node "+ nodeId+" in env "+envName)

@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='GET')
def task_get(envName,nodeId,taskId):
    print("getting info for task "+ taskId+ " in node "+ nodeId+" in env "+envName)
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='POST')
def task_post(envName,nodeId,taskId):
    print("post info for task"+ taskId+ "in node"+ nodeId+" in env "+envName)
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='PUT')
def task_put(envName,nodeId,taskId):
    print("puting info for task"+ taskId+ "in node"+ nodeId+" in env "+envName)
@server.route('/environments/:envName/nodes/:nodeId/tasks/:taskId' , method='DELETE')
def task_delete(envName,nodeId,taskId):
    print("deleting info for task"+ taskId+ "in node"+ nodeId+" in env "+envName)

#############################################
"""Node Connector handling """
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='GET')
def connector_get(envName,nodeId):
    print("getting info for connector of node "+ nodeId+" in env "+envName)
    
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='PUT')
def connector_put(envName,nodeId):
    nodeId=int(nodeId)
    request.params['nodeId']=nodeId
    try:
        server.environmentManager.get_environment(envName).set_connector(**request.params)
    except Exception as inst:
        server.logger.critical("in env %s  node %d connector put error: %s",envName,nodeId, str(inst))
    
@server.route('/environments/:envName/nodes/:nodeId/connector' , method='DELETE')
def connector_delete(envName,nodeId):
    nodeId=int(nodeId)
    try:
        pass#server.environmentManager.get_environment(envName).delete_node(nodeId)
    except Exception as inst:
        server.logger.critical("in env %s  node %d connector delete error: %s",envName,nodeId, str(inst))
    
#############################################
#############################################
"""Node connector DRIVER handling """
@server.route('/environments/:envName/nodes/:nodeId/connector/driver' , method='GET')
def driver_get(envName,nodeId):
    print("getting info for driver of node "+ nodeId+" in env "+envName)
    
@server.route('/environments/:envName/nodes/:nodeId/connector/driver' , method='PUT')
def driver_put(envName,nodeId):
    print("puting info for driver of node"+ nodeId+" in env "+envName)
    nodeId=int(nodeId)
    request.params['nodeId']=nodeId
    try:
        server.environmentManager.get_environment(envName).set_driver(**request.params)
    except Exception as inst:
        server.logger.critical("in env %s  node %d driver put error: %s",envName,nodeId, str(inst))
    
@server.route('/environments/:envName/nodes/:nodeId/connector/driver' , method='DELETE')
def driver_delete(envName,nodeId):
    print("deleting info for connector of node"+ nodeId+" in env "+envName)
#############################################




def start_webServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    hostIp=s.getsockname()[0]

    run(app=server,server=server.chosenServer, host=hostIp, port=server.chosenPort)
