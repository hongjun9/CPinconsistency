import setting
import random
from evaluate import *
from selections import *
from setting import *
import logger as log
from non_dominated_sorting import *

def evolution(test_id):

    ##========================================
    # initialize_population(N, M, V, Vrange)
    # random individual
    init_individuals = [None] * setting.N
    for i in range(setting.N):
        input_vector = []
        #for j in range(setting.V):  # for V inputs
        #    ##$$
        #    random_input = round(random.uniform(setting.Vrange[j][0], setting.Vrange[j][1]), 4)
        #    input_vector.append(random_input)
        for j in reversed(range(setting.MAX_INPUT)): 
            if(setting.Vmap & 1<<j):
                inputs = setting.Vrange[j]
                for k in range(len(inputs)/2):
                    random_input = round(random.uniform(inputs[k], inputs[k+1]))
                    input_vector.append(random_input)
                    k = k+2
            
        init_individuals[i] = [0, input_vector]  #code, [input_vector]
    gen_id = str(test_id) + "_g0"

    # evaluate inits ----------------------
    init_individuals = evaluate(gen_id, init_individuals)   #given inputs
    init_individuals = non_dominated_sorting(init_individuals, setting.M, setting.V)
    print "@@init individuals", setting.N, gen_id
     
    for i in range(setting.N):
       log.info(str(init_individuals[i]))

    # end init

    ##=========================================
    # start evolution
    #
    individuals = init_individuals
    for gen in range(0,setting.GEN):
        
        log.info("#########################################################################################")
        log.info("############################# [#%3d / %3d] Evolution starts #############################" % (gen+1, setting.GEN))
        log.info("#########################################################################################")
        gen_id = str(test_id) + "_g" + str(gen+1)

        #output generations to logs
        print(gen_id + " @@starting individuals " + str(len(individuals)))
        print "[",str(gen+1),"]", "@@------starting_individuals", len(individuals)
        for i in range(len(individuals)):
            print individuals[i]

        #log.info("[INDIVIDUALS] " + str(len(individuals)) + " " + str(setting.V) + " " + str(setting.M) + " " + str(setting.M_P))
        #for i in range(len(individuals)):
        #    line = ''
        #    print individuals[i]
        #    line += str(individuals[i][setting.INDEX_CODE]) + ','                   #code
        #    for j in range(setting.V):
        #        line += str(individuals[i][setting.INDEX_INPUT][j]) + ','           #inputs
        #    for k in range(setting.M+setting.M_P):
        #        line += str(individuals[i][setting.INDEX_OUTPUT][k]) + ','          #outputs
        #    line += str(individuals[i][setting.INDEX_RANK]) + ',' + str(individuals[i][setting.INDEX_CPIRANK])  #pareto, cpi
        #    log.info(line)
        
        #log.info(str(individuals[i][j][k]))
        #print(Style.RESET_ALL)

        ##--------------------------------------------------------
        ### parents selection (binary tournament selection) - half from total
        # parents are selectd for reproduction to generate offspring
        pool = int(round(setting.N/2.0))  # size of mating pool (N/2)
        tour = 2                  # tournament size (selection pressure)

        #If the tournament size is larger, weak individuals have a smaller chance to be selected,  
        #because, if a weak individual is selected to be in a tournament, there is a higher probability 
        #that a stronger individual is also in that tournament.
        if setting.SCORE_OPTION == 3:   # random selection
            parent_individuals = random_selection(individuals, pool)
        else:                           # tournament selection
            parent_individuals = tournament_selection(individuals, pool, tour)

        print "[",str(gen+1),"]", "@@------parent_individuals", len(parent_individuals)
        for i in range(len(parent_individuals)):
            print parent_individuals[i]

        ##--------------------------------------------------------
        ## genetic operator
        # crossover and mutation from parents (Simulated Binary Crossover (SBX) and Polynomial mutation)
        # evaluate offsprings (SIMULATION)
        print "[",str(gen+1),"]", "@@-------------- genetic operator  ---------------"
        candidate_individuals = genetic_operator(gen_id, individuals, parent_individuals, pool)

        print "[",str(gen+1),"]", "@@------candidate_individuals = individual + offspring", len(candidate_individuals)
        for i in range(len(candidate_individuals)):
            print candidate_individuals[i]

        candidate_individuals = non_dominated_sorting(candidate_individuals, setting.M, setting.V)
        print "[",str(gen+1),"]", "@@------after non_dominated_sorting: candidate_individuals", len(candidate_individuals)
        for i in range(len(candidate_individuals)):
            print candidate_individuals[i]


        ##--------------------------------------------------------
        # select top N from candidates (individual + offspring)
        new_individuals = top_n_selection(candidate_individuals, setting.N)
        #new_individuals = tournament_selection(candidate_individuals, N, tour)

        ## opt4 : random population
        if setting.SCORE_OPTION == 4:   #random individuals
            new_individuals = random_pop_generation(setting.N)

        ###--------------------------------------------
        # plot
        #if setting.FIGON:
        #    plot_scatter(new_individuals, "Generation " + str(gen+1) + " new_individuals") 
        ##-----------------------------------------------

        print "[GEN #",str(gen+1),"]", "@@------new_individuals", len(new_individuals)
        for i in range(len(new_individuals)):
            print new_individuals[i]

        individuals = new_individuals

        #----------------------------
        # save output
        output_file_name = "genout_" + test_id + ".log"
        output_file = setting.CPII_TESTLOG + "/" + output_file_name    
        outf = open(output_file, "a+")       # log for the resulting generation 
        outf.write("GENERATION " + str(gen_id) + "\n")
        for j in range(setting.N):
            print individuals[j]
            outf.write(str(individuals[j])+"\n")

        cprint("[GEN #"+str(gen+1)+"] DONE" + " #POP #INPUTS #C_COST #P_COST [GEN#]", "yellow")
        log.info("[INDIVIDUALS] " + str(len(individuals)) + " " + str(setting.V) + " " + str(setting.M) + " " + str(setting.M_P) + "  [" + str(gen+1) + "]")
        for i in range(len(individuals)):
            line = ''
            #print individuals[i]
            line += str(individuals[i][setting.INDEX_CODE]) + ', '                   #code
            for j in range(setting.V):
                line += str(individuals[i][setting.INDEX_INPUT][j]) + ', '           #inputs
            for k in range(setting.M+setting.M_P):
                line += str(individuals[i][setting.INDEX_OUTPUT][k]) + ', '          #outputs
            line += str(individuals[i][setting.INDEX_RANK]) + ', ' + str(individuals[i][setting.INDEX_CPIRANK])  #pareto, cpi
            log.info(line)

        #
        #end one evolution
        #
    
    return True


