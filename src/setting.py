#!/usr/bin/env python

from os.path import expanduser
import os

# Modes
TEST_MODE = 1       # 1: evolutionary cpi test, 2: random test (random population)
SIM_MODE_REAL = True #False  #use real simulaion or dummay simulation? 
SCORE_OPTION = 1      # during evolutionary 1: cpi-score  2: crowd distance 3: random seleciton (tournmanet and top_n) 4: random population
#FIGON = 0   # (true,false) figure on for debug 
#NO_SIM_TEST = 0
DEBUG = 1       # detailed logs


#system-specific
USER_HOME = expanduser("~")
MAINNAME = None         #target system name
AUTOHOME = None         #target script home
#CPII_HOME = None        #main path: ~/cpii
CPII_HOME = USER_HOME + "/cpii"
CPII_OUTPUTS = CPII_HOME + "/outputs"
CPII_RESULT = CPII_HOME + "/result"
CPII_TESTLOG = CPII_HOME + "/testlog"

GZ_HOME = None          #gazebo home
COMMAND = None          #lauchning command for main controller

#paths
world_file = None
model_file = None
param_file = None
mission_file = None     #mission_file path
mavscript_file = None
last_sim_log = None     #LASTLOG.TXT
sim_log_name = None     #BIN filename
sim_log_file = None     #BIN path
test_log_name = None    #test_xxx.log
log_file = None         #testlog path
mission_log_file = None #mission log file


home_location = None
bounds = None 
mission_len = 5


## ==========================================================
## Configuration GEN30, N10
GEN = None                #number of generation
N = None                  #number of population (individual)
V = None                   # input#
M = None                   # objectives# (cyber)
M_P = None                 # objectives# (pysical)

MAX_INPUT = 40
Vrange = [0] * MAX_INPUT
Vlist = [0] * MAX_INPUT
Vmap = int('0000000000000000000000000000000000000000', 2) #bitmask for inputs


#Vrange = [[0, 2*3.14],[0, 2*3.14],[0, 2*3.14],[0, 2*3.14]]  # input range    [[min,max],...] size V
#Vrange = [[0, 30]]  #ixx
#Vrange = [[3, 4]]   #windgust strength
#Vrange = [[0, 30],[30,40]]  #ixx
#=============================================================

SIM_COUNT = 0       # total simulation count
CPI_COUNT = 0       # totla number of cpi found

# Define Inputs ==========
WORLD_WINDGUST_DIRECTION = 0    #xyz
WORLD_WINDGUST_DURATION = 1     #s
WORLD_WINDGUST_START = 2        #s
WORLD_WINDGUST_FORCEMEAN = 3     #n

MODEL_POSITION = 20  #xyz
MODEL_ROTATION = 21  #rpy
MODEL_INERTIA = 22   #xyz
MODEL_MASS = 23      #m
# ------------------------


INDEX_CODE = 0
INDEX_INPUT = 1
INDEX_OUTPUT = 2
INDEX_RANK = 3
INDEX_CPIRANK = 4

CODE_NONE = 0
CODE_COMP = 1   #mission completed
CODE_TP = 2
CDOE_TN = 3
CODE_FP = 4     #over-approximation
CODE_FN = 5     #under-approximation
# ================

# SIMULATION
MISSION_TIME = 0 # timeout  
LOOP_RATE = 0 #(Hz)                          #loop rate of the the target system
TIMEOUT = 0  #(sec)    #timeout in seconds  (MISSION_TIME/LOOP_RATE)
MODEL_DEVIATION = None  #not used yet
WAIT_TIME = 0 #(sec)


#ALPHA = 0.01    #gradient step - determines how much the input changes along the gradient of the cost function
#gradient_default = 0.0003
#

