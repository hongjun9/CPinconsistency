#!/usr/bin/env python

import time, datetime
import logger as log
import random
import argparse
import setting
import evolutionary
import mission

def main():

    random.seed(0)
    # global evolution log
    #test_id = datetime.datetime.now().strftime("%Y%m%d_%I%M%S_%f")
    test_id = datetime.datetime.now().strftime("%Y%m%d_%I%M%S")

    setting.test_log_name = "test_" + test_id + ".log"                   #log file name
    setting.log_file = setting.CPII_TESTLOG + "/" + setting.test_log_name   #log file path 
    setting.mission_log_file = setting.CPII_TESTLOG + "/mission_" + test_id + ".txt" 

    log_level = log.DEBUG #INFO
    log.init(setting.log_file, log_level) 

    # mission generation
    mission.generateRandomMission(test_id, setting.home_location, setting.mission_file, setting.mission_len, setting.bounds) 
    
    #=============================================================
    print("[**] CPI test starting..")
    start_time = time.time()

    if (setting.TEST_MODE == 2):
    
        ## Random testing
        evolutionary.random_population(test_id, setting.GEN); 

    elif (setting.TEST_MODE == 1):

        ## Evolutionary testing
        if (setting.N <= 3):
            print "Check num_parameters!! (N <= 3)"
            exit()

        ## start the Evolution process (T evolutions)
        evolutionary.evolution(test_id)

    else:
        print "ERROR: NOT SUPPORTED TEST MODE"

    # test stat ========================================================
    log.info("================= TEST STATS ====================")
    log.info("Population logs: genout_" + str(test_id) + ".log")
    log.info("#POP: " + str(setting.GEN*setting.N))
    log.info("#CPI cases: " + str(setting.CPI_COUNT))

    elapsed_time = time.time() - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info("#TOTAL_SIM: " + str(setting.SIM_COUNT) + ", TOTAL_TIME: " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))



if __name__ == '__main__':

    #wind direction (xyz: 0-180, 0-170, 0-160), wind duration (sec: 0-10), wind start (sec: 10-30), wind force (N: 0-30)
    #model inertia (xyz: 0-31, 0-32, 0-32), mass (kg: 0-50)
    default_inputs = 1<<setting.WORLD_WINDGUST_DIRECTION | 1<<setting.WORLD_WINDGUST_DURATION | 1<<setting.WORLD_WINDGUST_START | 1<<setting.WORLD_WINDGUST_FORCEMEAN | 1<<setting.MODEL_INERTIA | 1<<setting.MODEL_MASS
    default_range = [[0,180, 0, 170, 0, 160], [0,10], [10, 30], [0,30],[0,31, 0,32, 0,33],[0,50]]

    parser = argparse.ArgumentParser()
    parser.add_argument('--target', help='target system', default='arducopter')#, required=True)
    parser.add_argument('--gen', help='num of generation GEN', default='20', type=int)
    parser.add_argument('--pop', help='num of population N', default='10', type=int)
    parser.add_argument('--M', help='num of cyber outputs M', default='3', type=int)
    parser.add_argument('--M_P', help='num of pysical outputs M_P', default='3', type=int)
    parser.add_argument('--V', help='num of inputs', default='10', type=int)
    parser.add_argument('--Vmap', help='bitmask for inputs', default=default_inputs, type=int)
    parser.add_argument('--range', help='input ranges', nargs='+', default=default_range, type=float)
    parser.add_argument('--sim_real', help='simulation mode', default=False)
    parser.add_argument('--score_option', help='score option (default: cpi score)', default=1)
    parser.add_argument('--test_mode', help='test mode (default 1: cpi-ea, 2: random)', default=1)

    args = parser.parse_args()

    setting.MAINNAME = args.target
    setting.GEN = args.gen
    setting.N = args.pop 
    setting.V = args.V
    setting.M = args.M
    setting.M_P = args.M_P
    setting.Vmap = args.Vmap
    index = 0
    for i in range(setting.MAX_INPUT):    #input ranges
        if(setting.Vmap & 1<<i): 
            setting.Vrange[i] = args.range[index]
            index = index + 1

    setting.SIM_MODE_REAL = args.sim_real
    setting.SCORE_OPTION = args.score_option
    setting.TEST_MODE = args.test_mode
    setting.read_setting()  #print settings

    #compare #input and V
    range_list = [i for i, e in enumerate(setting.Vrange) if e != 0]
    input_num = 0
    for i in range_list:
        input_num = input_num + len(setting.Vrange[i])/2
    if(input_num != setting.V):
        print("[ERROR] check the number of input V and range Vrange")
        exit()
    
    main()