def genetic_operator(gen_id, individuals, parent_individuals, pool):
    # crossover and mutation
    # Simulated Binary Crossover (SBX) and Polynomial mutation
    # crossover probability pc = 0.9
    # mutation probability pm = 1/N
    # distribution index for crossover and mutation as mu = 20 and mum = 20, resprectively.
    mu = 20;
    mum = 20;
    pr = 0.9

    print "Individuals:"
    for i in range(len(individuals)):
        print individuals[i]
    print "Parents:"
    for i in range(len(parent_individuals)):
        print parent_individuals[i]
    offspring = []
    print "genetic_operator pool:", pool

    #make Vrange
    Vrange = []
    for k in reversed(range(setting.MAX_INPUT)): 
        if(setting.Vmap & 1 << k):
            for j in range(0,len(setting.Vrange[k]),2):
                Vrange.append(setting.Vrange[k][j:j+2])
    print "Vrange:", Vrange
    ###
    
    for i in range(pool):
        if random.random() < pr:       # crossover
            child1 = [None]*setting.V
            child2 = [None]*setting.V
            parent1_i = random.randint(0, pool-1)
            parent2_i = random.randint(0, pool-1)
            while parent1_i == parent2_i:
                parent2_i = random.randint(0, pool-1)
            parent1 = parent_individuals[parent1_i]
            parent2 = parent_individuals[parent2_i]
            #print "parent1: ", parent1_i, "/", pool-1, parent1
            #print "parent2: ", parent2_i, "/", pool-1, parent2

            u = [None] * setting.V
            bq = [None] * setting.V
            for j in range(setting.V):       # for each input
                if(setting.Vmap & 1 << k):
                    # SBX
                    u[j] = random.random()
                    if u[j] <= 0.5:
                        bq[j] = (2*u[j])**(1.0/(mu+1)) 
                    else:
                        bq[j] = (1.0/(2*(1-u[j])))**(1.0/(mu+1))

                    # generate child for each input
                    child1[j] = 0.5 * ( ((1+bq[j])*parent1[setting.INDEX_INPUT][j]) + (1-bq[j]) * parent2[setting.INDEX_INPUT][j] )
                    child2[j] = 0.5 * ( ((1-bq[j])*parent1[setting.INDEX_INPUT][j]) + (1+bq[j]) * parent2[setting.INDEX_INPUT][j] )
                    child1[j] = round(min(max(child1[j], Vrange[k][0]), Vrange[k][1]), 4)
                    child2[j] = round(min(max(child2[j], Vrange[k][0]), Vrange[k][1]), 4)

            offspring.append([0,child1])
            offspring.append([0,child2])
            print "child1,2:", child1, child2

        else:                           # mutation
            parent3 = random.randint(0, pool-1)
            child3 = list(parent_individuals[parent3][setting.INDEX_INPUT])
            r = [None] * setting.V
            delta = [None] * setting.V
            for j in range(setting.V):
                r[j] = random.random()
                if r[j] < 0.5:
                    delta[j] = (2.0*r[j])**(1.0/(mum+1)) - 1.0
                else:
                    delta[j] = 1.0 - (2.0*(1-r[j]))**(1.0/(mum+1.0))

                child3[j] = round(child3[j] + delta[j] ,4);
                child3[j] = min(max(child3[j], Vrange[j][0]), Vrange[j][1])

            offspring.append([0,child3])
            print "child3:", child3

    print "@@----- offspring", len(offspring)
    for i in range(len(offspring)):
        print offspring[i]
    print "--------------------------------"

    ##evaluate offspring
    offspring_individuals = evaluate(gen_id, offspring)
    print "@@after offspring_individual evaluated", len(offspring_individuals)
    for i in range(len(offspring_individuals)):
        print offspring_individuals[i]

    ## select new individuals (highest pareto ranking, and then cpi-cost) : 0 is the highest
    candidate_individuals = []
    candidate_individuals += [row[setting.INDEX_CODE:setting.INDEX_OUTPUT+1] for row in individuals] + offspring       # only code:inputs:output

    return candidate_individuals


