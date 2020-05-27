import setting

#!/usr/bin/env python
import subprocess, shlex
import socket, sys, time, datetime, signal, os
from shutil import copyfile
from shutil import copy
import logger as log
import sdfmutator as sdf
import output_parser 
from os.path import expanduser
import psutil
from termcolor import colored, cprint
import random

GAZEBO = 'gzserver'


def kill_tasks():
    pname = ["gzserver", "ArduCopter.elf", "APMrover2.elf", "MAVProxy", "sim_vehicle", "mavproxy", "xterm", "gazebo", "px4", "px4_iris"]
    #pname = ["gzserver", "MAVProxy", "sim_vehicle", "mavproxy", "gazebo"]

    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if any(x in line for x in pname):
            pid = int(line.split(None, 1)[0])
            try:
                os.kill(pid, signal.SIGKILL)
                print "killing ", line
            except OSError:
                print "already killed ", pid, line

def runSim(id, cmd, TIMEOUT, MAINNAME, INIT_TIME, real):
    '''
    run simulation (dummy or real sim)
    '''

    if (real == True):      #real simulation
        startSim(id, cmd, TIMEOUT, MAINNAME, INIT_TIME)


    else:                   #dummy simulation
        log.cinfo("#%s Dummy Simulation running ..." % (id))

        sim_out_name = "simout_" + id + ".log"
        sim_out = expanduser("~") + "/cpii/outputs/" + sim_out_name        #arducopter *.log
        print "dummy sim out:", sim_out
        print "dummy sim log:", setting.sim_log_file
        outf = open(sim_out, "w")

        plist = []     
        clist = []
        for i in range(4): 
            rand_double = round(random.uniform(0, 10), 4)
            plist.append(rand_double)
        for i in range(8):
            rand_double = round(random.uniform(0, 10), 4)
            clist.append(rand_double)
    
        #plist = [21, 22, 23, 24]
        #clist = [11, 12, 13, 14, 15, 16, 17, 18]
        #dummy_output = "[FN] (fs) 0 0 1 (mode) AUTO (count) 10999 6239 (geo) -0.001761 15.324518 -0.624730 0.001679 0.000000 3.151427 (p-dev) 0.027364 0.118612 0.010910 0.064531                     (max_pdev) 0.155947 0.689804 0.072074 0.368104 (cyber) -100.000000 0.000000 1.093414 48.912453 -768.000000 (phy) 0.316004 0.000000 (cost) 0.000000 (sum_e) 2852.309814 58276.433594 -1390860.000000 0.0 (e) 0.316004 2.867680 59.530594 0.000000 0.000000 0.000000 0.000000 0.000000"

        dummy_output = "[FN] (fs) 0 0 1 (mode) AUTO (count) 2 2 (geo) 6 6 6 6 6 6 (p-dev) 4 4 4 4 (max_pdev) " 
        dummy_output += ' '.join(map(str, plist))
        dummy_output += " (cyber) 5 5 5 5 5 (phy) 2 2 (cost) 1 (sum_e) 3 3 3 4 (c_dev) "
        dummy_output += ' '.join(map(str, clist))
        print "dummy output\n", dummy_output
        outf.write(dummy_output)


