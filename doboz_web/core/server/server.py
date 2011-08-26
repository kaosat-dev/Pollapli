import logging, sys,os,shutil,uuid,tempfile
from twisted.python import log
from twisted.web.static import File
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.resource import NoResource
from twisted.internet import reactor
from twisted.enterprise import adbapi
from twisted.plugin import pluginPackagePaths
from twisted.internet import reactor, defer


from doboz_web.core.components.environments.environment import EnvironmentManager,Environment
from doboz_web.core.server.rest.handlers.environment_handlers import EnvironmentsHandler
from doboz_web.core.server.rest.handlers.driver_handlers import DriverTypesHandler
from doboz_web.core.server.rest.handlers.config_handlers import ConfigHandler
from doboz_web.core.server.rest.exception_converter import ExceptionConverter
from doboz_web.exceptions import *
from doboz_web.core.file_manager import FileManager
from doboz_web.core.components.updates.update_manager import UpdateManager
from doboz_web.core.components.drivers.driver import DriverManager
from doboz_web.core.signal_system import SignalHander
from doboz_web.core.tools import checksum_tools
from doboz_web.core.server.rest.data_formater   import JsonFormater
from doboz_web.core.components.autocompile.compile_upload import  SconsProcessProtocol
#from doboz_web.dependencies.usb import core  
#from doboz_web.dependencies import usb
#from doboz_web.dependencies.wmi import wmi

from twisted.application.service import Application
from twisted.python import log
class MainServer():
    def __init__(self,port,rootPath,filePath,dataPath):
        #app = Application("PollapliServer")

        self.port=port
        self.rootPath=rootPath
        self.filePath=filePath
        self.dataPath=dataPath
        self.logPath=dataPath
        self.updatesPath=os.path.join(dataPath,"updates")
        self.addOnsPath=os.path.join(self.rootPath,"addons")
        self.environmentsPath=os.path.join(self.dataPath,"environments")
        self.depenciesPath=os.path.join(self.rootPath,"dependencies")
        if not os.path.exists(self.rootPath):
            os.makedirs(self.rootPath)
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)
        if not os.path.exists(self.updatesPath):
            os.makedirs(self.updatesPath)
        if not os.path.exists(self.addOnsPath):
            os.makedirs(self.addOnsPath)
        if not os.path.exists(self.environmentsPath):
            os.makedirs(self.environmentsPath)

        
        """""""""""""""""""""""""""""""""""""""""
        Initialize various subsystems /set correct paths
        """
        UpdateManager.addOnPath=self.addOnsPath
        UpdateManager.updatesPath=self.updatesPath
        EnvironmentManager.envPath=self.environmentsPath
        FileManager.rootDir=self.dataPath        
        FileManager.corePath=os.path.join(self.rootPath,"core")
        self.environmentManager=EnvironmentManager(self.dataPath)
        
        """"""""""""""""""""""""""""""""""""""
        exceptionConverter=ExceptionConverter()
        exceptionConverter.add_exception(ParameterParseException,400 ,1,"Params parse error")
        exceptionConverter.add_exception(UnhandledContentTypeException,415 ,2,"Bad content type")
        exceptionConverter.add_exception(EnvironmentAlreadyExists,409 ,3,"Environment already exists")
        exceptionConverter.add_exception(EnvironmentNotFound,404 ,4,"Environment not found")
        exceptionConverter.add_exception(UnknownNodeType,500 ,5,"Unknown node type")
        exceptionConverter.add_exception(NodeNotFound,404 ,6,"Node not found")
        exceptionConverter.add_exception(NoDriverSet,404,7,"Node has no connector")
        exceptionConverter.add_exception(UnknownDriver,500,8,"Unknown connector driver type")
        exceptionConverter.add_exception(DeviceHandshakeMismatch,500,9,"Device handshake failed to match the one defined by the driver")
        exceptionConverter.add_exception(InvalidFile,500,10,"Invalid File")
        exceptionConverter.add_exception(DeviceNotConnected,500,11,"Attempting to communicate with not connected device")
        
        self.signalChannel="main_signal_listener"
        self.signalHandler=SignalHander(self.signalChannel)
        self.signalHandler.add_handler(channel="driver_manager")   
        self.signalHandler.add_handler(channel="update_manager")
        self.signalHandler.add_handler(channel="environment_manager")
        self.signalHandler.add_handler(channel="node_manager")
        
        self.setup()

        
       # reactor.callLater(2,self.compiler_test)
       # reactor.callLater(2,self.compiler_test2)
        #reactor.callLater(5,self.uploader_test)
        
        #self.formatter_tests()
        #self.usbTest2()
        #reactor.callLater(1,self.gstInspectTest)
        
    def gstInspectTest(self):
        path="C:\\Program Files\\OSSBuild\\GStreamer\\v0.10.6\\bin\gst-inspect.exe"
        scp = SconsProcessProtocol("truc")
        scp.deferred = defer.Deferred()
        cmd = [path]     
       
        p = reactor.spawnProcess(scp, cmd[0], cmd,env=os.environ )
        #p = reactor.spawnProcess(processProtocol=scp, executable=cmd[0],args=cmd,env=os.environ )
        return scp.deferred
    def usbTest_pyusb(self):
        #import pysusb.usb.core
        dev = usb.core.find(find_all=True)
        print("dev ",dev)
    def usbTest(self):
        
        #print("core inst",core.__name__)
        devices= usb.core.find(find_all=True)
        print("total devices",devices)
        try:
            for device in devices:
                print("====DEVICE====")
                _name = usb.util.get_string(device,256,device.iProduct)  #This is where I'm having trouble
                print ("device name=",_name)
                #print ("Device:", device.filename)
                print("descriptor type",device.bDescriptorType)
                print("highest usb type",device.bcdUSB)
                print("class",device.bDeviceClass)
                print("subClass",device.bDeviceSubClass)
                print("vendor id",device.idVendor)
                print("device id",device.idProduct)
                print("bDeviceProtocol",device.bDeviceProtocol)
                print("bcdDevice",device.bcdDevice)
                print("iSerialNumber",device.iSerialNumber)
                print("serialNumber",usb.util.get_string(device,256,device.iSerialNumber))
                print("iManufacturer",device.iManufacturer)
                print("manufacturer",usb.util.get_string(device,256,device.iManufacturer))
                print("iProduct",device.iProduct)
                print("product",usb.util.get_string(device,256,device.iProduct))
                print("configs",device.bNumConfigurations)
                print("   **getting data**")
                
                print("test",usb.util.get_string(device,256,3))
                
                #device.set_configuration(0)
                activeConf=device.get_active_configuration()
                print("active conf", activeConf)
                print("bconfValue", activeConf.bConfigurationValue)
                print("bNumInterfaces", activeConf.bNumInterfaces)
                for interf in activeConf:
                    print("bInterfaceNumber", interf.bInterfaceNumber)
                    print("interfaceInterf", interf.iInterface)
                    print("interfaceBaseClass", interf.bInterfaceClass)
                    print("interfaceSubClass", interf.bInterfaceSubClass)

        except Exception as inst:
            print("error",inst)
                
