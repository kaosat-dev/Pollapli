#!python
"""
.. py:module:: run
   :platform: Unix, Windows, Mac
   :synopsis: Main entry point to doboz-web.
"""
from __future__ import absolute_import
import sys
import ConfigParser
import logging
import os
import socket
#from doboz_web import plugins
from twisted.python.runtime import platform

def configure_all():
    """
    Setup all pre required elements for reprap , webcam handling and webserver 
    """ 
    
    
    logger = logging.getLogger("pollapli.core")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    """"""""""""""""""""""""""""""""""""
    
    Config = ConfigParser.ConfigParser()
    rpath= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    rootPath = os.path.join(rpath,"doboz_web")
    Config.read(os.path.join(rootPath, "config.cfg"))
    
    
    """"""""""""""""""""""""""""""""""""
    """Environment manager elements"""
    envPath=os.path.join(rootPath,"data","environments")
    if not os.path.exists(envPath):
        os.makedirs(envPath)
    
    sys.path.insert(0, os.path.join(rootPath, "addons"))
    sys.path.insert(0, os.path.join(rootPath))
    sys.path.insert(0, os.path.join(rootPath,"dependencies"))
    #sys.path.insert(0, os.path.join(rootPath,"dependencies","pyusb"))
    
    """"""""""""""""""""""""""""""""""""
    """WebCam config elements"""
    useWebcam = Config.getboolean("WebCam", "use")
    webcamDriver = Config.get("WebCam", "driver")
    #server.webcamsEnabled = useWebcam
#    if useWebcam:
#         from doboz_web.core.components.connectors.webcam.gstreamer_cam import GStreamerCam
#         webcamNode = WebcamNode()
#         webcamNode.filePath = os.path.join(rootPath, "core", "print_server", "files", "static", "img", "test")
#         webcamConnector = GStreamerCam(driver=webcamDriver)
#         webcamNode.set_connector(webcamConnector)
#         webcamNode.start()
#         """"""
#         testBottle.webcam = webcamNode

    """"""""""""""""""""""""""""""""""""
    """Web Server config elements"""
   
    servertype = Config.get("WebServer", "server")
    port = Config.getint("WebServer", "port")
  
    
    #server.chosenServer = servertype
    #server.chosenPort = port
    dataPath=os.path.join(rootPath,"data")
    filePath=os.path.join(rootPath,"core","server","static")
#    server.printFilesPath=os.path.join(server.rootPath,"files","machine","printFiles")
#    server.scanFilesPath=os.path.join(server.rootPath,"files","machine","scanFiles")
#    if not os.path.exists(server.printFilesPath):
#        os.makedirs(server.printFilesPath)
#    if not os.path.exists(server.scanFilesPath):
#        os.makedirs(server.scanFilesPath)
        
    
    """"""""""""""""""""""""""""""""""""
    """Twisted server setup"""
    
    if platform.isWindows():
        from twisted.internet import win32eventreactor
        reactor=win32eventreactor        
    else:
        from twisted.internet import selectreactor
        reactor=selectreactor
    reactor.install()
        
    
    from doboz_web.core.server.server import MainServer
    server=MainServer(port,rootPath,filePath,dataPath)
    
    """
    starts all server components
    """
    server.start()
    #start_webServer()
    
    
if __name__ == "__main__":
    configure_all()
 



