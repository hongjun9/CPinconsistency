# Cyber-Physical Inconsistency Identification

**Cyber-Physical Inconsistency Identifier (CPII)** searches cyber and physical inconsistency vulnerabilities in the control program of robotic vehicles. The details of technical aspects of our approach can be referred to our paper "Cyber-Physical Inconsistency Vulnerability Identification for Safety Checks in Robotic Vehicles (CCS 2020)"

<!--## Citation
``` 
@inproceedings{choi2020detecting,
  title={Detecting attacks against robotic vehicles: A control invariant approach},
  author={Choi, Hongjun and Lee, Wen-Chuan and Aafer, Yousra and Fei, Fan and Tu, Zhan and Zhang, Xiangyu and Xu, Dongyan and Deng, Xinyan},
  booktitle={Proceedings of the 2018 ACM SIGSAC Conference on Computer and Communications Security},
  pages={801--816},
  year={2018}
}
```-->

##Introduction

**Cyber-Physical Inconsistency** is a new type of vulnerability for robotic vehicles (RVs). These vulnerabilities are induced by the inherent incompleteness of general-purpose, high-level programming languages in describing complex physics. This safety related and can be exploited by solely manipulating environmental conditions, which leads to physical damages and life-threatening. 

We provide a testing based tool to identify the CP-inconsistency vulnerabilities systematically. The technique requires the interplay of program analysis, vehicle modeling, and search-based testing. 

This provides a prototype of our tool to play with a sample robotic system (Arducopter), including a simulated vehicle, gazebo models, and control-guided evolutionary search. 

##Setup

###Software Requirements
1. Matlab R2017B or above
2. VMware Workstation 12.0 or above
3. VMiamge (apm_gazebo) includes:
    - Ubuntu 16.04.3 LTS
    - ArduCopter V3.7
    - Customized Mavproxy 1.5.2
    - Gazebo 8.6.0
    - Gazebo models (e.g., obstacles)
    - Gazebo plugins (e.g., wind generator)
    - Mission Generator
    - CPII 1.0 (test engine)

###Installation

The provided VM image (id: apm / password: apm) includes all the programs and related packages to test CPII tool, expect the Matlab tools. For the system modeling, Matlab is essential and should be installed in your host machine. 

In this setup, we assume that the user knows how to make the system model with System Identification (SI) technique. In this tutorial, we do not provide the details. Please read our previous paper "Detecting attacks against robotic vehicles: A control invariant approach (CCS'18)" and the previous tutorial at: https://github.com/hongjun9/CPS_Invariant

##Evolutionary Searching

CPII Evolutionary search requires 1) cyber costs, 2) physical costs, 3) search engine. 

### Cyber cost

The cyber cost function is constructed from the control program via static analysis. It essentially represents the degree of the cyber anomaly (see Section 4.2). The profiling code will be inserted into the control program to collect cyber costs while the simulation is running. 
    
    Example inserted code:     ~/ardupilot/ArduCopter/crash_check.cpp
    
    e_c1 = CRASH_CHECK_ACCEL_MAX - land_accel_ef_filter.get().length();
    e_c2 = attitude_control->get_att_error_angle_deg() - CRASH_CHECK_ANGLE_DEVIATION_DEG;
    e_c3 = crash_counter - CRASH_CHECK_TRIGGER_SEC * scheduler.get_loop_rate_hz() ;

The collecting codes run in the main control at a certain frequency (400hz). We piggy-back the profile data collection on the existing logging components. Thus, the log system should be customized to store our additional variables. We modified the DataFlash log module of Arducopter. To modify the log module, please refer the code at:
    
    ~/arducopter/Arucopter/Log.cpp (already modified)

