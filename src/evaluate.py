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
        setting.SIM_COUNT += 1  # just for log
        
        ###====================================================
        # output parser: system-specific post processing
        output_vector = output_parser.process_output(setting.MAINNAME, simlog_id)

        # process output and safe testlog
        #code, output_list = output_evaluate(input_vector, output_vector)
        ##====================================================
        # Check output and log
        # if output is the CPinc-case, save the output

        if output_vector == None or output_vector[0] == setting.CODE_NONE:
            log.error("[CPI_OUTPUT] SIM_ERR NO_CPi_found")
            dummy_output = [float('inf')]*(setting.M+setting.M_P)
            code = setting.CODE_NONE
            output_list = dummy_output 

        else:
            code = output_vector[0]     #[XX]
            c_dev = output_vector[1]    #[c1, c2, ...]
            p_dev = output_vector[2]    #[p]
            #c_dev_sum = output_vector[3]
        
            # output to testlog
            print("=========================================================")
            log.info("[INPUT _VECTOR] " + str(input_vector))
            log.info("[OUTPUT_VECTOR] " + str(output_vector))

            # cpii log
            output = "[CPI_OUTPUT]" + ' ' + str(code) + '\n(input) ' + str(input_vector) + '\n(c_dev) ' + str(c_dev) + ' (p_dev) ' + str(p_dev)
            log.cimportant(output)

            # 
            # if cpi found, then copy (log_file, sim_outfile) the case to result/
            #
            result_dir = setting.CPII_RESULT + '/'
            if code == setting.CODE_FP or code == setting.CODE_FN:
                cprint("!! CPInconsistency case found !!", 'red')
                setting.CPI_COUNT = setting.CPI_COUNT + 1

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
                print "cpi fonud:", result_dir + case_output_name
                case_output = open(result_dir + case_output_name, 'w+', 0)
                case_output.write("[MISSION]\n" + mission + '\n')
                case_output.write("[INPUTS]\n" + str(input_vector) + '\n')
                case_output.write("[OUTPUT]\n" + str(output_vector) + '\n')
                
            cost_list = c_dev + p_dev

        ##for test
        #if NO_SIM_TEST:
        #    cost_list = []
        #    for j in range(M):
        #        cost_list.append(round(random.uniform(0, 1), 4))
        #    print cost_list

        #======================================
        #[code, [inputs], [outputs]]
        individuals[i][INDEX_CODE] = code 
        individuals[i].append(cost_list)

        cprint("Evaluation " + str(i+1) + "/" + str(N) + " done -- individual: " + str(individuals[i]), 'yellow')

        #end one loop (sim)

    return individuals


