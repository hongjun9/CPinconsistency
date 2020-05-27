#!/usr/bin/env python
from xml.etree import ElementTree as et
from xml.dom import minidom
from shutil import copyfile
from collections import namedtuple
from os.path import expanduser
import logger as log
import random
import setting 

geo_bound = []  # [xmin, xmax, ymin, ymax, zmin, zmax] position bounds from the trajectory in the seed simulation
tunnel = []
#ALPHA = 1

#def config(bound, alpha):
#    global geo_bound, ALPHA
#    geo_bound = bound
#    #ALPHA = alpha

def mutate_3f(text, bound, N):  
    pivot = text.split() # not used yet
    x = round(random.uniform(bound[0], bound[1]), N)
    y = round(random.uniform(bound[2], bound[3]), N)
    z = round(random.uniform(bound[4], bound[5]), N)
    xyz = [x,y,z]
    fuzzed_3f = ' '.join([str(e) for e in xyz])
    return fuzzed_3f

def mutate_f(value, bound, N):
    return str(round(random.uniform(bound[0], bound[1]), N))

def gradient_descent_f(value, g, alpha):
    result = float(value) - g*alpha
    print("*gradient_decent_f " + str(result) + "=" + str(float(value)) + "-(" + str(alpha) + "*" + str(g)) + ")"
    return str(result)

def mutate_pose(text, bound, N):
    pose = text.split()
    n = pose[0]
    e = pose[1]
    u = pose[2]
    r = pose[3]
    p = pose[4]
    y = pose[5]

    #muate n e  y 
    n = mutate_f(n, bound[0:2], N)
    e = mutate_f(e, bound[2:4], N)
    u = mutate_f(u, bound[4:6], N)
    r = mutate_f(r, bound[6:8], N)
    p = mutate_f(p, bound[8:10], N)
    y = mutate_f(y, bound[10:12], N)

    posatt = [n, e, u, r, p, y]
    fuzzed_pose = ' '.join([str(e) for e in posatt])
    return fuzzed_pose


def mutate_param(log_id, filename, timeout, V, M, M_P):
    # log_id: data_time  for logfile_name
    # tunnel size: x y l w
    # timeout (loop count)
    # batt_capacity (mAh)    0: disable

    global tunnel
    log.cinfo("=== Reading Param file: " + filename)
    input_param = []

    # tunnel bound
    x = 30
    y = -10
    l = 30
    w = 20

    # batt cap (mAh)
    batt_cap = 0    #0: use default 

    f = open(filename, "w")
    output = [x, y, l, w]
    output = [0, 0, 0, 0]   #to disable
    tunnel_int = [(output[0]+output[2])/2, 0, 0, 0]
    tunnel = ' '.join(str(e) for e in tunnel_int)   #to string

    output_str = log_id + "\n"
    input_param = input_param + ['log_id', log_id]

    output_str += tunnel + "\n"
    input_param = input_param + ['tunnel', tunnel]

    output_str += str(timeout) + "\n"
    input_param = input_param + ['timeout', timeout]

    output_str += str(batt_cap) + "\n"
    input_param = input_param + ['battcap', batt_cap]

    output_str += str(V) + " " + str(M) + " " + str(M_P)    # #input #c_output #p_output
    input_param = input_param + ['nums', M, M_P, V]

    f.write(output_str)
    log.info(output_str)
    log.cinfo(">> Saved: Fuzz (Param): %s" % (filename))
    #log.write(output_str)
    return input_param 

