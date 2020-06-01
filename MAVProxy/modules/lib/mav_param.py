from pymavlink import mavparm

class mav_param(mavparm.MAVParmDict):
    '''subclass of MAVParmDict with command() for common commmandline set'''

    def command_set(self, mav, args):
        '''handle command line set on a parameter'''
        if len(args) < 1:
            print("Usage: param set PARMNAME VALUE")
            return
        if len(args) == 1:
            self.show(args[0])
            return
        param = args[0].upper()
        value = args[1]
        if not param.upper() in self:
            print("Unable to find parameter '%s'" % param)
            return
        self.mavset(mav, param, value, retries=3)
