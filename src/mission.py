#!/usr/bin/env python

import random
import setting
from pymavlink import mavutil
import argparse

#
# system-specfiic 
#
arduCommandTable = {

    ##NAVIGATION COMMANDS
    'takeoff'    : 'MAV_CMD_NAV_TAKEOFF',          #param7: Alt
                                                   #first command
    'straightwp' : 'MAV_CMD_NAV_WAYPOINT',         #param1: Delay (sec), param5: Lat, param6: Lon, param7: Alt
    'splinewp'   : 'MAV_CMD_NAV_SPLINE_WAYPOINT',  #param1: Delay (sec), param5: Lat, param6: Lon, param7: Alt
    'circle'     : 'MAV_CMD_NAV_LOITER_TURNS',     #param1: Turns# (360 degrees), param5: Lat, param6: Lon, param7: Alt
                                                   #circle flight mode
    'wait'       : 'MAV_CMD_NAV_LOITER_TIME',      #param1: Time (sec), param5: Lat, param6: Lon, param7: Alt
                                                   #Loiter flight mode
    'rtl'        : 'MAV_CMD_NAV_RETURN_TO_LAUNCH', #RTL flight mode
                                                   #last command
    'land'       : 'MAV_CMD_NAV_LAND',             #param5: Lat, param6: Lon
                                                   #Land flight mode
    'cmdjump'    : 'MAV_CMD_DO_JUMP',              #param1: WP#, param2: Repeat#

    ##CONDITION COMMANDS
    'delay'      : 'MAV_CMD_CONDITION_DELAY',      #param1: Time (sec)
    'changealt'  : 'MAV_CMD_CONDITION_CHANGE_ALT', #param1: Rate (m/sec), param7: Alt
    'distance'   : 'MAV_CMD_CONDITION_DISTANCE',   #param1: Dist (m)
    'changehead' : 'MAV_CMD_CONDITION_YAW',        #param1: Deg, param3: Dir (add or subtract for Rel), param4: Rel or Abs

    ##DO COMMANDS
    'changespeed': 'MAV_CMD_DO_CHANGE_SPEED',      #param2: Speed (m/sec)
    'sethome'    : 'MAV_CMD_DO_SET_HOME'           #param1: Current (1=current,2=in-message), param5: Lat, param6: Lon, param7: Alt
                              
    ##ADDITIONAL DO COMMANDS
    #MAV_CMD_DO_SET_RELAY,                         #param1: Relay no., param2: Off(0) or On(1)
    #MAV_CMD_DO_REPEAT_RELAY,                      #param1: Relay no., param2: Repeat#, param3: Delay (sec)
    #MAV_CMD_DO_SET_SERVO,                         #param1: Servo no., param2: PWM (microsec, typically 1000-to-2000)
    #MAV_CMD_DO_REPEAT_SERVO,                      #param1: Servo no., param2: PWM (microsec, typically 1000-to-2000), param3: Repeat#, param4: Delay (sec)s
    #MAV_CMD_DO_SET_ROI,                           #param5: Lat, param6: Lon, param7: Alt (of the fixed ROI i.e., region of interest)
    #MAV_CMD_DO_DIGICAM_CONFIGURE,                 #param1: Mode (1: ProgramAuto 2: Aperture Priority 3: Shutter Priority 4: Manual 5: IntelligentAuto 6: SuperiorAuto),
    #                                              #param2: Shutter speed, param3: Aperture, param4: ISO (e.g., 80,100,200), param7: Engine cut-off time
    #MAV_CMD_DO_DIGICAM_CONTROL,                   #param1: Off(0) or On(1), param4: Focus lock (0: Ignore 1: Unlock 2: Lock), param5: Shutter command (any non-zero value)
    #MAV_CMD_DO_MOUNT_CONTROL,
    #MAV_CMD_DO_SET_CAM_TRIGG_DIST,
    #MAV_CMD_DO_PARACHUTE    
}

