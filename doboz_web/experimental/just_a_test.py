import subprocess,os


def subprocessTest():
    trucpath=os.path.join("d:\\Progra","arduino-0018","arduino.exe")
    trucpath=os.path.join("d:\\","data","projects","Doboz","doboz_web","dependencies","scons","scons.py")

    print("trucpath",trucpath)
    args=["python",trucpath]
    p = subprocess.Popen(args)
    
def usbTest():
    import win32com.client
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_USBController")
    for objItem in colItems:
#        print "Availability: ", objItem.Availability
        print "Caption: ", objItem.Caption
#        print "Config Manager Error Code: ", objItem.ConfigManagerErrorCode
#        print "Config Manager User Config: ", objItem.ConfigManagerUserConfig
        print "Creation Class Name: ", objItem.CreationClassName
        print "Description: ", objItem.Description
        print "Device ID: ", objItem.DeviceID
#        print "Error Cleared: ", objItem.ErrorCleared
#        print "Error Description: ", objItem.ErrorDescription
#        print "Install Date: ", objItem.InstallDate
#        print "Last Error Code: ", objItem.LastErrorCode
        print "Manufacturer: ", objItem.Manufacturer
        print "Max Number Controlled: ", objItem.MaxNumberControlled
        print "Name: ", objItem.Name
        print "PNP Device ID: ", objItem.PNPDeviceID
        z = objItem.PowerManagementCapabilities
        if z is None:
            a = 1
        else:
            for x in z:
                print "Power Management Capabilities: ", x
#        print "Power Management Supported: ", objItem.PowerManagementSupported
#        print "Protocol Supported: ", objItem.ProtocolSupported
#        print "Status: ", objItem.Status
#        print "Status Info: ", objItem.StatusInfo
        print "System Creation Class Name: ", objItem.SystemCreationClassName
        print "System Name: ", objItem.SystemName
#        print "Time Of Last Reset: ", objItem.TimeOfLastReset

if __name__=="__main__":
    usbTest()