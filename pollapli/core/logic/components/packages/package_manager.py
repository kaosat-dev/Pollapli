"""
.. py:module:: addon_manager
   :synopsis: manager of addons : add ons are packages of plugins + extras, 
   and this manager handles the references to all of them
"""
import logging
import uuid
import pkgutil
import zipfile
import os
import sys
import json
import shutil
import time
import filecmp
from distutils import file_util
from distutils import dir_util
from zipfile import ZipFile
from twisted.internet import reactor, defer, task
from twisted.python import log, failure
from twisted.plugin import getPlugins, IPlugin

from pollapli.core.logic.tools.signal_system import SignalDispatcher
from pollapli.exceptions import UnknownPackage, PackageNotFound
from pollapli.core.logic.components.packages.package import Package
from pollapli.core.logic.tools.downloader import DownloaderWithProgress


class PackageManager(object):
    """
    Class for managing updates/addons: works as a container, a handler
    and a central management point for the list of available and installed addons/updates
    """
    def __init__(self, pathManager=None, packageCheckEnabled=False, packageCheckFrequency = 240):
        self._path_manager = pathManager
        self._signal_channel = "package_manager"
        self._signal_dispatcher = SignalDispatcher(self._signal_channel)
        self.signalChannelPrefix = "package_manager"

        pollapli_package = Package(name="Pollapli", description="core package", version="0.5.0", installed=True)
        pollapli_package.cid = uuid.UUID("23b0d813-a6b2-461a-88ad-a7020ae67742")
        self._installed_packages = {pollapli_package.cid: pollapli_package}
        self._available_packages = {}

        self.package_check_frequency = packageCheckFrequency
        self.package_check_enabled = packageCheckEnabled
        self.package_list_url = "http://kaosat.net/pollapli/pollapli_packages.json"
        self._package_check = task.LoopingCall(self.refresh_packageList)

        self._addon_path = "."
        self.updates_path = "."
        self._max_download_attempts = 5
        self._downloader = DownloaderWithProgress()

    @defer.inlineCallbacks
    def setup(self):
        """initial configuration method :
        * first it checks for locally copied addons and extracts/installs them
        * then tries to fetch the list of available packages from the update
        server
        * if any new (newer version number or never seen before) update is
        available, it adds it to the dictionary
        of available updates, but it does NOT download or install those updates
        """
        if self.package_check_enabled:
            self._package_check.start(interval=self.package_check_frequency, now=False)
        yield self._list_localPackages()
        #        updates = yield self._persistenceLayer.load_updates()