def startSim(id, cmd, TIMEOUT, MAINNAME, INIT_TIME):
    #print "max time " + str(TIMEOUT)
    #sys.exit() 
    isNormal = True

    start_time = datetime.datetime.now()

    log.cinfo("#%s Simulation running ..." % (id))
    print "start: ", start_time

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #print "subprocess pid: ", p.pid                     #main process ('/bin/sh', cd /home...)
    #main_process = psutil.Process(p.pid)
    #children = main_process.children(recursive=True)    #child process ('python', ./sim_vheicle.py...)
    #for child in children:
    #    print 'child pid: ', child.pid

    while True: 
        now = datetime.datetime.now()
        print ' Waiting for Init .. ', (int)(INIT_TIME - (now-start_time).seconds), "\r",
        if (datetime.datetime.now() - start_time).seconds >= INIT_TIME:
            break;
        time.sleep(0.1)
    print "\nRunning..."

    #time.sleep(20)  # wait for initiating Gazebo, main...

    #for proc in psutil.process_iter():
    #    #print '\t\t', proc.pid, proc.name(), proc.cmdline()
    #    if proc.pid == p.pid:
    #        print ("main [%d %s %s]" % (proc.pid, proc.name(), proc.cmdline()))
    #    for child in children:
    #        if proc.pid == child.pid:
    #            print ("child [%d %s %s]" % (proc.pid, proc.name(), proc.cmdline()))


    PROCNAME = MAINNAME
    elf_pid = None
    gazebo_pid = None

    # check finish
    while p.poll() is None:

        time.sleep(1)

        # progress
        now = datetime.datetime.now()
        progress_sec = (now-start_time).seconds #elapsed second
        progress = int((progress_sec*100 / TIMEOUT))    # (sec)
        print ' [ ' + str(progress) + "%]", (int)(TIMEOUT - progress_sec), "sec to timeout\r",
        #print (' [%3d] Running... (%d sec to timeout)'  % (progress, (int)(TIMEOUT-progress_sec)))
        sys.stdout.flush()

		## check main alive
        # get pid for elf and gazebo
        if elf_pid == None or gazebo_pid == None:
            plist = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
            out, err = plist.communicate()
            #print out  #list all 
            for line in out.splitlines():
                elf_pid = None
                if MAINNAME in line:
                    #print "Main Program Info :", line
                    if not 'defunct' in line:
                        elf_pid = int(line.split(None, 1)[0])
                        break
            for line in out.splitlines():
                gazebo_pid = None 
                if GAZEBO in line:
                    #print "Gazebo Server Info:", line
                    gazebo_pid = int(line.split(None, 1)[0])
                    break
            if elf_pid != None and gazebo_pid != None:
                print "Main Program : ", MAINNAME, elf_pid
                print "Gazebo       : ", gazebo_pid
            
        #if psutil.pid_exists(elf_pid) == True:
            #main_process = psutil.Process(elf_pid)
            #stdout, stderr = main_process.communicate()
            #print 'STDOUT:{}'.format(stdout)
            #print 'STDERR:{}'.format(stderr)


        # check not exist => kill all        
        if psutil.pid_exists(elf_pid) != True: 
                # or psutil.Process(elf_pid).status() == psutil.STATUS_ZOMBIE:
            cprint("\n System Info: ", 'yellow')
            print " [", MAINNAME, elf_pid, "] terminated ... "
            time.sleep(3)
            kill_tasks()
            break
        #else:
        #    print "\n", elf_pid, MAINNAME, " alive"

        if psutil.pid_exists(gazebo_pid) != True:
            cprint("\n System Info: ", 'yellow')
            print " [", GAZEBO, gazebo_pid, "] dead, abnormally terminating ... "
            time.sleep(3)
            kill_tasks()
            break
        

        #check timeout
        if (now - start_time).seconds >= TIMEOUT:
            print "\nTIMEOUT kill process ", p.pid
            os.kill(p.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            kill_tasks()
            isNormal = False
    #while end

    end_time = datetime.datetime.now()
    print "end: ", end_time
    print "elaped: ", end_time - start_time
    kill_tasks()
    log.info("\n  --- Simulation %s completed ---\n" % (id,))


def main():
    AUTOHOME = expanduser("~") + "/ardupilot/Tools/autotest"
    log_id = '000000_000001'
    COMMAND = "cd " + AUTOHOME + "; ./sim_vehicle.py -v ArduCopter -f gazebo-iris -m --mav10 --map --console -I1 -D -K " + log_id
    TIMEOUT = 120
    mainname = 'arducopter'
    startSim(log_id, COMMAND, TIMEOUT, mainname)

if __name__ == '__main__':
    main()
