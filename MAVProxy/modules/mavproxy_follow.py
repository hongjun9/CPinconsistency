"""
    MAVProxy follow module, for testing FOLLOW mode
"""

from pymavlink import mavwp
from pymavlink import mavutil
import time, os, platform
from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util

if mp_util.has_wxpython:
    from MAVProxy.modules.lib.mp_menu import *

class FollowModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(FollowModule, self).__init__(mpstate, "follow", "follow mode control", public = True)
        self.followloader = mavwp.MAVFollowLoader(self.settings.target_system, self.settings.target_component)
        self.have_list = False
        self.abort_alt = 50
        self.abort_first_send_time = 0
        self.abort_previous_send_time = 0
        self.abort_ack_received = True

        self.menu_added_console = False
        self.menu_added_map = False
        self.add_command('follow', self.cmd_follow, "follow commands")
        if mp_util.has_wxpython:
            self.menu = MPMenuItem('Follow', 'Follow', '# follow setpos');

    def idle_task(self):
        '''called on idle'''
        if self.module('map') is not None and not self.menu_added_map:
            self.menu_added_map = True
            self.module('map').add_menu(self.menu)

    def print_usage(self):
        print("Usage: follow setpoint")

    def cmd_follow(self, args):
        '''follow commands'''
        if len(args) < 1:
            self.print_usage()
            return

        elif args[0] == "setpos":
            self.cmd_follow_setpos()

    def cmd_follow_setpos(self):
        try:
            latlon = self.module('map').click_position
        except Exception:
            print("No map available")
            return
        if latlon is None:
            print("No map click position available")
            return
        self.master.mav.set_position_target_local_ned_send(
                                      0,  # system time in milliseconds
                                      1,  # target system
                                      0,  # target component
                                      8,  # coordinate frame MAV_FRAME_BODY_NED
                                      455,      # type mask (vel only)
                                      0, 0, 0,  # position x,y,z
                                      x_mps, y_mps, z_mps,  # velocity x,y,z
                                      0, 0, 0,  # accel x,y,z
                                      0, 0)     # yaw, yaw rate
        
        self.cmd_rally_add(args[1:])

    def print_usage(self):
        print("Usage: follow <list|load|land|save|add|remove|move|clear|alt>")

def init(mpstate):
    '''initialise module'''
    return FollowModule(mpstate)
