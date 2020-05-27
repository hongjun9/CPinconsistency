#!/usr/bin/env python
import xml.etree.ElementTree as ET
import subprocess, shlex
import socket, sys, time, datetime, signal, os
from shutil import copyfile
from shutil import copy
import logger as log
import sdfmutator as sdf
import output_parser 
import simulator
from os.path import expanduser
import psutil
from termcolor import colored, cprint
import random
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt 
import math
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


#Input Ranges
XLIM = [-1,1]
YLIM = [-1,2]
ZLIM = [-1,1]
PLIM = [-4,4]


USER_HOME = expanduser("~")
world_file = USER_HOME + '/ardupilot_gazebo/worlds/copter.world'
AUTOHOME = USER_HOME + "/ardupilot/Tools/autotest"   
CPII_HOME = USER_HOME + "/cpii"
GZ_HOME = USER_HOME + '/ardupilot_gazebo'
world_file = GZ_HOME + '/worlds/copter.world'
model_file = GZ_HOME + '/models/fs_gray_wall/model.sdf'    #model file
param_file = CPII_HOME + '/param.txt'
OUTPUT_HOME = CPII_HOME + '/outputs/'
LOG_HOME = CPII_HOME + '/testlog/'


#if(FIGON):
#    plt.ion()
#    fig = plt.figure()
#    ax = fig.add_subplot(1, 1, 1, axisbg="1.0")
#    #ax = fig.add_subplot(1, 1, 1, projection='3d')


def plot_scatter(individuals, title):

    x = [row[1][0] for row in individuals]  #2d outputs
    y = [row[1][1] for row in individuals]
    #z = [row[1][2] for row in parent_individuals]
    ax.clear()
    ax.scatter(x,y)
    ax.set_xlim(XLIM[0], XLIM[1])
    ax.set_ylim(YLIM[0], YLIM[1])
    #ax.set_zlim(0,1)
    plt.title(title)
    fig.canvas.draw_idle()
    plt.show()
    plt.pause(0.3)
    #plt.waitforbuttonpress()





def plot_result(test_id, GEN, total_individuals, M):

    # plot individuals
    plt.ion()
    fig = plt.figure()
    if M == 2:
        ax = fig.add_subplot(1, 1, 1, axisbg="1.0")
    if M >= 3:
        ax = fig.add_subplot(1, 1, 1, projection='3d')

    for i in range(GEN):
        individuals = total_individuals[i]
        title = "Generation " + str(i+1)
        ax.clear()

        x = [row[INDEX_OUTPUT][0] for row in individuals]
        y = [row[INDEX_OUTPUT][1] for row in individuals]
        ax.set_xlim(XLIM[0], XLIM[1])
        ax.set_ylim(YLIM[0], YLIM[1])

        if(M == 2):
            s = ax.scatter(x,y)
        if(M == 3):
            ax.set_zlim(ZLIM[0], ZLIM[1])
            z = [row[INDEX_OUTPUT][2] for row in individuals]
            s = ax.scatter(x,y,z)
        if(M == 4):
            z = [row[INDEX_OUTPUT][2] for row in individuals]
            p = [-row[INDEX_OUTPUT][3] for row in individuals]
            s = ax.scatter(x,y,z, c=p, cmap=plt.cm.coolwarm)
            s.set_clim(PLIM[0], PLIM[1])
            if i == 0:
                plt.colorbar(s)
        if(M > 4):
            print "unsupported dimenssion!"
            exit()

        #fig.canvas.draw_idle()
        plt.title(title)
        plt.show()
        plt.pause(0.9)

    plt.savefig(CPII_HOME + "/testlog/plots/"+test_id)  #save final gen
    plt.waitforbuttonpress()


def main(argv):

    GEN = 0
    M = 0
    V = 0 

    path = LOG_HOME
    for file in os.listdir(path):
        log_file = None
        if file.endswith(".log"):
            log_file = os.path.join(path, file)
            print log_file

            #----------------------------------------------
            total_individuals = []        # total
            with open(log_file) as f:
                line = f.readline()
                while line:
                    if 'INDIVIDUALS' in line:   # found one generation
                        individuals = []
                        GEN += 1
                        N = int(line.split(' ')[1])
                        V = int(line.split(' ')[2])
                        M = int(line.split(' ')[3])
                        for i in range(N):
                            row = f.readline().split(',')
                            #print "row:", row
                            inputs = []
                            outputs = []
                            code = int(row[INDEX_CODE])
                            for i in range(V):
                                inputs.append(float(row[INDEX_INPUT+i]))
                            for j in range(M):
                                outputs.append(float(row[INDEX_INPUT+V+j]))
                            indiv = [code, inputs, outputs, int(row[INDEX_INPUT+M+V]), int(row[INDEX_INPUT+M+V+1])]
                            individuals.append(indiv)
                        total_individuals.append(individuals)
                    line = f.readline()

                print "GEN/V/M:", GEN, V, M
            #print "end:", log_file

            for i in range(GEN):
                print "Generation " +  str(i+1)
                for j in range(N):
                    print total_individuals[i][j]

    ## Option
    ## plot individuals
    #plt.ion()
    #fig = plt.figure()
    #if M == 2:
    #    ax = fig.add_subplot(1, 1, 1, axisbg="1.0")
    #if M >= 3:
    #    ax = fig.add_subplot(1, 1, 1, projection='3d')

    #for i in range(GEN):
    #    individuals = total_individuals[i]
    #    title = "Generation " + str(i+1)
    #    ax.clear()

    #    x = [row[INDEX_OUTPUT][0] for row in individuals]  
    #    y = [row[INDEX_OUTPUT][1] for row in individuals]
    #    ax.set_xlim(XLIM[0], XLIM[1])
    #    ax.set_ylim(YLIM[0], YLIM[1])

    #    if(M == 2):
    #        s = ax.scatter(x,y)
    #    if(M == 3):
    #        ax.set_zlim(ZLIM[0], ZLIM[1])
    #        z = [row[INDEX_OUTPUT][2] for row in individuals]
    #        s = ax.scatter(x,y,z)
    #    if(M == 4):
    #        p = [row[INDEX_OUTPUT][2] for row in individuals]
    #        s = ax.scatter(x,y,z, c=p, cmap=plt.cm.coolwarm)
    #        s.set_clim(-1,1) 
    #        if i == 0:
    #            plt.colorbar(s)
    #    if(M > 4):
    #        print "unsupported dimenssion!"
    #        exit()

    #    #fig.canvas.draw_idle()
    #    plt.title(title)
    #    plt.show()
    #    plt.pause(0.9)
    #
    #plt.waitforbuttonpress()


if __name__ == '__main__':
    main(sys.argv)
