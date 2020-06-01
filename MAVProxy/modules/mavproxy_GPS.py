#!/usr/bin/env python
'''
support for a GCS attached GPS

tested using the builtin GPS on a X230 Thinkpad
'''

import serial, time
from pynmea.streamer import NMEAStream

mpstate = None

class module_state(object):
    def __init__(self):
        self.device = None
        self.port = None
        self.nmea = None

def convert_nmea_degrees(nmea_degrees):
    '''convert NMEA formatting latitude/longitude to decimal degrees'''
    deg = int(nmea_degrees * 0.01)
    decimal = (nmea_degrees - deg*100) / 60.0
    return deg + decimal

def idle_task():
    '''called in idle time'''
    state = mpstate.GPS_state
    if state.nmea is None:
        return
#    s = state.port.read(200)
#    if s:
#        print(s)
    try:
        next_data = state.nmea.get_objects()
    except IndexError:
        return
    print("n1", next_data)
    nmea_objects = []
    while next_data:
        nmea_objects += next_data
        try:
            next_data = state.nmea.get_objects()
        except IndexError:
            break
    print("n2", nmea_objects)
    for obj in nmea_objects:
        print(obj.sen_type)
        if obj.sen_type == 'GPGGA':
            print(obj.latitude, obj.longitude, obj.num_sats, obj.timestamp)
#            latitude = convert_nmea_degrees(float(obj.latitude))
#            longitude = convert_nmea_degrees(float(obj.longitude))
#            print(latitude, longitude)

def name():
    '''return module name'''
    return "GPS"

def description():
    '''return module description'''
    return "ground station attached GPS support"

def mavlink_packet(pkt):
    pass

def cmd_GPS(args):
    '''set GPS device'''
    state = mpstate.GPS_state
    if len(args) != 1:
        print("Usage: GPS <device>")
        return
    state.device = args[0]
    state.port = serial.Serial(state.device, 38400, timeout=0,
                               dsrdtr=False, rtscts=False, xonxoff=False)
    state.port.write("AT*E2GPSCTL=1,5,1\r\n")
    time.sleep(2)
    state.port.write("AT*E2GPSNPD\r\n")
    time.sleep(2)
    state.nmea = NMEAStream(stream_obj=state.port)

def init(_mpstate):
    '''initialise module'''
    global mpstate
    mpstate = _mpstate
    state = module_state()
    mpstate.GPS_state = state
    mpstate.command_map['GPS'] = (cmd_GPS, "GPS setup")
