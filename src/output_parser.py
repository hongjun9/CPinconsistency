#!/usr/bin/env python
#Arducopter output formatting
#analyze simulaiton log and generate code/costs
import os
import logger as log
import random
from termcolor import colored, cprint
import setting

geo_bound = []  # [xmin, xmax, ymin, ymax, zmin, zmax] position bounds from the trajectory in the seed simulation
tunnel = []

'''
    system specific output processing
    input: output log
    output: [result_code, costs (cyber and physical)]
'''

def process_output(name, simlog_id):


    if(name == 'arducopter'):

        # Simulation (raw BIN) log 
        sim_log_name = open(setting.last_sim_log).readline().rstrip().rjust(8,'0') + ".BIN"
        sim_log_file = setting.AUTOHOME + '/logs/' + sim_log_name
        print("simlog(BIN) copy: " + sim_log_file + ' to' + setting.CPII_HOME + '/outputs/simout_' + simlog_id + '.BIN')

        # copy BIN log to output folder
        if not os.path.isfile(sim_log_file):
            print("simlog(BIN) not exists: " + sim_log_file)
        else:
            copyfile(sim_log_file, setting.CPII_HOME + '/outputs/simout_' + simlog_id + '.BIN')     


        # simulation output (c/p costs) from control program
        sim_outfile_name = 'simout_' + simlog_id + '.log'  
        sim_outfile = setting.CPII_HOME + '/outputs/' + sim_outfile_name

        #output_vector:[cpi-code, [c_cost], [p_cost]]
        output_vector = output_parser.arducopter_process_output(sim_outfile, setting.M, setting.M_P, setting.V) 
        print("debug: [output_vector] " + str(output_vector))

        
        log.cinfo("=== Collecting outputs: %s %s" % (sim_log_file, sim_outfile))

        exit()

    #elif setting.MAINNAME == 'px4':
    # add your system
        #sim_log_name = open(setting.last_sim_log).readline().rstrip()
        #sim_log_file = setting.HOME + "/build/posix_sitl_default/tmp/" + sim_log_name
        #print("simlog(ulg) copy: " + sim_log_file + ' to' + setting.CPII_HOME + '/outputs/simout_' + simlog_id + '.ulg')
        #if not os.path.isfile(sim_log_file):
        #    print "Not exists: ", sim_log_file
        #else:
        #    copyfile(sim_log_file, setting.CPII_HOME + '/outputs/simout_' + simlog_id + '.ulg')     

        #sim_outfile_name = 'simout_' + simlog_id + '.log'   #simulation output log by control program
        #sim_outfile = setting.CPII_HOME + '/outputs/' + sim_outfile_name
        #log.cinfo("=== Collecting outputs: %s %s" % (sim_outfile, sim_log_file))

        ##output_vector: [cpi-code, [c_cost], [p_cost]]
        #output_vector = output_parser.px4_process_output(sim_outfile, setting.M)      

    else:
        print "ERROR: Not supported system: ", MAINNAME
        exit(0)




def arducopter_process_output(sim_outfile, M, M_P, V):
    exists = os.path.isfile(sim_outfile)
    output = 0, [float('inf')],[float('inf')]  #sim error

    if not exists:
        cprint(" !!![Error] cpii_output (sim_outfile) does not exist. Check simulation", 'red')
        print "sim_outfile:", sim_outfile
        #f = open(sim_outfile, "w")
        #output_str = "[ERROR] No SIMULATION\n"
        #f.write(output_str)
        return output

    print "-----------------Process Outputs-------------------"
    print "FILE: " + sim_outfile
    with open(sim_outfile) as fp:
        line = fp.readline()
        while line:
            if 'ERR' in line:                     # error with codes
                cprint(line.strip(), 'red')
            if '[FN]' in line or '[FP]' in line or '[TP]' in line or '[TN]' in line:
                cprint(line.strip(), 'red')
                output = line.split()
                result = output[0]
                code = 0
                if result == '[FN]':
                    code = setting.CODE_FN
                elif result == '[FP]':
                    code = setting.CODE_FP
                elif result == '[TP]':
                    code = setting.CODE_TP
                elif result == '[COMPLETED]' or result == '[TN]':
                    code = setting.CODE_COMP
                else:
                    code = setting.CODE_NONE

                e_c = float(output[28])
                e_p = -float(output[34])        ## negation of physical cost (maximize)

                sum_c = float(output[29])
                e_c1 = float(output[30])
                e_c2 = float(output[31])
                e_c3 = float(output[32])

                ec_list = [None]*setting.M
                ep_list = [None]*setting.M_P
                for i in range(setting.M):
                    ec_list[i] = float(output[44+i])                #cyber cost (max)
                for i in range(setting.M_P):
                    ep_list[i] = float(output[23+i])                #physical cost (max)

                print "========= output_parser result begin ========="
                print "ep_list", ep_list
                print "ec_list", ec_list
                print "output_parser output:", code, ec_list, ep_list
                print "========= output_parser result end ========="
                return code, ec_list, ep_list
            line = fp.readline()

        return output 


def px4_process_output(sim_outfile, M):
    exists = os.path.isfile(sim_outfile)
    output = 0, [float('inf')],[float('inf')]  #sim error

    if not exists:
        cprint(" !!![Error] cpii_output (sim_outfile) does not exist. Check simulation", 'red')
        print "sim_outfile:", sim_outfile
        #f = open(sim_outfile, "w")
        #output_str = "[ERROR] No SIMULATION\n"
        #f.write(output_str)
        return output

    print "-----------------Process Outputs-------------------"
    print "FILE: " + sim_outfile
    with open(sim_outfile) as fp:
        line = fp.readline()
        while line:
            print line
            if 'ERR' in line:                     # error with codes
                cprint(line.strip(), 'red')
            if '[FN]' in line or '[FP]' in line or '[TP]' in line or '[TN]' in line:
                cprint(line.strip(), 'red')
                output = line.split()
                result = output[0]
                code = 0
                if result == '[FN]':
                    code = setting.CODE_FN
                elif result == '[FP]':
                    code = setting.CODE_FP
                elif result == '[TP]':
                    code = setting.CODE_TP
                elif result == '[TN]':
                    code = setting.CODE_COMP
                else:
                    code = setting.CODE_NONE        #err

                ec_list = [None]*setting.M
                ep_list = [None]*setting.M_P
                for i in range(settingM):
                    ec_list[i] = float(output[2+i])
                for i in range(M_P):
                    ep_list[i] = float(output[5+i])

                print "ep_list", ep_list
                print "ec_list", ec_list
                return code, ec_list, ep_list, [sum_c]
            line = fp.readline()
        return output 

def main():
    file="/home/apm/cpii/outputs/simout_20200109_015650_g0_s1.log"
    out_dir="/home/apm/cpii/outputs/"
    #for root, dirs, files in os.walk(out_dir): 
    files = [f for f in os.listdir(out_dir) if os.path.isfile(os.path.join(out_dir, f))]
    N = len(files);
    print N
    for filename in files:
        if filename.endswith('.log'):
            file=out_dir+filename
            output_vector = arducopter_process_output(file, 3, 1, 1)  #M M_P V
            print output_vector
            code = output_vector[0] #[XX]
            c_dev = output_vector[1]
            p_dev = output_vector[2]
            c_dev_sum = output_vector[3]
            print code
            print c_dev
            print p_dev
            print c_dev_sum

if __name__ == '__main__':
    main()

