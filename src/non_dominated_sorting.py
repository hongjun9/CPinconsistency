import setting

def non_dominated_sorting(individuals, M, V):
    #non-dominatd pareto sorting

    print "Non_dominated_sorting " + str(len(individuals))
    for i in range(len(individuals)):
        print i, individuals[i]

    front = 0           # current pareto front 
    pareto = [[]]       # list of index of pareto group
    N = len(individuals)
    dominated_num = [None]*N    # []: number of individuals that dominate this individual   n
    dominates = [None]*N        # [][]: individuals which this individual dominate    S
    for i in range(N):    #N: #population     i: this individual
        dominated_num[i] = 0      
        dominates[i] = []         
        for j in range(N):
            count_dominates = 0       
            count_equal = 0
            count_dominatedby = 0
            for k in range(M):     #M: #objects
                #print individuals[i][setting.INDEX_OUTPUT], k, M   ##check input/output number
                if individuals[i][setting.INDEX_OUTPUT][k] < individuals[j][setting.INDEX_OUTPUT][k]:     # this i dominates j
                    count_dominates = count_dominates + 1
                elif individuals[i][setting.INDEX_OUTPUT][k] == individuals[j][setting.INDEX_OUTPUT][k]:  # equal
                    count_equal = count_equal + 1
                else:                                               # this i is dominated by j
                    count_dominatedby = count_dominatedby + 1
            if count_dominatedby == 0 and count_equal != M:
                dominates[i] += [j]
            elif count_dominates == 0 and count_equal != M:
                dominated_num[i] = dominated_num[i] + 1;
                    
        if dominated_num[i] == 0:
            individuals[i] += [front]
            pareto[front] += [i]
    #print "dominated_num:", dominated_num, "dominates:", dominates
    #print "pareto front: ", pareto[front]
    
    # find subsequent fronts
    while len(pareto[front]) != 0:
        Q = []
        for i in range(len(pareto[front])):
            p = pareto[front][i]
            if len(dominates[p]) != 0:
                for j in range(len(dominates[p])):
                    q = dominates[p][j]     # p dominates q
                    dominated_num[q] = dominated_num[q] - 1
                    if dominated_num[q] == 0:
                        individuals[q] += [front + 1]
                        Q += [dominates[p][j]]
        front = front + 1
        pareto += [Q]     #set of individuals for each pareto front pareto[1...front]
    
    individuals = sorted(individuals, key=lambda individuals: individuals[setting.INDEX_RANK])  # sort by rank
    pareto = []*front     # re-assign after sorting 
    for i in range(front):
        current_pareto = []
        for j in range(N):
            if i == individuals[j][setting.INDEX_RANK]:
                current_pareto += [j]
        pareto += [current_pareto]

    print "after non-domniated sorting"
    for i in range(len(individuals)):
        print individuals[i]
    print "pareto: ", pareto
    
    # (opt1) cpi-score added
    if(setting.SCORE_OPTION != 2):
        for i in range(front):
            cpi_score = 0 
            pareto_members = []     # current pareto front members
            for j in range(len(pareto[i])):
                index = pareto[i][j] 
                pareto_members += [individuals[index]]  
            #for x in range(len(pareto_members)):
            #    print pareto_members[x]
        
            for k in range(M):      # for each objective
                sorted_pareto_members = sorted(pareto_members, key=lambda pareto_members: pareto_members[setting.INDEX_OUTPUT][k])  # sort by objective
                #TODO
                #for now, sort with the last objective (phy_dev)
                #f_min = sorted_pareto_members[0][setting.INDEX_OUTPUT][k]          # [row][output][output_type]
                #f_max = sorted_pareto_members[len(sorted_pareto_members)-1][setting.INDEX_OUTPUT][k]
        
            #    print "sorted with objective: ", k, "(front):", i
            #    for x in range(len(sorted_pareto_members)):
            #        print sorted_pareto_members[x]
            #    print "max/min:", f_max, f_min
        
            for l in range(len(sorted_pareto_members)):
                cpi_score = len(sorted_pareto_members)-l
                sorted_pareto_members[l] += [cpi_score]
            
            #print "ci_score_added"
            #for x in range(len(sorted_pareto_members)):
            #    print sorted_pareto_members[x]

    ### (opt2) crowding distance
    if(setting.SCORE_OPTION == 2):
        for i in range(front):      # for total length of pareto front
            pareto_members = []     # current pareto front members

            for j in range(len(pareto[i])):
                index = pareto[i][j]
                pareto_members += [individuals[index]]
            for j in range(len(pareto_members)):
                pareto_members[j] += [0.0]      # distance

            for k in range(M):
                sorted_pareto_members = sorted(pareto_members, key=lambda pareto_members: pareto_members[setting.INDEX_OUTPUT][k])
                
                f_min = sorted_pareto_members[0][setting.INDEX_OUTPUT][k]
                f_max = sorted_pareto_members[len(sorted_pareto_members)-1][setting.INDEX_OUTPUT][k]
            
                sorted_pareto_members[0][setting.INDEX_CPIRANK] = float('inf')
                sorted_pareto_members[len(sorted_pareto_members)-1][setting.INDEX_CPIRANK] = float('inf')

                if len(sorted_pareto_members) >= 3:
                    for l in range(1, len(sorted_pareto_members)-2):
                        next = sorted_pareto_members[l+1][setting.INDEX_OUTPUT][k]
                        previous = sorted_pareto_members[l-1][setting.INDEX_OUTPUT][k]
                        if (f_max - f_min) == 0:
                            sorted_pareto_members[l][setting.INDEX_CPIRANK] = float('inf')
                        else:
                            sorted_pareto_members[l][setting.INDEX_CPIRANK] += round((next - previous) / (f_max-f_min), 4)

        print "after non-domniated sorting (crowdistance)"
        for i in range(len(individuals)):
            print individuals[i]
 

    return individuals