#        for update in updates:
#            self._updates[update.name]=update
        log.msg("Package Manager setup succesfully ", system="Package Manager", logLevel=logging.INFO)

    def tearDown(self):
        pass

    def send_signal(self, signal="", data=None):
        prefix = "%s." % self.signalChannelPrefix
        self._signal_dispatcher.send_message(prefix + signal, self, data)

    def enable_package_checking(self):
        if not self.package_check_enabled:
            self._package_check.start(interval=self.package_check_frequency, now=False)
            self.package_check_enabled = True

    def disable_package_checking(self):
        if self.package_check_enabled:
            self._package_check.stop()
            self.package_check_enabled = False

    """
    ####################################################################################
    The following are the "CRUD" (Create, read, update,delete) methods for the general handling of updates/addons
    """

    def get_package(self, id=None):
        package = self._installed_packages.get(id)
        if package is None:
            raise UnknownPackage()
        return package

    def get_packages(self, filters=None):
        """
        Returns the list of packages, filtered by  the filter param
        the filter is a dictionary of list, with each key beeing an attribute
        to check, and the values in the list , values of that param to check against
        """
        deferred = defer.Deferred()

        def filter_check(package, filters):
            for key in filters.keys():
                if not getattr(package, key) in filters[key]:
                    return False
            return True

        @defer.inlineCallbacks
        def _get_packages(filters, package_list):
            yield self.refresh_packageList()
            if filter:
                defer.returnValue([package for package in package_list if filter_check(package, filters)])
            else:
                defer.returnValue(package_list)

        deferred.addCallback(_get_packages, self._installed_packages.values())
        reactor.callLater(0.5, deferred.callback, filters)
        return deferred

    def delete_package(self, package_id):
        """
        Remove an package : this needs a whole set of checks,
        as it would delete an package completely
        Params:
        id: the id of the package
        """
        deferred = defer.Deferred()

        def remove(package_id, packages):
            package = packages[id]
            if package.type == "package":
                raise Exception("only addons can be removed")
            packages[id].delete()
            del packages[id]
            log.msg("Removed addOn ", package.name, "with id ", package_id, logLevel=logging.CRITICAL)
        deferred.addCallback(remove, self._installed_packages)
        reactor.callLater(0, deferred.callback, id)
        return deferred

    @defer.inlineCallbacks
    def clear_packages(self):
        """
        Removes & deletes ALL the packages that are addons "simple" packages cannot be deleted
        This should be used with care,as well as checks on client side
        """
        for package_id in self._installed_packages.keys():
            yield self.delete_package(package_id=package_id)

    @defer.inlineCallbacks
    def get_plugins(self, interface=None, addOnName=None):
        """
        find a specific plugin in the list of available addOns, by interface and/or addOn
        """
        plugins = []

        @defer.inlineCallbacks
        def scan(path):
            plugins = []
            try:
                addonpackages = pkgutil.walk_packages(path=[path], prefix='')
                for loader, name,isPkg in addonpackages:
                    mod = pkgutil.get_loader(name).load_module(name)
                    try:
                        plugins.extend((yield getPlugins(interface, mod)))
                    except Exception as inst:
                        log.msg("error in fetching plugin: ", str(inst), system="Package Manager", logLevel=logging.CRITICAL)
            except Exception as inst:
                log.msg("error %s in listing packages in path : %s " % (str(inst), path), system="Package Manager", logLevel=logging.CRITICAL)
            defer.returnValue(plugins)

        for addOn in self._installed_packages.itervalues():
            if addOn.type == "addon":
                if addOnName:
                    if addOn.name == addOnName and addOn.enabled:
                        plugins.extend((yield scan(addOn.installPath)))
                else:
                    if  addOn.enabled:
                        plugins.extend((yield scan(addOn.installPath)))
        log.msg("Got plugins: ", str(plugins), system="Package Manager", logLevel=logging.DEBUG)
        defer.returnValue(plugins)

    def enable_addon(self, id=None):
        package = self._installed_packages.get(id)
        if package is None:
            raise UnknownPackage()
        package.enabled = True

    def disable_addon(self, id=None):
        package = self._installed_packages.get(id)
        if package is None:
            raise UnknownPackage() 
        package.enabled = False

    """
    ####################################################################################
    Package download and installation methods
    """

    @defer.inlineCallbacks
    def refresh_packageList(self):
        """Fetches the remote package list, downloads it, and if there were any changes, packages
        the in memory package list accordingly
        """
        log.msg("checking for new packages : time", time.time(), logLevel=logging.CRITICAL)
        packageInfoPath = os.path.join(self._path_manager.tmpPath, "packages.txt") 
        try:
            yield DownloaderWithProgress.download(url=self.package_list_url, destination=packageInfoPath)
            self._parse_packageListFile()
        except Exception as inst:
            log.msg("Failed to download package master list: error:", inst, system="Package Manager", logLevel=logging.CRITICAL)

    @defer.inlineCallbacks
    def setup_package(self,id):
        try:
            yield self._downloadPackage(id)
            yield self.installPackage(id)
        except Exception as inst:
            log.msg("Failed to setup package ", id ,"because of error", inst, system="Package Manager", logLevel=logging.CRITICAL)

    @defer.inlineCallbacks
    def _download_package(self, id):
        """downloads the specified package, if the download was successfull, it checks the package's md5 checksum
        versus the one stored in the package info for integretiy, and if succefull, dispatches a success message
        """
        package = self._available_packages.get(id)
        if package is None:
            raise PackageNotFound()
        try:
            downloadPath = os.path.join(self._path_manager.tmpPath,package.file)  
            yield DownloaderWithProgress.download(url = package.downloadUrl, destination= downloadPath, object=package, refChecksum=package.fileHash)
            package.downloaded = True
            #update.installPath=self._addon_path
            self.send_signal("package_download_succeeded", package)
            log.msg("Successfully downloaded package ",package.name,system="Package Manager",logLevel=logging.DEBUG)
        except Exception as inst:
            self.send_signal("package_download_failed", package)
            log.msg("Failed to download package",package.name," error:",inst,system="Package Manager",logLevel=logging.CRITICAL)

    @defer.inlineCallbacks
    def install_package(self,id):
        """installs the specified package"""
        package = self._available_packages.get(id)
        if package is None:
            raise PackageNotFound()
        if not package.downloaded:
            raise Exception("Cannot install package that was not downloaded first")
        """Steps: 
            extract package in tmp folder
            create list of files it is going to replace
            backup those files to a "rollback" directory
            copy the new files to the correct place
            restart the whole system
            check if all starts well
            if not, delete new files, copy back rollback files, and restart again
            if yes all done
        """
        baseName = os.path.splitext(package.file)[0]
        baseName = baseName.replace('-','_').replace('.','_')
        tmpPath = os.path.join(self._path_manager.tmpPath,baseName)
        sourcePath = os.path.join(self._path_manager.tmpPath,package.file)
        
        if package.type == "addon":
            try:
                destinationPath = os.path.join(self._path_manager._addon_path,baseName)
                
                extractedPackageDir = yield self._extract_package(sourcePath,tmpPath) 
                extractedPackageDir = os.path.join(tmpPath,extractedPackageDir)
                shutil.copytree(extractedPackageDir, destinationPath)
                shutil.rmtree(tmpPath)
                os.remove(sourcePath)
                
                self._installed_packages[package.cid] = package
                package.installPath = os.path.join(self._path_manager._addon_path,os.path.basename(extractedPackageDir))
                package.enabled = True
                self.add_package_toPythonPath(package.installPath)
                self.send_signal("addon_install_succeeded", package)
            except Exception as inst:
                raise Exception("Failed to install addOn: error %s" %(str(inst)))
            
        elif package.type == "update":
            #TODO: add restart of system 
            try:
                packageToUpdate = self._installed_packages.get(package.targetId)
                if packageToUpdate is None:
                    raise Exception("Attempting to update not installed package, aborting")
                destinationPath = packageToUpdate.installPath
                
                extractedPackagePath = yield self._extract_package(sourcePath,tmpPath)
                extractedPackagePath = os.path.join(tmpPath,extractedPackagePath)