(See more details at https://ardupilot.org/copter/docs/common-logs.html)
    

### Physical cost

The physical cost function represents the degree of the physical anomaly. Our system model predicts the expected physical states as a kind of observer. The physical cost function calculates how much current physical states are deviated from the expected states. The predictive model based on SI technique can be extracted like the control invariant (see our CCS'18 paper). The observer can be either a non-linear model (e.g. EKF) or , linear state-space model. 

The physical costs are also collected at runtime. The collecting codes are inserted into the main control loop like the same way of the cyber costs.

### CPII Search Engine

CPII search engine perturbs the environmental conditions and runs the simulation multiple times. To do that, it requires Gazebo, Gazebo plugins, Gazebo models for simulation. Also, it requires the execution engine to run Arducopter under the Gazebo simulation environment, which repeatedly launches the simulation. 


#### Gazebo

Gazebo is a popular 3D simulator. It runs a physical dynamic engine with gazebo world, model, and plugins to simulate realistic physical behaviors. The directories that include objects (obstacles and the simulated vehicle) SDF files are located at 

    ~/ardupilot_gazebo/models/
    
The world describes some environmental effects (e.g., weather). 

    ~/ardupilot_gazebo/worlds/copter.world

The plugins (e.g., wind plugin) to generate more complex environmental effects are located at 

    ~/ardupilot_gazebo/include/ 
 
#### Execution Engine

##### Mission and Ground Control System (GCS)

Missions and a GCS actually make the vehicle perform the given missions. Our mission generator (mission.py) generates the random missions by following the standard UAV mission format, MAVLink mission protocol (https://mavlink.io/en/services/mission.html). The generated mission "mission.txt" should be located at 

    ~/ardupilot/Tools/autotest/cpii/
    
    
For the automatic test, we modified the popular Python-based ground control system to launch the mission (from auto arming to mission launching). 

    ~/.local/bin/mavproxy.py

Our codes are inserted into the function **input_loop()** to check the simulation status and control program execution, and then automatically launch the mission script that includes mission commands. 

##### Execution driver

For the different control programs, different execution drivers would be required. The execution driver (simulator.py) includes all the scripts to manage (i.e., start, timeout, kill) processes for the simulation. 

* system-specific settings

	* setting.py: system-specific definitions (paths, files, etc)
	* evaluate.py: simulation execution
	* output_parser.py: a parser for simulation output (log)


#### Genetic Algorithm

Our evolutionary search (evolutionary.py) utilizes the popular non-domination-based genetic algorithm for Pareto optimality with our control-guided fitness function. The searching goal is to maximize the different cyber costs and physical costs. 

##### Data structure

The *individual* consists of the vulnerability code, input, output, and ranking. 

	[vtype, [input], [output], plevel, alevel]
	
	vtype: over/under-approximaiton, normal, etc.
	input: simulation inputs (parameters, models, world)
	output: simulation output (result_code, cyber costs, physical costs)
	plevel: pareto optimality level (fronts)
	alevel: physical anomlay level
	
##### Parameters

	G: the number of generation
	N: the number of population
	V: the number of inputs
	M: the number of cyber costs
	MP: the number of physical costs
	
	pool: size of maiting pool (N/2)
	tour: tournament size (default 2) (selection pressure)
	mu, mum: distribution index for crossover and mutation (default 20, 20)
	pr: proportion of crossover to mutaiton (default 0.9)


##How to run
	
	# run the main evolutionary search engine with a default setting.
	~/cpii/src/main.py 
	
For optional arguments

	~/cpii/src/main.py --help
	
###Outputs

During the evolutionary searching, CPII logs internal information, simulaiton logs and save the finding results seperately. The directory includes the outputs as follows.

* output: simulation outputs (*.log) / dataflash logs (*.BIN)
* testlog: logs during cpii execution
	* mission_<time>.txt: mission file
	* test_<time>.log: cpii logs
	* getout_<time>.log: list of individuals during searching
* result (finding cases) 
	* cpi\_\<datatime>\_<gen#>\_<indiv#>.txt: includes the mission, input, and output

Here is an exmpale output.

	# cpi_20200520_101319_g0_s1.txt
	
	[MISSION]
	QGC WPL 110
	0   0   0   16  0   0   0   0   -35.363262  149.165237  584.080017  1
	1   1   3   22  0   0   0   0   -35.363262  149.165237  43.776874061    1
	2   0   3   19  0   0   0   0   -35.3632937714  149.16509235    30.4509888547   1
	3   0   3   19  0   0   0   0   -35.3633406749  149.165222958   33.3352815782   1
	4   0   3   19  0   0   0   0   -35.3633492649  149.165390483   34.734759867    1
	5   0   3   19  0   0   0   0   -35.3630688858  149.16542313    46.0866380176   1
	6   0   3   21  0   0   0   0   -35.3630688858  149.16542313    0   1
	
	[INPUTS]
	[['log_id', '20200520_101319_g0_s1', 'tunnel', '0 0 0 0', 'timeout', 0, 'battcap', 0, 'nums', 3, 3, 10], ['static', 'false', 'mass', '36.0', 'ixx', '28.0', 'iyy', '10.0', 'izz', '15.0', 'size', '3 3 10'], ['windGustDirection', '164.0 6.0 81.0', 'windGustDuration', '6.0', 'windGustDuration', '6.0', 'magnetic_field', '6e-06 2.3e-05 -4.2e-05', 'temperature', '298.15', 'pressure', '101325.29', 'temperature_gradient', '-0.0066']]
	[OUTPUT]
	(5, [9.6103, 1.8497, 1.239], [3.7014, 9.8052, 0.3639])
	
For each vulnerability case that the tool find, the output log (cpi_<id>.txt) is generated under the *result* directory. 

The cpi log provides the mission and inputs that trigger the finding vulnerability. Also it containts simulation outputs (cyber and physical costs).


### Disclaimer
The VM has only been tested with our exmaple system. If you want to use the tool for the different system. Specific configuraiton should be customized properly. Any bug reports and feedbacks would be welcome. 


### Further reading

* More technical information can be found in our paper: "Cyber-Physical Inconsistency Vulnerability Identification for Safety Checks in Robotic Vehicles"
* Control invariant framework: https://github.com/hongjun9/CPS_Invariant
* Gazebo Robot Simulator: http://gazebosim.org/
* MAVProxy: https://ardupilot.github.io/MAVProxy/html/development/index.html
* MAVLink Developer Guide: https://mavlink.io/en/
* Ardupilot Development Site: https://ardupilot.org/dev/index.html


