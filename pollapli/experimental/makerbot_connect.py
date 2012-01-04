import serial
import struct
import time


def runcommand(payload):
    command = "\xd5"+chr(len(payload))+payload+crc(payload)
    ser.write(command)
    time.sleep(1)
    first = ser.read()
    if first == '':
        raise Exception("No response")
    if first != '\xd5':
        raise Exception("Bad leading byte")
    length = ord(ser.read())
    rec = "".join(ser.read()  for i in range(length))
    rcrc = ser.read()
    if rcrc != crc(rec):
        raise Exception("Return crc mismatch")
    return rec

def crc(payload):
    b = 0
    for c in payload:
       b = (b ^ ord(c)) & 0xff
       for i in range(8):
           if b & 0x01:
               b = ((b >> 1) ^ 0x8c)
           else:
               b = b >> 1
    return chr(b)

# prints 'Cupcake'
def getversion():
    return runcommand("\x14\x1c\x00")

def getversion2():
    return runcommand("\x00\x1d\x00")

def getpos():
    res = runcommand("\x04")
    return struct.unpack("<iiis", res[1:])

# setpos(0,0,0) would set current point to home
def setpos(x, y, z):
    return runcommand("\x82"+struct.pack("<iii", x, y, z))

def abort():
    return runcommand("\x07")

def getbuffsize():
    res = runcommand("\x02")
    return struct.unpack("<i", res[1:])[0]

def init():
    #actually seen in repg logs:
    #d5 3 0 1d 0 65
    #d5 3 14 1d 0 b1
    pass

def pulseDTR(ser):
    ser.setDTR(1)
    time.sleep(0.022)
    ser.setDTR(0)

def pulseRTS(ser):
    ser.setDTR(0)
    ser.setRTS(0)
    time.sleep(0.022)
    ser.setDTR(1)
    ser.setRTS(1)

#baudRates = [19200,38400,57600,115200]
baudRates = [115200]

def attemptConnection(ser): 
    ser.flush()
    ser.flushInput()
    ser.flushOutput()
    try:
        version = getversion()
        print("got version",version)
        return True
    except:pass
    return False

is_connected = False
port = "COM7"
port = "/dev/ttyUSB0"
for speed in baudRates:
    print("Connecting at speed %i" % speed)
    ser = serial.Serial(port, speed, timeout=2.6)
    ser.flush()
    ser.flushInput()
    ser.flushOutput()
    time.sleep(2.6)
    for i in range(5):
        print("Attempt %i" % i)
        if attemptConnection(ser) :
            is_connected = True
            break
        if i == 1:
            pulseDTR(ser)
        time.sleep(2.6)
    if is_connected:
        setpos(20,8,12)
        x,y,z,a = getpos()
        print("x:%s, y:%s, z:%s, a:%s" % (x,y,z,a))
        vinfo = getversion2()
        print(vinfo)
    ser.close()
#    try:
#        v = getversion2()
#    except Exception as inst:
#        print("error",inst)
#        pulseDTR(ser)
#    ser.timeout = 2.6
#    for i in range(5):
#        try:
#            #ser.write("\xd5\x03\x14\x1d\x00\xb1")
#            #ser.write("\xd5\x03\x00\x1d\x00\x65")
#            #getversion()
#            getbuffsize()
#            #getversion2()
#        except Exception as inst:
#            print("Error %s" % str(inst))
    