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


from doboz_web.core.components.connectors.hardware.serial.serial_plus import SerialPlus
from doboz_web.core.components.drivers.reprap.Teacup.teacup_driver import TeacupDriver
from doboz_web.core.components.drivers.reprap.FiveD.fived_driver import FiveDDriver
from doboz_web.core.components.environments.environment_manager import EnvironmentManager
from doboz_web.core.components.nodes.hardware.reprap.reprap_node import ReprapNode
from doboz_web.core.components.nodes.hardware.webcam.webcam_node import WebcamNode
from doboz_web.core.server.server import *
   


def configure_all():
    """
    Setup all pre required elements for reprap , webcam handling and webserver 
    """ 
    
    logger = logging.getLogger("dobozweb.core")
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    """"""""""""""""""""""""""""""""""""
    
    Config = ConfigParser.ConfigParser()
    rpath= os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    rootPath = os.path.join(rpath,"doboz_web")
    Config.read(os.path.join(rootPath, "config.cfg"))
    
    """"""""""""""""""""""""""""""""""""
    """Environment manager elements"""
    envPath=os.path.join(rootPath,"data")
    if not os.path.exists(envPath):
        os.makedirs(envPath)
    environmentManager=EnvironmentManager(envPath)
    
    """"""""""""""""""""""""""""""""""""
    """Reprap config elements"""
    #reprapNode = ReprapNode()
   
    reprapDriver=  Config.get("Reprap", "driver")
    speed=  Config.getint("Reprap", "speed")
    seperator=Config.get("Reprap", "seperator")
    bufferSize=Config.getint("Reprap", "bufferSize")
    
    
    """"""""""""""""""""""""""""""""""""
    """WebCam config elements"""
    useWebcam = Config.getboolean("WebCam", "use")
    webcamDriver = Config.get("WebCam", "driver")
    server.webcamsEnabled = useWebcam
    if useWebcam:
         from doboz_web.core.components.connectors.webcam.gstreamer_cam import GStreamerCam
         webcamNode = WebcamNode()
         webcamNode.filePath = os.path.join(rootPath, "core", "print_server", "files", "static", "img", "test")
         webcamConnector = GStreamerCam(driver=webcamDriver)
         webcamNode.set_connector(webcamConnector)
         webcamNode.start()
         """"""
         testBottle.webcam = webcamNode

    """"""""""""""""""""""""""""""""""""
    """Web Server config elements"""
   
    servertype = Config.get("WebServer", "server")
    port = Config.getint("WebServer", "port")
    server.chosenServer = servertype
    server.chosenPort = port
    server.rootPath=os.path.join(rootPath,"core","server")
    server.printFilesPath=os.path.join(server.rootPath,"files","machine","printFiles")
    server.scanFilesPath=os.path.join(server.rootPath,"files","machine","scanFiles")
    if not os.path.exists(server.printFilesPath):
        os.makedirs(server.printFilesPath)
    if not os.path.exists(server.scanFilesPath):
        os.makedirs(server.scanFilesPath)
        
    server.environmentManager=environmentManager

    """
    starts all server components
    """
    start_webServer()

    
if __name__ == "__main__":
    configure_all()
 