#                yield self._backup_files(".")
                dirCompare = filecmp.dircmp(destinationPath,extractedPackagePath,hide = [])
                filesToBackup = dirCompare.common
                 
                backupFolderName = os.path.splitext(packageToUpdate.file)[0]
                backupFolderName = backupFolderName.replace('-','_').replace('.','_').replace(' ','')+"_back"
                backupFolderName = os.path.join(self._path_manager.tmpPath,backupFolderName)
                #TODO: add id at end ?
                os.makedirs(backupFolderName)
                
                for fileDir in filesToBackup:
                    fileDir = os.path.join(destinationPath,fileDir)
                    if os.path.isdir(fileDir):
                        dir_util.copy_tree(fileDir, backupFolderName)
                    else:
                        file_util.copy_file(fileDir, backupFolderName)
                        
                dir_util.copy_tree(extractedPackagePath, destinationPath) 
                shutil.rmtree(backupFolderName)  
                packageToUpdate.version = package.toVersion
                self.send_signal("update_install_succeeded", package)
            except Exception as inst:
                raise Exception("Failed to install update: error %s" %(str(inst)))
        else:
                raise Exception("Unknown package type")  
    """
    ####################################################################################
    Helper Methods    
    """
    def _list_localPackages(self):
        """
        Scans the packages path for addons etc , and adds them to the list of currently available packages
        """
        #TODO : also parse info for main (pollapli) package
        packageDirs = os.listdir(self._path_manager._addon_path)
        for fileDir in packageDirs : 
            if zipfile.is_zipfile(fileDir):
                sourcePath = fileDir
                baseName = os.path.splitext(sourcePath)[0]
                baseName = baseName.replace('-','_').replace('.','_')
                tmpPath = os.path.join(self._path_manager.tmpPath,baseName)
                
                destinationPath = os.path.join(self._path_manager._addon_path,baseName)
                extractedPackageDir = yield self._extract_package(sourcePath,tmpPath) 
                extractedPackageDir = os.path.join(sourcePath,extractedPackageDir)
                shutil.copytree(extractedPackageDir, destinationPath)
                shutil.rmtree(tmpPath)
                os.remove(sourcePath)
                fileDir = destinationPath
            self.add_package_toPythonPath(fileDir)
    
    def _parse_packageListFile(self):
        packagesFileName = os.path.join(self._path_manager.tmpPath,"pollapli_packages.json")
        packageFile = file(packagesFileName,"r")
        packageInfos = json.loads(packageFile.read(),"iso-8859-1")    
        packageFile.close()

        packageList = [Package.from_dict(package) for package in packageInfos["packages"]]   
        newPackageCount = 0
        
        for package in packageList:
            if package.type == "update":
                if package.targetId in self._installed_packages.keys():
                    if package.fromVersion == self._installed_packages[package.targetId].version:
                        if self._available_packages.get(package.cid,None) is None:
                            self._available_packages[package.cid] = package
                            newPackageCount +=1
            elif package.type == "addon":
                if package.cid not in self._installed_packages.keys():
                    if self._available_packages.get(package.cid,None) is None:
                            self._available_packages[package.cid] = package
                            newPackageCount +=1
            
        if newPackageCount>0:
            self.send_signal("new_packages_available", newPackageCount)     
    
    def _backup_packageFiles(self,rootPath):
        d = defer.Deferred()
        return d
    
    def _extract_package(self,sourcePath,destinationPath):
        d = defer.Deferred()      
        def extract(sourcePath,destinationPath):
            if not zipfile.is_zipfile(sourcePath):
                raise Exception("invalid package extension")
            packageFile = ZipFile(sourcePath, 'r')
            packageFile.extractall(path = destinationPath)
            packageFile.close()
            return os.listdir(destinationPath)[0]
            
        d.addCallback(extract,destinationPath=destinationPath)
        reactor.callLater(0,d.callback,sourcePath)
        return d
    
    @defer.inlineCallbacks
    def _extract_allPackages(self):
        """
        helper "hack" function to extract egg/zip files into their adapted directories
        """
        #TODO: fix this
        packageDirs = os.listdir(self._path_manager._addon_path)
        for fileDir in packageDirs : 
            if zipfile.is_zipfile(fileDir):
                yield self._extract_package(fileDir)
            if os.path.isdir(fileDir):
                self.add_package_toPythonPath(fileDir)
        
        #should perhaps be like this:
        #if it is a zip file, use the install_package method
        #if it is a directory, check if is in the path, and if not , add it to the path
    
    def add_package_toPythonPath(self,path):
        if os.path.isdir(path):
            if not path in sys.path:
                sys.path.insert(0, path) 

    @defer.inlineCallbacks
    def update_addOns(self):
        """
        wrapper method, for extraction+ list package in case of newly installed addons
        """
        yield self.extract_addons()
        yield self.list_addons()

    def save_package_list(self):
        for package in self._installed_packages:
            import json
            json.dumps(package)
        
    