def mutate_world(filename, Vlist, V, Vmap):
    """
    perturb world properties save the new world file
    filename: world sdf file path
    Vlist: input list
    Vmap: input bitmask
    """

    global tunnel
    log.cinfo("=== Reading world file: " + filename)
    tree = et.parse(filename)
    root = tree.getroot()
    xmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent=" ", newl='')
    
    input_world = []

    #world
    for world in root.findall("world"):     #for model in root.iter('model'):
        log.info(" world: %s" % (world.attrib))
        
        #physics
        physics = world.find('physics')
        if(physics != None):
            log.info("  physics: %s" % (physics.attrib))

        #light
        light = world.find('light')
        if(light != None):
            log.info("  light: %s" % (light.attrib))


        random_model = random.randint(0,4)      # randomly select model
        random_model = 5    #0: none, #1: tunnel, 2: box, 3: cylinder 4: sphere 5:gray_wall 

        #models
        for model in world.findall('model'):
            if(model != None):
                log.info("  model: %s" % (model.attrib))
                
                #name
                if(model.get('name') == 'fs_tunnel'):
                    if(random_model != 1):
                        world.remove(model)
                        continue
                    log.info("    fs_tunnel")

                    #pose
                    pose = model.find('pose')
                    log.info("      pose: " + pose.text)
                    #fuzzed_pose = tunnel
                    #pose.text = fuzzed_pose
                    #log.info("      *pose: " + pose.text)
                    input_world = input_world + ['tunnel_pose', pose.text]

                #name
                if(model.get('name') == 'fs_box'):
                    if(random_model != 2):
                        world.remove(model)
                        continue
                    log.info("    fs_box")

                    #pos
                    pose = model.find('pose')
                    log.info("      pose: " + pose.text)
                    #fuzzed_pose = mutate_pose(pose.text, [20, 20, 0, 0, 0, 0, 0, 0, 0, 0, -3.14, 3.14], 2)
                    #pose.text = fuzzed_pose
                    #log.info("      *pose: " + pose.text)
                    input_world = input_world + ['box_pose', pose.text]

                #name
                if(model.get('name') == 'fs_cylinder'):
                    if(random_model != 3):
                        world.remove(model)
                        continue
                    log.info("    fs_cylinder")
                    pose = model.find('pose')
                    log.info("      pose: " + pose.text)
                    #fuzzed_xyz =  mutate_3f(linear_velocity.text, [0,1,0,1,0,1], 2)
                    #fuzzed_pose = mutate_pose(pose.text, [20, 20, 0, 0, 0, 0, 0, 0, 0, 0, -3.14, 3.14], 2)
                    #pose.text = fuzzed_pose
                    #log.info("      *pose: " + pose.text)
                    input_world = input_world + ['cylinder_pose', pose.text]

                #name
                if(model.get('name') == 'fs_sphere'):
                    if(random_model != 4):
                        world.remove(model)
                        continue
                    log.info("    fs_sphere")

                    #pose
                    pose = model.find('pose')
                    log.info("      pose: " + pose.text)
                    #fuzzed_xyz =  mutate_3f(linear_velocity.text, [0,1,0,1,0,1], 2)
                    #fuzzed_pose = mutate_pose(pose.text, [20, 20, 0, 0, 0, 0, 0, 0, 0, 0, -3.14, 3.14], 2)
                    #pose.text = fuzzed_pose
                    #log.info("      *pose: " + pose.text)
                    input_world = input_world + ['sphere_pose', pose.text]                    

                #name
                if(model.get('name') == 'fs_gray_wall'):
                    if(random_model != 5):
                        world.remove(model)
                        continue
                    log.info("    fs_gray_wall")

                    #pose
                    pose = model.find('pose')
                    log.info("      pose: " + pose.text)
                    #fuzzed_pose = mutate_pose(pose.text, [20, 20, 0, 0, 0, 0, 0, 0, 0, 0, -3.14, 3.14], 2)
                    #pose.text = fuzzed_pose
                    #log.info("      *pose: " + pose.text)
                    input_world = input_world + ['gray_wall_pose', pose.text]

        #plugin
        for plugin in world.findall('plugin'):
            log.info("  plugin: %s" % (plugin.attrib))

            #name
            if(plugin.get('name') == "wind"):   #arducopter
                log.info("    wind") 

                #windDirection
                windDirection = plugin.find('windDirection')
                log.info("      windDirection: " + windDirection.text)
                
                #windForceMean
                windForceMean = plugin.find('windForceMean')
                log.info("      windForceMean: " + windForceMean.text)


                #windGustDirection
                windGustDirection = plugin.find('windGustDirection')
                log.info("      windGustDirection: " + windGustDirection.text)
                if(Vmap & 1<<setting.WORLD_WINDGUST_DIRECTION):
                    windGustDirection.text = str(Vlist[setting.WORLD_WINDGUST_DIRECTION][0]) + ' ' + str(Vlist[setting.WORLD_WINDGUST_DIRECTION][1]) + ' ' + str(Vlist[setting.WORLD_WINDGUST_DIRECTION][2])
                    log.info("      *windGustDirection: " + windGustDirection.text)
                    input_world = input_world + ['windGustDirection', windGustDirection.text]

                #windGustDuration
                windGustDuration = plugin.find('windGustDuration')
                log.info("      windGustDuration: " + windGustDuration.text)
                if(Vmap & 1<<setting.WORLD_WINDGUST_DIRECTION):
                    windGustDuration.text = str(Vlist[setting.WORLD_WINDGUST_DURATION][0])
                    log.info("      *windGustDuration: " + windGustDuration.text)
                    input_world = input_world + ['windGustDuration', windGustDuration.text]
 

                #windGustStart
                windGustStart = plugin.find('windGustStart')
                log.info("      windGustStart: " + windGustStart.text)
                if(Vmap & 1<<setting.WORLD_WINDGUST_DIRECTION):
                    windGustDuration.text = str(Vlist[setting.WORLD_WINDGUST_START][0])
                    log.info("      *windGustDuration: " + windGustDuration.text)
                    input_world = input_world + ['windGustDuration', windGustDuration.text]


                #iwndGustForceMean
                windGustForceMean = plugin.find('windGustForceMean')
                log.info("      windGustForceMean: " + windGustForceMean.text)
                if(Vmap & 1<<setting.WORLD_WINDGUST_FORCEMEAN):
                    windGustForceMean.text = str(Vlist[setting.WORLD_WINDGUST_FORCEMEAN][0])
                    log.info("     windGustForceMean: " + windGustForceMean.text)
                    input_world = input_world + ['windGustForceMean', windGustForceMean.text] 


                #xyz_offset
                xyz_offset = plugin.find('xyz_offset')
                log.info("      xyz_offset: " + xyz_offset.text)


            #wind_plugin
            if(plugin.get('name') == "wind_plugin"):    #px4 wind plugin
                log.info("    wind") 

                #windDirection
                windDirection = plugin.find('windDirection')
                log.info("      windDirection: " + windDirection.text)

                #windForceMean                
                windForceMean = plugin.find('windForceMean')
                log.info("      windForceMean: " + windForceMean.text)

                #windGustDirection
                windGustDirection = plugin.find('windGustDirection')
                log.info("      windGustDirection: " + windGustDirection.text)
                #fuzzed_windGustDirection = "0 0 0"
                #windGustDirection.text = fuzzed_windGustDirection
                #log.info("      *windGustDirection: " + windGustDirection.text)

                #windGustDuration
                windGustDuration = plugin.find('windGustDuration')
                log.info("      windGustDuration: " + windGustDuration.text)

                #windGustStart
                windGustStart = plugin.find('windGustStart')
                log.info("      windGustStart: " + windGustStart.text)

                #windGustForceMean
                windGustForceMean = plugin.find('windGustForceMean')
                log.info("      windGustForceMean: " + windGustForceMean.text)
                #fuzzed_windGustForceMean = str(vlist[0])
                #windGustForceMean.text = fuzzed_windGustForceMean
                #log.info("      *windGustForceMean: " + windGustForceMean.text)

                #xyzOffset
                xyzOffset = plugin.find('xyzOffset')
                log.info("      xyzOffset: " + xyzOffset.text)

 

        #TODO: randomly select models in the given ranges

        #pose = model.find('pose')           #model pose
        #if(pose != None):
        #    log.info("  pose: " + pose.text)
        #    fuzzed_pose = mutate_pose(pose.text)
        #    pose.text = fuzzed_pose
        #    log.info("  *fpose: " + pose.text)
 

        #wind
        wind = world.find('wind')
        if(wind != None):
            log.info("  wind")

            #linear_velocity
            linear_velocity = wind.find('linear_velocity')
            if(linear_velocity != None):
                log.info("    linear_velocity %s" % (linear_velocity.text))
                # 1 (m/s) = 2.237 (mph)
                #fuzzed_linear_velocity = mutate_3f(linear_velocity.text, [10,10,10,10,0,1], 2)
                #linear_velocity.text = fuzzed_linear_velocity
                #log.info("    *flinear_velocity %s" % (linear_velocity.text))
                input_world = input_world + ['linear_velocity', linear_velocity.text]

        #gravity
        gravity = world.find('gravity')
        if(gravity != None):
            log.info("  gravity: %s" % (gravity.text))

        #magnetic_field
        magnetic_field = world.find('magnetic_field')
        if(magnetic_field != None):
            log.info("  magnetic_field %s" % (magnetic_field.text))
            #fuzzed_magnetic_field = mutate_3f(magnetic_field.text, [6e-06, 6e-06, 2.3e-05, 2.3e-05, -4.2e-05, -4.2e-05], 7)
            #magnetic_field.text = fuzzed_magnetic_field
            #log.info("  *fmagnetic_field %s" % (magnetic_field.text))
            input_world = input_world + ['magnetic_field', magnetic_field.text]

        #atmosphere
        atmosphere = world.find('atmosphere')
        if(atmosphere != None):
            log.info('  atmosphere: %s' % (atmosphere.attrib))

            #temparature
            temperature = atmosphere.find('temperature') 
            if(temperature != None):
                log.info('    temperature: %s' % (temperature.text))
                #fuzzed_temperature = mutate_f(temperature.text, [298.15, 298.15], 2)
                #temperature.text = str(fuzzed_temperature)
                #log.info('    *ftemperature: %s' % (temperature.text))
                input_world = input_world + ['temperature', temperature.text]

            #pressure
            pressure = atmosphere.find('pressure') 
            if(pressure != None):
                log.info('    pressure: %s' % (pressure.text))
                #fuzzed_pressure = mutate_f(pressure.text, [101325, 101326], 2)
                #pressure.text = str(fuzzed_pressure)
                #log.info('    *fpressure: %s' % (pressure.text))
                input_world = input_world + ['pressure', pressure.text]

            #temperature_gradient
            temperature_gradient = atmosphere.find('temperature_gradient') 
            if(temperature != None):
                log.info('    temperature_gradient: %s' % (temperature_gradient.text))
                #fuzzed_temperature_gradient = mutate_f(temperature_gradient.text, [-0.0065, -0.0066], 4)
                #temperature_gradient.text = str(fuzzed_temperature_gradient)
                #log.info('    *ftemperature_gradient: %s' % (temperature_gradient.text))
                input_world = input_world + ['temperature_gradient', temperature_gradient.text]

        #scene
        scene = world.find('scene')
        if(scene != None):
            log.info('  scene')
            # TODO visual effects (if required)

    log.cinfo(">> Saved: Fuzz (World): %s" % (filename))
    #log.write(et.tostring(tree.getroot(), encoding='utf8', method='xml'))
    tree.write(filename)
    return input_world
   

