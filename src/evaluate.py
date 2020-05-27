import setting
import logger as log
from setting import *
import sdfmutator as sdf
import simulator
import os
from shutil import copyfile
import output_parser
from termcolor import colored, cprint

def evaluate(eval_id, individuals):
    #return individuals having outputs
    #leave simulation log to file sim_*.log

    ## evaluation (N population) : run simulations
    N = len(individuals);
    cprint("===============================================================================", 'red')
    cprint("=============================== Evaluate POP: " + str(N) + " ==============================", 'red')
    cprint("===============================================================================", 'red')
    for i in range(len(individuals)):
        print individuals[i]

    for i in range(N):
        simlog_id = eval_id + "_s" + str(i+1)
        log.cimportant("###### [#%s / %d] Evaluation (SIM) starts ###### " % (simlog_id, N))

        output_list = None 
        vlist = individuals[i][INDEX_INPUT][0:setting.V]    #input list

        ###====================================================
        # generate input files for simulation
        # output: intput files and input_vector (xml texts)
        index = 0
        print "input list:", vlist
        # make Vlist from Vmap, Vrange
        for j in reversed(range(setting.MAX_INPUT)):
            if(setting.Vmap & 1<<j):
                input_num = len(setting.Vrange[j])/2
                setting.Vlist[j] = vlist[index:index + input_num]
                index = index + input_num
        print "Vmap", "{0:040b}".format(setting.Vmap)
        print "Vrange", setting.Vrange
        print "Vlist",setting.Vlist

        input_params = sdf.mutate_param(simlog_id, setting.param_file, setting.MISSION_TIME, setting.V, setting.M, setting.M_P)
        input_models = sdf.mutate_model(setting.model_file, setting.Vlist, setting.V, setting.Vmap)
        input_world = sdf.mutate_world(setting.world_file, setting.Vlist, setting.V, setting.Vmap)
        input_vector = [input_params, input_models, input_world]    #input_vector: param/model/world for gazebo
        print "debug: [input_vector]" 
        for j in range(len(input_vector)):
            print str(input_vector[j])
        ## input_vector generated

        simulator.kill_tasks()

        # Execution: run program
        cmd = setting.COMMAND + " -K " + simlog_id  #to save simulation log to "/tmp/<simlog_id>.simlog"
        simulator.runSim(simlog_id, cmd, setting.TIMEOUT, setting.MAINNAME, setting.WAIT_TIME, setting.SIM_MODE_REAL)

        
        ###====================================================
        # System-specific post processing

        # Arducopter
        if(setting.MAINNAME == 'arducopter'):



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

        ## single simulation and output_vector generated
        ##--------------------------------------------------

        setting.SIM_COUNT += 1  # just for log

        # process output and safe testlog
        #code, output_list = output_evaluate(input_vector, output_vector)
        ##====================================================
        # Check output and log
        # if output is the CPinc-case, save the output

        if output_vector[0] == setting.CODE_NONE:
            log.error("[CPI_OUTPUT] SIM_ERR NO_CPi_found")
            dummy_output = [float('inf')]*(M+M_P)
            code = setting.CODE_NONE
            output_list = dummy_output 
        else:
            code = output_vector[0]     #[XX]
            c_dev = output_vector[1]    #[c1, c2, ...]
            p_dev = output_vector[2]    #[p]
            #c_dev_sum = output_vector[3]
        
            # output to testlog
            print("=========================================================")
            log.info("[INPUT_VECTOR] " + str(input_vector))
            log.info("[OUTPUT_VECTOR] " + str(output_vector))
        
            # cpii log
            # + ' (c_dev_sum) ' + str(c_dev_sum)
            output = "[CPI_OUTPUT]" + ' ' + str(code) + '\n(input) ' + str(input_vector) + '\n(c_dev) ' + str(c_dev) + ' (p_dev) ' + str(p_dev)
            log.cimportant(output)
        
            # if cpi found, then copy (log_file, sim_outfile) the case to result/
            result_dir = setting.CPII_HOME + '/result/'
            if code == setting.CODE_FP or code == setting.CODE_FN:
                cprint("!! CPInconsistency case found !!", 'red')
                #print "copying", setting.log_file, " >> ", result_dir + setting.test_log_name
                #copyfile(setting.log_file, result_dir + setting.test_log_name)      #cpii_input
                #print "copying", sim_outfile, " >> ",  result_dir + sim_outfile_name
                #copyfile(sim_outfile, result_dir + sim_outfile_name)   #sim_output
                
                # save finding case with input, output and mission
                #print "mission:", result_dir + "mission_" + simlog_id + ".txt"
                #copyfile(setting.mission_file, result_dir + "mission_" + simlog_id + ".txt")
                mission_f = open(setting.mission_file, 'r')
                mission = mission_f.read()
                case_output_name  = "cpi_" + simlog_id + ".txt"
                print "cpi output:", result_dir + case_output_name
                case_output = open(result_dir + case_output_name, 'w+', 0)
                case_output.write("[MISSION]\n" + mission + '\n')
                case_output.write("[INPUTS]\n" + str(input_vector) + '\n')
                case_output.write("[OUTPUT]\n" + str(output_vector) + '\n')
                
                
                exit()
        
            output_list = c_dev + p_dev

        ##for test
        #if NO_SIM_TEST:
        #    output_list = []
        #    for j in range(M):
        #        output_list.append(round(random.uniform(0, 1), 4))
        #    print output_list

        #======================================
        #[code, [inputs], [outputs]]
        individuals[i][INDEX_CODE] = code 
        individuals[i].append(output_list)
        cprint("Evaluation " + str(i+1) + "/" + str(N) + " done -- code [costs]: " + str(code) + " " + str(output_list), 'yellow')

        #end one loop (sim)

    return individuals

#def output_evaluate(input_vector, output_vector):
#
#    ##====================================================
#    # Check output and log
#    # if output is the CPInc-case, save the output
#    # input_vector, output_vector
#    if output_vector[0] == CODE_NONE:
#        log.error("[CPI_OUTPUT] SIM_ERR NO_CPi_found")
#        dummy_output = [float('inf')]*M
#        return CODE_NONE, dummy_output 
#    else:
#        code = output_vector[0] #[XX]
#        c_dev = output_vector[1]
#        p_dev = output_vector[2]
#        c_dev_sum = output_vector[3]
#    
#        # output to testlog
#        log.info("[INPUT_VECTOR] " + str(input_vector))
#        log.info("[OUTPUT_VECTOR] " + str(output_vector))
#    
#        # cpii log
#        output = "[CPI_OUTPUT]" + ' ' + str(code) + ' (input) ' + str(input_vector) + ' (c_dev) ' + str(c_dev) + ' (p_dev) ' + str(p_dev) + ' (c_dev_sum) ' + str(c_dev_sum)
#    
#        log.cimportant(output)
#    
#        # if found, then copy the case
#        result_dir = CPII_HOME + '/result/'
#        if code == CODE_FN or code == CODE_FN:
#            cprint("!! CPInconsistency case found !!", 'red')
#            print "copying", log_file, "to ", result_dir + test_log_name
#            copyfile(log_file, result_dir + test_log_name)      #cpii_input
#            print "copying", sim_outfile, "to ",  result_dir + sim_outfile_name
#            copyfile(sim_outfile, result_dir + sim_outfile_name)   #sim_output
#
#        output = c_dev + p_dev
#        return code, output