px4CommandTable = {

    'takeoff'    : 'MAV_CMD_NAV_TAKEOFF',           #NAV_CMD_TAKEOFF
    'straightwp' : 'MAV_CMD_NAV_WAYPOINT',          #NAV_CMD_WAYPOINT
    'wait'       : 'MAV_CMD_NAV_LOITER_TIME',       #NAV_CMD_LOITER_TIME_LIMIT
    'land'       : 'MAV_CMD_NAV_LAND',              #NAV_CMD_LAND
    'cmdjump'    : 'MAV_CMD_DO_JUMP'                #NAV_CMD_DO_JUMP
                             
    #MAV_CMD_DO_SET_SERVO                           #NAV_CMD_DO_SET_SERVO
    #MAV_CMD_DO_DIGICAM_CONTROL                     #NAV_CMD_DO_DIGICAM_CONTROL
}



def generateRandomMission(seq, home_location, mission_file, missionLen, bounds):

    print "BOUND", bounds
    xminIn = bounds[0]
    xmaxIn = bounds[1]
    yminIn = bounds[2]
    ymaxIn = bounds[3]
    zminIn = bounds[4]
    zmaxIn = bounds[5]
    timeMin = int(bounds[6])
    timeMax = int(bounds[7])

    #filename = "mission_" + str(seq) + ".txt"
    #filepath = setting.CPII_HOME + "/" + filename
    filepath = setting.mission_log_file
    missionFormat = ['takeoff']     #start command
    output = 'QGC WPL 110\n'

    # flight modes
    stateTable = {
        #'takeoff'     : ['straightwp', 'splinewp', 'circle', 'wait', 'rtl', 'land'],
        #'straightwp'  : ['straightwp', 'splinewp', 'circle', 'wait', 'rtl', 'land', 'changespeed'],
        #'splinewp'    : ['straightwp', 'splinewp', 'circle', 'wait', 'rtl', 'land', 'changespeed'],
        #'circle'      : ['straightwp', 'splinewp', 'circle', 'wait', 'rtl', 'land'],
        #'wait'        : ['straightwp', 'splinewp', 'circle', 'wait', 'rtl', 'land'],
        #'rtl'         : ['takeoff'],
        #'land'        : ['takeoff'],
        #'changespeed' : ['straightway', 'splinewp']

        # 'takeoff'    : ['straightwp', 'land', 'wait'],
        # 'straightwp' : ['straightwp', 'land', 'wait','cmdjump'],
        # 'land'       : ['takeoff'],
        # 'cmdjump'    : ['straightwp', 'land']

        # transition
        'takeoff': ['straightwp', 'wait'],
        'straightwp': ['straightwp', 'wait'],
        'wait': ['straightwp', 'wait'],
        'land': ['takeoff']
    }

    ##
    # MAV_CMD_NAV_TAKEOFF : 22
    # MAV_CMD_NAV_WAYPOINT : 16
    # MAV_CMD_NAV_LAND : 21

    #<INDEX> <CURRENT WP> <COORD FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <PARAM5/X/LONGITUDE> <PARAM6/Y/LATITUDE> <PARAM7/Z/ALTITUDE> <AUTOCONTINUE>

    '''
QGC WPL 110
0    1    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
1    0    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
2    0    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
    '''
    ## mission command format: seq,current,frame,command,   param1,param2,param3,param4,param5,param6,param7,autocontinue

    ## write home and takeoff command to mission file

    # index 0 and 1
    currentCmd = missionFormat[0]   #takeoff
    alt = random.uniform(zminIn, zmaxIn)
    commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
        (0, 0, 0, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, home_location[0], home_location[1], home_location[2], 1)
    output += commandline
    commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
        (1, 1, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, home_location[0], home_location[1], alt, 1)
    output += commandline


    # index 2~
    for i in xrange(2,missionLen+1):    #2~missionLen
        nextCmds = stateTable.get(currentCmd)
        currentCmd = random.choice(nextCmds)
        missionFormat.append(currentCmd)

        lat = random.uniform(xminIn, xmaxIn)
        lon = random.uniform(yminIn, ymaxIn)
        alt = random.uniform(zminIn, zmaxIn)

        ## write current command to mission file
        if currentCmd == 'takeoff':
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (i, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, home_location[0], home_location[1], alt, 1)    #22

        elif currentCmd == 'straightwp':
            delay = random.randint(timeMin, timeMax)
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (i, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, delay, 0, 0, 0, lat, lon, alt, 1)    ## 16

        elif currentCmd == 'wait':
            delay = random.randint(timeMin, timeMax)
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (i, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME, delay, 0, 0, 0, lat, lon, alt, 1)

        elif currentCmd == 'land':
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (i, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, lat, lon, 0, 1)    # 21
        output += commandline


    if currentCmd != 'land':
        ## write land command to mission file
        missionFormat.append('land')
        commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                      (missionLen+1, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, lat, lon, 0, 1)
        output += commandline


    #store mission file for save 
    if filepath != None:
        with open(filepath, 'w') as f:
            f.write(output)
        f.close()
        print "mission file (backup):", filepath

    #create mission file to use
    with open(mission_file, 'w') as f:
        f.write(output)
    f.close()
    print "mission file:", mission_file
    print output