def mutate_model(filename, Vlist, V, Vmap):
    """
    perturb model properties and save the mode sdf file 
    filename: model sdf path
    Vlist: input list
    Vmap: input bitmask
    """

    log.cinfo("=== Reading model file: " + filename)
    tree = et.parse(filename)
    root = tree.getroot()
    #print("root: %s %s" % (root.tag, root.attrib))    #sdf version
    input_model = []

    xmlstr = minidom.parseString(et.tostring(root)).toprettyxml(indent=" ", newl='')
    #print(xmlstr.encode('utf-8'))

    ## iterate
    # tags = [elem.tag for elem in root.iter()]

    ## find target
    #for model in root.findall("./world/model/pose"):
    #    print(model)

    #model_name = 'tunnel1'
    #for model in root.findall("./world/model[@name='" + model_name + "']"):    #world file
    #for model in root.findall("./model[@name='" + model_name + "']"):          #model file
    
    for model in root.findall("model"):     #for model in root.iter('model'):
        log.info(" model: %s" % (model.attrib))
        ######################################### example
        #<model>
            #<static>
            #<pose>*
            #<enable_wind>
            #<link>*
              #<gravity>
              #<enable_wind>
              #<inertial>
              #<collision>*
                  #<geometry>*
                  #<pose>*
                  #<surface>
              #<visual>*
                  #<pose>*
                  #<geometry>*
                  #<material>*
                  #<ambient>*
              #<static> : immovable
              #<enable_wind>
              #<pose>
            #</link>
         #</model>
        #pose = model.find('pose')           #model pose
        #if(pose != None):
        #    log.info("  pose: " + pose.text)
        #    fuzzed_pose = mutate_pose(pose.text)
        #    pose.text = fuzzed_pose
        #    log.info("  *fpose: " + pose.text)
        #########################################

        #static 
        static = model.find('static')       #optional
        if(static != None):
            log.info("  static: " + static.text)
            #fuzzed_static = random.randint(0,1)
            #static.text = str(fuzzed_static)
            #log.info("  *fstatic: " + static.text)
            input_model = input_model + ['static', static.text]

        #enable_wind
        enable_wind = model.find('enable_wind')       #optional
        if(enable_wind != None):
            log.info("  enable_wind: " + enable_wind.text)
            #fuzzed_enable_wind = random.randint(0,1)
            #enable_wind.text = str(fuzzed_enable_wind)
            #log.info("  *fenable_wind: " + enable_wind.text)
            input_model = input_model + ['enable_wind', enable_wind.text]

        #link
        links = model.findall('link')       
        for link in links:
            if(link != None):
                log.info("  link: %s" % (link.attrib))

                #inertial
                inertial = link.find('inertial')   
                if(inertial != None):
                    log.info("    inertial")

                    #mass
                    mass = inertial.find('mass')
                    log.info("      mass:" + mass.text)
                    if(Vmap & 1<<setting.MODEL_MASS):
                        mass.text = str(Vlist[setting.MODEL_MASS][0])
                        log.info("      *mass:" + mass.text)
                        input_model = input_model + ['mass', mass.text]

                    #inertia
                    inertia = inertial.find('inertia')
                    log.info("      inertia")
                    ixx = inertia.find('ixx')
                    iyy = inertia.find('iyy')
                    izz = inertia.find('izz')
                    log.info("        ixx:" + ixx.text)
                    log.info("        iyy:" + iyy.text)
                    log.info("        izz:" + izz.text)
                    if(Vmap & 1<<setting.MODEL_INERTIA):
                        ixx.text = str(Vlist[setting.MODEL_INERTIA][0])
                        iyy.text = str(Vlist[setting.MODEL_INERTIA][1])
                        izz.text = str(Vlist[setting.MODEL_INERTIA][2])
                        log.info("        *ixx:" + ixx.text)
                        log.info("        *iyy:" + iyy.text)
                        log.info("        *izz:" + izz.text)
                        input_model = input_model + ['ixx', ixx.text, 'iyy', iyy.text, 'izz', izz.text]

                #collision    
                collision = link.find('collision')
                if(collision != None):
                    log.info("    collision: %s" % (collision.attrib))
                    
                    #geometry
                    geometry = collision.find('geometry')
                    if(geometry != None):
                        log.info("      geometry")

                    # TODO add more models
                    #box
                    box = geometry.find('box')  
                    if(box != None):
                        size = box.find('size')
                        log.info("        size: %s" % (size.text))
                        #fuzzed_size = mutate_3f(size.text, [3.4,3.4, 1.9,1.9, 9,9],2)
                        #size.text = str(fuzzed_size)
                        #log.info("        *fsize: %s" % (size.text))
                        input_model = input_model + ['size', size.text]


                    #pose
                    pose = collision.find('pose')
                    if(pose != None):
                        log.info("      pose: " + pose.text)

                    #surface
                    surface = collision.find('surface')
                    if(surface != None):
                        log.info("      surface")

                        #friction
                        friction = collision.find('friction')
                        if(friction != None):
                            log.info("        friction")

                        #bounce
                        bounce = collision.find('bound')
                        if(bounce != None):
                            log.info("        bound")

                        #contact
                        contact = surface.find('contact')
                        if(contact != None):
                            log.info("        contact")

                #visual
                visual = link.find('visual')
                if(visual != None):
                    log.info("    visual: %s" % (visual.attrib))
                    
                    #geometry
                    geometry = visual.find('geometry')
                    if(geometry != None):
                        log.info("      geometry")

                    #box     
                    box = geometry.find('box')
                    if(box != None):

                        #size
                        size = box.find('size')
                        log.info("        size: %s" % (size.text))
                        #size.text = str(fuzzed_size)
                        #log.info("        *fsize: %s" % (size.text))

                    #pose (collision)
                    pose = collision.find('pose')
                    if(pose != None):
                        log.info("      pose: " + pose.text)

                #pose (link)
                pose = link.find('pose')
                if(pose != None):
                    log.info("    pose: " + pose.text)

                

    # update values
    #model.attrib['name'] = model.attrib['name'] + "xx"

    log.cinfo(">> Saved: Fuzz (Model): %s" % (filename))
    #log.write(et.tostring(tree.getroot(), encoding='utf8', method='xml'))
    tree.write(filename)
    return input_model


def main():
    # mutate('iris_ardupilot.world')
    home = expanduser("~")

    pos_range = [0, 45, 0, 0, 0, 5]   #NEU
    att_range = [-3.14, 3.14, -3.14, 3.14, -3.14, 3.14]
    #config(pos_range, ALPHA)

    #world_file = home + '/ardupilot_gazebo/worlds/iris_ardupilot_tunnel.world'
    #model_file = home + '/ardupilot_gazebo/models/tunnel1/model.sdf'
    world_file = home + '/ardupilot_gazebo/worlds/copter.world'
    model_file = home + '/ardupilot_gazebo/models/fs_gray_wall/model.sdf'

    #mutate_param()
    mutate_model(model_file, [0, 1])
    mutate_world(0.1,world_file)

if __name__ == '__main__':
    main()