def random_population(test_id, G):
    '''
    random generation (vs. evolutionary)
    '''

    for g in range(G):

        gen_id = str(test_id) + "_" + str(g)

        individuals = [None] * setting.N
        for i in range(setting.N):
            input_vector = []
            for j in range(setting.V):  # for V inputs
                ##$$
                random_input = round(random.uniform(setting.Vrange[j][0], setting.Vrange[j][1]), 4)
                input_vector.append(random_input)
            individuals[i] = [0, input_vector]  #code, [input_vector]
        
        #gen_id = str(test_id) + "_g0"
        individuals = evaluate(gen_id, individuals)   #given inputs
        individuals = non_dominated_sorting(individuals, setting.M, setting.V)
    
        # save output
        output_file_name = "genout_" + test_id + ".log"
        output_file = setting.CPII_TESTLOG + "/" + output_file_name    
        outf = open(output_file, "a+")       # log for the resulting generation 
        outf.write("GENERATION " + str(gen_id) + "\n")
        for j in range(setting.N):
            print individuals[j]
            outf.write(str(individuals[j])+"\n")

        log.info("[INDIVIDUALS] " + str(len(individuals)) + " " + str(setting.V) + " " + str(setting.M) + " " + str(setting.M_P) + "  [" + str(gen+1) + "]")
        for i in range(len(individuals)):
            line = ''
            #print individuals[i]
            line += str(individuals[i][setting.INDEX_CODE]) + ', '                   #code
            for j in range(setting.V):
                line += str(individuals[i][setting.INDEX_INPUT][j]) + ', '           #inputs
            for k in range(setting.M+setting.M_P):
                line += str(individuals[i][setting.INDEX_OUTPUT][k]) + ', '          #outputs
            line += str(individuals[i][setting.INDEX_RANK]) + ', ' + str(individuals[i][setting.INDEX_CPIRANK])  #pareto, cpi
            log.info(line)


def random_pop_generation(N):
    '''
        random individuals
    '''
    individuals = [None] * N
    for i in range(N):
        input_vector = []
        for j in range(V):
            input = round(random.uniform(setting.Vrange[j][0], setting.Vrange[j][1]), 4)
            input_vector.append(input)
        individuals[i] = [input_vector]

    individuals = evaluate('0', individuals)
    return individuals


