"""Parser that converts gcodes to pollapli commands"""
import re
from twisted.python import log
from pollapli.core.hardware.commands import EnableDisableComponents,\
    SetVariableTarget


class FiveDPoint():
    def __init__(self, x=0, y=0, z=0, e=0, f=0):
        self.x = x
        self.y = y
        self.z = z
        self.e = e
        self.f = f

    def __str__(self):
        return "["+str(self.x)+","+str(self.y)+","+str(self.z)+","+str(self.e)+","+str(self.f)+"]"


class GCodeParser(object):
    def __init__(self):
        pattern = "(?P<t>[G|M][-+]?[0-9]*\.?[0-9]+)\s?(S(?P<s>[-+]?[0-9]*\.?[0-9]+))?\s?(X(?P<x>[-+]?[0-9]*\.?[0-9]+))?\s?(Y(?P<y>[-+]?[0-9]*\.?[0-9]+))?"
        pattern += "\s?(Z(?P<z>[-+]?[0-9]*\.?[0-9]+))?\s?(F(?P<f>[-+]?[0-9]*\.?[0-9]+))?\s?(E(?P<e>[-+]?[0-9]*\.?[0-9]+))?"

        #BUT IT would be good to make a  regex to match all blocks anywhere
        #pattern="(\S[^G1|G0])?(?P<t>G1|G0)?(\S[^G1|G0])?"
        self.gcodeRe = re.compile(pattern)

    def parse(self, line):
        """parses a gcode line"""
        command = None
        try:
            result = self.gcodeRe.search(line)
            commandType = result.group('t')

            if commandType == "M17":
                command = EnableDisableComponents(component_category="actuator", component_type="stepper", component_on=True)
            elif commandType == "M18":
                command = EnableDisableComponents(component_category="actuator", component_type="stepper", component_on=False)
            elif commandType == "M103":
                command = EnableDisableComponents(component_category="actuator", component_type="extruder", component_on=False)
            elif commandType == "M104":
                value = float(result.group("s"))
                command = SetVariableTarget(variable="temperature", target_value=value)
            elif commandType == "G0":
                pos = FiveDPoint()
                for dim in ['x', 'y', 'z', 'e', 'f']:
                    try:
                        r = result.group(dim)
                        if r:
                            setattr(pos, dim, float(r))
                    except Exception as inst:
                        print("error", inst)
                command = SetVariableTarget(variable="position", target_value=pos)
            elif commandType == "G1":
                pos = FiveDPoint()
                for dim in ['x', 'y', 'z', 'e', 'f']:
                    try:
                        r = result.group(dim)
                        if r:
                            setattr(pos, dim, float(r))
                    except Exception as inst:
                        print("error", inst)
                command = SetVariableTarget(variable="position", target_value=pos)
        except Exception as inst:
            log.msg("Error in parsing gcode line")

        return command
#        pos = None
#        try:
#            result = self.gcodeRe.search(line)
#            if result:
#                pos = FiveDPoint()
#                for dim in ['x', 'y', 'z', 'e', 'f']:
#                    try:
#                        r = result.group(dim)
#                        if r:
#                            setattr(pos,dim,float(r))
#                    except Exception as inst:
#                        print("error",inst)
#            try:
#                commandType = result.group('t')
#                #need mapping of command type to ...
#                #print("Type",type)
#                if commandType != "G1" and commandType !="G0":
#                    pos = None
#            except:pass
#        except Exception as inst:
#            pass
#        #print("ParsedPos",str(pos))
#        return pos

if __name__ == "__main__":
    gcode_parser = GCodeParser()
    gcode_parser.parse("G1 X-11.4 Y-22.21 Z0.2 F180.0 E0.318")
    gcode_parser.parse("G0X10.0Y-0.25Z12.0")
    gcode_parser.parse("M104")
    #g.parse("G0X10.0Y-0.25Z12.0E2F1600.00")