def read_setting():

    global GZ_HOME, AUTOHOME, COMMAND 
    global world_file, model_file, param_file, last_sim_log, sim_log_name, sim_log_file 
    global mission_file, mission_len, home_location, bounds
 

    ## System-specific settings 
    if MAINNAME == 'arducopter':
    
        MISSION_TIME = 400*60 * 4                   #(4min) timeout loop_count 24000=1(min)   
        LOOP_RATE = 400 #(Hz)                        #loop rate of the the target system
        TIMEOUT = MISSION_TIME / LOOP_RATE #(sec)    #timeout in seconds 24000(cnt)/400(Hz) = 1 min
        MODEL_DEVIATION = [0.098, 0.24, 0.01, 0.49]  #not used yet
        WAIT_TIME = 25 #(sec)
    
        AUTOHOME = USER_HOME + "/ardupilot/Tools/autotest"
        #COMMAND = "cd " + AUTOHOME + "; ./sim_vehicle.py -N -v ArduCopter -f gazebo-iris -m --mav10 --map --console -I1 -D"
        COMMAND = "cd " + AUTOHOME + "; ./sim_vehicle.py -v ArduCopter -f gazebo-iris -m --mav10 --map --console -I1 -D"
        #CPII_HOME = USER_HOME + "/cpii"
        if not os.path.exists(CPII_OUTPUTS):
            os.makedirs(CPII_OUTPUTS)
        if not os.path.exists(CPII_RESULT):
            os.makedirs(CPII_RESULT)
        if not os.path.exists(CPII_TESTLOG):
            os.makedirs(CPII_TESTLOG)

        GZ_HOME = USER_HOME + '/ardupilot_gazebo'
        world_file = GZ_HOME + '/worlds/copter.world'
        #model_file = GZ_HOME + '/models/fs_box/model.sdf'
        #model_file = GZ_HOME + '/models/tunnel/model.sdf'
        model_file = GZ_HOME + '/models/fs_gray_wall/model.sdf'  # more models are addable with new paht variables 
        param_file = CPII_HOME + '/param.txt'

        last_sim_log = AUTOHOME + '/logs/LASTLOG.TXT'
        sim_log_name = open(last_sim_log).readline().rstrip().rjust(8,'0') + ".BIN"  # simulation raw log (BIN)
        sim_log_file = AUTOHOME + '/logs/' + sim_log_name

        mission_file = AUTOHOME + '/mission.txt'
        mission_len = 5         #0 home 1 takeoff 2~5 
        home_location = [-35.3632619999999989, 149.165236999999991, 584.080016999999998]
        #UD LR ALT TIME
        bounds = [home_location[0]-0.0002, home_location[0]+0.0002, home_location[1]-0.0003, home_location[1]+0.0003, 10, 50, 0, 0] 
    
    
    else:
        print "ERROR: Not supported system: ", MAINNAME
        exit(0)

    
    print ("---------------------")
    print ("SYSTEM NAME  : %s") % MAINNAME
    print ("AUTO HOME    : %s") % AUTOHOME
    print ("CPII HOME    : %s") % CPII_HOME
    print ("GZ_HOME      : %s") % GZ_HOME
    print ("COMMAND      : %s") % COMMAND
    print ("MISSION_TIME : %d") % MISSION_TIME
    print ("MISSION_FILE : %s") % mission_file
    print ("LOOP_RATE    : %d") % LOOP_RATE
    print ("TIMEOUT      : %d") % TIMEOUT
    print ("HOME:        : {}".format(home_location))
    print ("BOUNDS:      : {}".format(bounds))
    print ("---------------------")
    print ("GENERATION   : %d") % GEN
    print ("POPULATION   : %d") % N
    print ("OBJECTIVES C : %d") % M
    print ("OBJECTIVES P : %d") % M_P
    print ("#INPUTS      : %d") % V
    print "INPUT_BITMASK:", "{0:040b}".format(Vmap)
    print "INPUT RANGE  :", Vrange 
    print "SIM_REAL     :", SIM_MODE_REAL
    print "SCORE_OPTION :", SCORE_OPTION
    print "TEST_MODE    :", TEST_MODE
    print ("---------------------")