def generateRandomMissionFile(home_location, filename, mission_commands, bounds):
    output = 'QGC WPL 110\n'
    row = 0     #INDEX

    # home command
    commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                  (row, 0, 0, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, home_location[0], home_location[1],
                   home_location[2], 1)
    output += commandline
    row = row + 1

    ##
    # MAV_CMD_NAV_TAKEOFF : 22
    # MAV_CMD_NAV_WAYPOINT : 16
    # MAV_CMD_NAV_LAND : 21

    #<INDEX> <CURRENT WP> <COORD FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <PARAM5/X/LONGITUDE> <PARAM6/Y/LATITUDE> <PARAM7/Z/ALTITUDE> <AUTOCONTINUE>

    '''
QGC WPL 110
0    1    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
1    0    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
2    0    0    16    0.149999999999999994    0    0    0    8.54800000000000004    47.3759999999999977    550    1
    '''

    for currentCmd in mission_commands:
        print currentCmd
        if currentCmd == 'takeoff':
            if row == 1: current = 1
            alt = random.uniform(bounds[4], bounds[5])
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                         (row, current, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, home_location[0], home_location[1], alt, 1)
            current = 0

        elif currentCmd == 'straightwp':
            delay = int(random.uniform(bounds[6], bounds[7]))
            lat = random.uniform(bounds[0], bounds[1])
            lon = random.uniform(bounds[2], bounds[3])
            alt = random.uniform(bounds[4], bounds[5])
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (row, current, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, delay, 0, 0, 0, lat, lon, alt, 1)

        elif currentCmd == 'wait':
            time = int(random.uniform(bounds[6], bounds[7]))
            lat = random.uniform(bounds[0], bounds[1])
            lon = random.uniform(bounds[2], bounds[3])
            alt = random.uniform(bounds[4], bounds[5])
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (row, current, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LOITER_TIME, time, 0, 0, 0, lat, lon, alt, 1)

        elif currentCmd == 'land':
            lat = random.uniform(bounds[0], bounds[1])
            lon = random.uniform(bounds[2], bounds[3])
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % \
                          (row, current, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, lat, lon, 0, 1)

        else:
            commandline = "[ERROR] Not supported command"
            return output


        output += commandline
        print output
        row = row + 1

    #create mission file
    with open(filename, 'w') as f:
        f.write(output)
        print output
    f.close()
    print "mission file:", filename
    print output


def main():
    
    home_location = [-35.3632619999999989, 149.165236999999991, 584.080016999999998]
    #[0 1]up down,  [2 3]left right, [4 5]alt,  [6 7]time 
    default_bounds = [home_location[0]-0.0002, home_location[0]+0.0002, home_location[1]-0.0003, home_location[1]+0.0003, 10, 50, 0, 0]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', help="home locaiton [lat, lon, alt]), default = [-35.3636, 149.1652, 584.0]", default=home_location)
    parser.add_argument('--length', help="mission length, default=5", default=5)
    parser.add_argument('--bounds', help="geo bounds (up,down, left, right, alt, time_start, time_end), default=[home-0.0002, home+0.002, home-0.0003, home+0.0003, 10, 50, 0, 0]",  default=default_bounds)

    args = parser.parse_args()
    home_location = args.home
    mission_len = args.length
    bounds = args.bounds


    mission_command = ['takeoff', 'straightwp', 'land']
    missionfile = '/home/apm/cpii/mission.txt' 
    seq = 1     # starting mission index

    print "Home", home_location
    print "MIssion File", missionfile
    print "MIssion Command", mission_command

    generateRandomMission(seq, home_location, missionfile, mission_len, bounds)



if __name__ == '__main__':
    main()