#        busses = usb.busses()
#        print("busses",busses)
#        for bus in busses:
#            devices = bus.devices
#            for dev in devices:
#                print "Device:", dev.filename
#                _name = usb.util.get_string(device,256,0)  #This is where I'm having trouble
#                print ("device name=",_name)
#                print "  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor)
#                print "  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct)
        reactor.stop()
    def usbTest2(self):
       # import wmi

        c = wmi.WMI()
        
        drivers=c.Win32_PnPSignedDriver()
        for driver in drivers:
            print(driver)
        print("devices")
        devices= c.Win32_USBControllerDevice()
        for dev in devices:
            #print(dev)
            devId=dev.Dependent.DeviceID
            for device in c.Win32_PnPEntity(DeviceID=devId):
                #print(device)
                print(device.DeviceID)
                #print (device.ClassGuid,device.Name,device.DeviceID)
#        dep=devices[0].Dependent 
#        print("Did",dep)
        
#        for device in c.Win32_PnPEntity(DeviceID=dep.DeviceID):
#            print (device)
    def spawn_test(self):
        trucpath=os.path.join("d:\\Progra","arduino-0018","arduino.exe")
        trucpath=os.path.join("d:\\","data","projects","Doboz","doboz_web","dependencies","scons","scons.py")

        """
        env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join(sys.path)
                reactor.callLater(0,reactor.spawnProcess, env=env, *self.spawn)
                """
        print('PYTHONPATH',os.environ['PYTHONPATH'])

        scp = SconsProcessProtocol("truc")
        scp.deferred = defer.Deferred()
        print("os environ",os.environ)
        print("sys exect",sys.executable)
        cmd = ["C:\Progra\Python26\python.exe",trucpath]   
        cmd=[sys.executable,trucpath]  
       
        p = reactor.spawnProcess(scp, cmd[0], cmd,env=os.environ )
        #p = reactor.spawnProcess(processProtocol=scp, executable=cmd[0],args=cmd,env=os.environ )
        return scp.deferred
    
    
    def compiler_test3(self):
        testTarget=os.path.join(self.rootPath,"arduinoexample")
        sconsPath=os.path.join(self.depenciesPath,"scons","scons.py")
        shutil.copy2(os.path.join(self.rootPath,"core","components","autocompile","SConstruct"),os.path.join(testTarget,"SConstruct"))
        if os.path.exists(sconsPath):
            print("scons found")
            print("sconsPath",sconsPath)
            scp = SconsProcessProtocol("arduino")
            scp.deferred = defer.Deferred()
            """on linux """
            #cmd = [sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i"]
            """on win32"""
            cmd =[sys.executable,sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i"]
            p = reactor.spawnProcess(scp, cmd[0], cmd,env=os.environ )
            return scp.deferred
        else:
            print("scons not found")
    
    
    def compiler_test(self):
        """todo: add temp file deletion"""
        testTarget=os.path.join(self.addOnsPath,"ArduinoExampleAddOn","arduinoExample" ,"firmware","arduinoexample")
        print(testTarget)
        #print("tutu","\\\?\\")
        ##apparently, max path limitation could get avoided with : "\\\?\\" prefix, causes the build
        ##to fail though
        
        envCopy=os.environ.copy()
        
        sconsPath=os.path.join(self.depenciesPath,"scons","scons.py")
        
        
        def create_dir_struture(source,inTemp=False):
            if inTemp:
                import distutils.dir_util
                targetBuildDir=tempfile.mkdtemp()
                distutils.dir_util.copy_tree(testTarget, targetBuildDir)
            else:
                buildsDir=os.path.join(self.rootPath,"builds")
                if not os.path.exists(buildsDir):
                    os.makedirs(buildsDir)
        
                targetBuildName=str(uuid.uuid4())
                targetBuildDir=os.path.join(buildsDir,targetBuildName)
                shutil.copytree(testTarget, targetBuildDir)
            """rename the pde file"""
            tmp = os.path.basename(testTarget)
            tmpDst=os.path.basename(targetBuildDir)
            shutil.move( os.path.join(targetBuildDir,tmp+".pde"),os.path.join(targetBuildDir,tmpDst+".pde"))
            """copy scons file to folder"""
            shutil.copy2(os.path.join(self.rootPath,"core","components","autocompile","SConstruct"),targetBuildDir)
            return targetBuildDir
        
        testTarget=create_dir_struture(testTarget)
        
        
        if os.path.exists(sconsPath):
            print("scons found")
            print("sconsPath",sconsPath)
            scp = SconsProcessProtocol("arduino",testTarget)
            scp.deferred = defer.Deferred()
            """on linux """
            #cmd = [sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i"]
            """on win32"""
            cmd =[sys.executable,sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i","--diskcheck=none","--cache-disable","--config=force"]
            p = reactor.spawnProcess(scp, cmd[0], cmd,env=envCopy )
            return scp.deferred
        else:
            print("scons not found")
    
    def compiler_test2(self):
        testTarget=os.path.join(self.addOnsPath,"Hydroduino_0_0_1_py2_6","hydroduino" ,"firmware","hydroduino")
        
        sconsPath=os.path.join(self.depenciesPath,"scons.py")  
        scp = SconsProcessProtocol("hydroduino")
        scp.deferred = defer.Deferred()
        cmd = [sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i"]
        p = reactor.spawnProcess(scp, cmd[0], cmd,env=os.environ,usePTY=True )
        return scp.deferred
        
    def uploader_test(self):
        testTarget=os.path.join(self.addOnsPath,"ArduinoExampleAddOn_0_0_1_py2_6","arduinoExample" ,"firmware","arduinoexample")
        
        sconsPath="/home/ckaos/data/Progra/Scons/scons.py"  
        scp = SconsProcessProtocol()
        scp.deferred = defer.Deferred()
        cmd = [sconsPath,"-Y"+testTarget,"TARGETPATH="+testTarget,"-i", "upload"]
        p = reactor.spawnProcess(scp, cmd[0], cmd,env=os.environ,usePTY=True )
        return scp.deferred
        
#        compiler=compiler_uploader(arduinoPath="/home/ckaos/utilz/Progra/arduino-0022/",targetDir=testTarget)
#        compiler.check_boardName()
#        compiler.do_stuff()
#        compiler.check_source_main()
#        compiler.set_flags()
#        compiler._createBuilders()
#        compiler.addArduinoCore()
#        compiler.addArduinoLibs()
#        compiler.do_convert()
#        
#        compiler.build()
        #compiler.tearDown()
        
        #subprocess.call("myProg -arg1 -arg2")
    
    @defer.inlineCallbacks
    def do_stuff(self):
        #filePath="D:\\data\\projects\\Doboz\\add_ons_egg_tests\\virtualDevice\\dist\\VirtualDeviceAddOn-0.0.1-py2.6.egg"
        rootAddonsPath="D:\\data\\projects\\Doboz\\add_ons_egg_tests\\"
        filePath=os.path.join(rootAddonsPath,"virtualDevice\\dist\\VirtualDeviceAddOn-0.0.1-py2.6.egg")
        filePath=os.path.join(rootAddonsPath,"arduinoExample\\dist\\ArduinoExampleAddOn-0.0.1-py2.6.egg")
        #filePath=os.path.join(rootAddonsPath,"reprap\\dist\\ReprapAddOn-0.0.1-py2.6.egg")
        
        hash=yield checksum_tools.generate_hash(filePath)
        print ("md5 hash",hash)
        hashCompare=yield checksum_tools.compare_hash("80e157c0f10baef206ee2de03fae7449",filePath)
        print("md5 compare", hashCompare)
    
    def formatter_tests(self):
        formater=JsonFormater(resource="Tutu",rootUri="http://localhost",ignoredAttrs=["blah","blob"],addedAttrs={"gateaux":75},list=False)
        class subThing(object):
           EXPOSE=["strengh","width","height"]
           def __init__(self,strengh="Max",width=10,height=7):
               self.strengh=strengh
               self.width=width
               self.height=height
        class Thing(object):
            #EXPOSE=["subThings"]
            def __init__(self):
                self.subThings=[]
                self.subThings.append(subThing("truc")) 
                self.subThings.append(subThing("muche")) 
        class OtherThing(object): 
            EXPOSE=["var","subThing1","subThing2"]
            def __init__(self,var="somevalue"):
                self.var=var    
                self.subThing1=subThing()
                self.subThing2=subThing("min")
                
        class Tutu(object):
           id=0
           EXPOSE=["id","thing.subThings"]
           def __init__(self,blob="blob",blib=42,blah="nii"):
               self.blob=blob
               self.blib=blib
               self.blah=blah
               self.id=Tutu.id
               self.name="truc"
               self.thing=Thing()
               Tutu.id+=1
               
        class ThingWithId(object):
            id=0
            EXPOSE=["id","thingy"]
            def __init__(self,thingy="thing"):
                self.id=ThingWithId.id
                ThingWithId.id+=1
                self.thingy=thingy
        print("single item: ",formater.format(OtherThing(),"Otherthing","http://localhost/otherthing"))
        print("single item: ",formater.format(Tutu(),"tutu","http://localhost/tutu"))
        print("multiple items: ",formater.format([subThing("min",0.5,3),subThing()],"kpouer","http://localhost/kpouer"))
        print("multiple items: ",formater.format([ThingWithId(),ThingWithId()],"wobbly","http://localhost/wobbly"))
       
    
    def callbackTests(self):
        d=defer.Deferred() 
        def funct1(result):
            print("in funct1")  
        def funct2(result):
            print("in funct2")
        def funct3(result):
            print("in funct3")  
        d.addCallback(funct1)
        d.addCallback(funct2)
        d.addCallback(funct3)
        d.callback(None)
    
    @defer.inlineCallbacks
    def setup(self):
        """configure all systems """
        from twisted.enterprise import adbapi
        from twistar.registry import Registry
        envPath=os.path.join(EnvironmentManager.envPath,"home")
        dbPath=os.path.join(envPath,"home")+".db"
        Registry.DBPOOL = adbapi.ConnectionPool("sqlite3",database=dbPath,check_same_thread=False)
        """this is a required but very cheap hack: since twistard does not support multiple databases,
        we do not have a "master" database, which causes problems because of the dependencies, and initialization
        order of different elements, so for now, the "home" database is enforced"""
        
        yield UpdateManager.setup()
        yield DriverManager.setup()
        yield EnvironmentManager.setup()
        
        defer.returnValue(None)
        
    def start(self):
        observer = log.PythonLoggingObserver("pollapli.core")
        observer.start()
       # log.startLogging(sys.stdout)
       # logfile=os.path.join(self.logPath,"pollapli.log")
       # log.startLogging(open(logfile, 'w'),setStdout=False)
        
        root = File(self.filePath)
        restRoot=Resource()
        root.putChild("rest",restRoot)
        try:
            restRoot.putChild("config", ConfigHandler("/rest/config"))
            restRoot.putChild("drivertypes", DriverTypesHandler("/rest/drivertypes")) 
            restRoot.putChild("environments", EnvironmentsHandler("/rest/environments",self.environmentManager))

        except Exception as inst:
            log.msg("Error in base rest resources creation",str(inst), system="server", logLevel=logging.CRITICAL)
        
        
        factory = Site(root)
        #self.port=9071#TEMP HACK!!
        reactor.listenTCP(self.port, factory)
        log.msg("Server started!", system="server", logLevel=logging.CRITICAL)
        reactor.run()
         #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
         #s.connect(('google.com', 0))
         #hostIp=s.getsockname()[0]
    